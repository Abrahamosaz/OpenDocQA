"""
Embedding generation and storage utilities.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings."""
    
    def __init__(self, embedding_model: Optional[Embeddings] = None):
        """Initialize the embedding service."""
        self.embedding_model = embedding_model or self._get_default_embeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _get_default_embeddings(self) -> Embeddings:
        """Get default OpenAI embeddings."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-3-small"
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.embedding_model.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.embedding_model.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks for processing."""
        try:
            # Create a text splitter with custom parameters
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            chunks = splitter.split_text(text)
            logger.info(f"Text split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to chunk text: {e}")
            raise
    
    def process_document(self, content: str, filename: str) -> List[Dict[str, Any]]:
        """Process a document: chunk, embed, and prepare for storage."""
        try:
            # Split document into chunks
            chunks = self.chunk_text(content)
            
            # Generate embeddings for each chunk
            embeddings = self.generate_embeddings_batch(chunks)
            
            # Prepare document data
            processed_chunks = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_data = {
                    "content": chunk,
                    "embedding": embedding,
                    "metadata": {
                        "filename": filename,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk)
                    }
                }
                processed_chunks.append(chunk_data)
            
            logger.info(f"Processed {len(processed_chunks)} chunks for {filename}")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Failed to process document {filename}: {e}")
            raise
    
    def get_similar_chunks(
        self, 
        query: str, 
        all_chunks: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find most similar chunks to a query."""
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query)
            
            # Calculate similarities (cosine similarity)
            similarities = []
            for chunk in all_chunks:
                similarity = self._cosine_similarity(query_embedding, chunk["embedding"])
                similarities.append((chunk, similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [chunk for chunk, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Failed to find similar chunks: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

# Global embedding service instance
embedding_service = EmbeddingService()

def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    return embedding_service
