"""
RAG (Retrieval-Augmented Generation) pipeline implementation using LangChain.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA, load_summarize_chain
# Removed unused imports that are not available in current LangChain version
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

from .db import get_db, get_similar_documents, store_document, get_all_documents
from .embeddings import get_embedding_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    """RAG pipeline for question answering and document summarization."""
    
    def __init__(self):
        """Initialize the RAG pipeline."""
        self.llm = self._get_llm()
        self.embeddings = self._get_embeddings()
        self.embedding_service = get_embedding_service()
        
    def _get_llm(self) -> ChatOpenAI:
        """Get the language model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.1
        )
    
    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get the embeddings model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )
    
    def process_and_store_document(self, content: str, filename: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Process a document and store it in the database."""
        try:
            db = get_db()
            
            # Process document into chunks
            processed_chunks = self.embedding_service.process_document(content, filename)
            
            # Store each chunk in the database
            for chunk_data in processed_chunks:
                chunk_metadata = chunk_data["metadata"]
                if metadata:
                    chunk_metadata.update(metadata)
                
                store_document(
                    db=db,
                    filename=chunk_data["metadata"]["filename"],
                    content=chunk_data["content"],
                    embedding=chunk_data["embedding"],
                    metadata=chunk_metadata
                )
            
            db.close()
            logger.info(f"Successfully processed and stored document: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process and store document {filename}: {e}")
            return False
    
    def answer_question(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Answer a question using RAG pipeline."""
        try:
            db = get_db()
            
            # Generate embedding for the question
            query_embedding = self.embedding_service.generate_embedding(question)
            
            # Find similar documents
            similar_docs = get_similar_documents(
                db=db,
                query_embedding=query_embedding,
                limit=top_k
            )
            
            if not similar_docs:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context from similar documents
            context = "\n\n".join([doc["content"] for doc in similar_docs])
            
            # Create prompt for the LLM
            prompt = f"""
            Based on the following context, please answer the question. If the answer cannot be found in the context, say "I don't have enough information to answer this question."

            Context:
            {context}

            Question: {question}

            Answer:
            """
            
            # Get answer from LLM
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Calculate confidence based on similarity scores
            avg_similarity = sum(doc["similarity"] for doc in similar_docs) / len(similar_docs)
            confidence = min(avg_similarity, 1.0)
            
            db.close()
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "filename": doc["filename"],
                        "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                        "similarity": doc["similarity"]
                    }
                    for doc in similar_docs
                ],
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "answer": "I encountered an error while processing your question.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def summarize_document(self, filename: str) -> Dict[str, Any]:
        """Summarize a specific document."""
        try:
            db = get_db()
            
            # Get all chunks for the document
            from .db import Document
            chunks = db.query(Document).filter(Document.filename == filename).all()
            
            if not chunks:
                return {
                    "summary": f"No document found with filename: {filename}",
                    "success": False
                }
            
            # Combine all chunks
            full_content = "\n\n".join([chunk.content for chunk in chunks])
            
            # Create summarization chain
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200
            )
            
            # Split the document into smaller chunks for summarization
            docs = text_splitter.create_documents([full_content])
            
            # Use map-reduce summarization
            chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                return_intermediate_steps=True
            )
            
            result = chain({"input_documents": docs})
            
            db.close()
            
            return {
                "summary": result["output_text"],
                "success": True,
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to summarize document {filename}: {e}")
            return {
                "summary": f"Failed to summarize document: {str(e)}",
                "success": False
            }
    
    def get_document_list(self) -> List[Dict[str, Any]]:
        """Get list of all documents in the database."""
        try:
            db = get_db()
            documents = get_all_documents(db)
            db.close()
            
            # Group by filename to show unique documents
            unique_docs = {}
            for doc in documents:
                filename = doc["filename"]
                if filename not in unique_docs:
                    unique_docs[filename] = {
                        "filename": filename,
                        "chunks": 0,
                        "created_at": doc["created_at"],
                        "metadata": doc["metadata"]
                    }
                unique_docs[filename]["chunks"] += 1
            
            return list(unique_docs.values())
            
        except Exception as e:
            logger.error(f"Failed to get document list: {e}")
            return []
    
    def delete_document(self, filename: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            db = get_db()
            
            # Get all chunks for the document
            from .db import Document
            chunks = db.query(Document).filter(Document.filename == filename).all()
            
            # Delete all chunks
            for chunk in chunks:
                db.delete(chunk)
            
            db.commit()
            db.close()
            
            logger.info(f"Deleted document: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {filename}: {e}")
            return False

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()

def get_rag_pipeline() -> RAGPipeline:
    """Get the global RAG pipeline instance."""
    return rag_pipeline
