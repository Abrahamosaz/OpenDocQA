"""
Database connection and setup for PostgreSQL with pgvector extension.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import create_engine, text, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/rag_db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    """Document model for storing text and embeddings."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSONB, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    embedding = Column(Vector(1536))  # OpenAI embeddings dimension
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class ChatSession(Base):
    """Chat session model for storing chat sessions."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Chat message model for storing individual messages."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(JSONB, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let the caller handle it

def init_database():
    """Initialize database with required extensions and tables."""
    try:
        # Enable vector extension FIRST
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        
        # Create all tables AFTER enabling the extension
        Base.metadata.create_all(bind=engine)
            
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def test_connection() -> bool:
    """Test database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_similar_documents(
    db: Session, 
    query_embedding: List[float], 
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Find similar documents using vector similarity search."""
    try:
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        # SQL query for cosine similarity search
        query = text("""
            SELECT id, filename, content, doc_metadata, 
                   1 - (embedding <=> :embedding) as similarity
            FROM documents 
            WHERE 1 - (embedding <=> :embedding) > :threshold
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """)
        
        result = db.execute(query, {
            "embedding": embedding_str,
            "threshold": similarity_threshold,
            "limit": limit
        })
        
        documents = []
        for row in result:
            documents.append({
                "id": row.id,
                "filename": row.filename,
                "content": row.content,
                "metadata": row.doc_metadata,
                "similarity": float(row.similarity)
            })
        
        return documents
    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        return []

def store_document(
    db: Session,
    filename: str,
    content: str,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """Store a document with its embedding."""
    try:
        if metadata is None:
            metadata = {}
            
        document = Document(
            filename=filename,
            content=content,
            embedding=embedding,
            doc_metadata=metadata
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        logger.info(f"Document stored successfully: {filename}")
        return document.id
    except Exception as e:
        logger.error(f"Failed to store document: {e}")
        db.rollback()
        return None

def get_all_documents(db: Session) -> List[Dict[str, Any]]:
    """Get all documents from the database."""
    try:
        documents = db.query(Document).all()
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "content": doc.content,
                "metadata": doc.doc_metadata,
                "created_at": doc.created_at,
                "updated_at": doc.updated_at
            }
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        return []

def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document by ID."""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            db.delete(document)
            db.commit()
            logger.info(f"Document deleted: {document_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        db.rollback()
        return False

# Chat Session Functions

def create_chat_session(db: Session, name: str) -> Optional[int]:
    """Create a new chat session."""
    try:
        session = ChatSession(name=name)
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"Chat session created: {name}")
        return session.id
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        db.rollback()
        return None

def get_chat_sessions(db: Session) -> List[Dict[str, Any]]:
    """Get all chat sessions."""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
        return [
            {
                "id": session.id,
                "name": session.name,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages)
            }
            for session in sessions
        ]
    except Exception as e:
        logger.error(f"Failed to retrieve chat sessions: {e}")
        return []

def get_chat_session(db: Session, session_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific chat session with messages."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return None
            
        return {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.message_metadata,  # Updated to use message_metadata
                    "created_at": msg.created_at
                }
                for msg in session.messages
            ]
        }
    except Exception as e:
        logger.error(f"Failed to retrieve chat session: {e}")
        return None

def add_message_to_session(
    db: Session, 
    session_id: int, 
    role: str, 
    content: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """Add a message to a chat session."""
    try:
        if metadata is None:
            metadata = {}
            
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            message_metadata=metadata  # Updated to use message_metadata
        )
        
        db.add(message)
        
        # Update session's updated_at timestamp
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(message)
        
        logger.info(f"Message added to session {session_id}")
        return message.id
    except Exception as e:
        logger.error(f"Failed to add message to session: {e}")
        db.rollback()
        return None

def delete_chat_session(db: Session, session_id: int) -> bool:
    """Delete a chat session and all its messages."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            logger.info(f"Chat session deleted: {session_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete chat session: {e}")
        db.rollback()
        return False

def update_chat_session_name(db: Session, session_id: int, new_name: str) -> bool:
    """Update the name of a chat session."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.name = new_name
            session.updated_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Chat session name updated: {session_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update chat session name: {e}")
        db.rollback()
        return False
