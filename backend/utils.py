"""
Utility functions for document processing and text extraction.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
from docx import Document as DocxDocument
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Utility class for processing various document formats."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file content."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file content."""
        try:
            doc = DocxDocument(io.BytesIO(file_content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {e}")
            raise
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file content."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    text = file_content.decode(encoding)
                    logger.info(f"Extracted {len(text)} characters from TXT using {encoding}")
                    return text.strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 with error handling
            text = file_content.decode('utf-8', errors='ignore')
            logger.warning("Used utf-8 with error handling for TXT file")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from TXT: {e}")
            raise
    
    @staticmethod
    def extract_text_from_file(file_content: bytes, filename: str) -> str:
        """Extract text from file based on its extension."""
        file_extension = Path(filename).suffix.lower()
        
        if file_extension == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_content)
        elif file_extension in ['.docx', '.doc']:
            return DocumentProcessor.extract_text_from_docx(file_content)
        elif file_extension == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    @staticmethod
    def get_file_metadata(filename: str, file_size: int) -> Dict[str, Any]:
        """Get metadata for a file."""
        return {
            "filename": filename,
            "file_size": file_size,
            "file_extension": Path(filename).suffix.lower(),
            "processed_at": None  # Will be set during processing
        }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    @staticmethod
    def validate_file(file_content: bytes, filename: str, max_size: int = 10 * 1024 * 1024) -> bool:
        """Validate file before processing."""
        # Check file size
        if len(file_content) > max_size:
            raise ValueError(f"File too large: {len(file_content)} bytes (max: {max_size})")
        
        # Check file extension
        supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Check if file is not empty
        if len(file_content) == 0:
            raise ValueError("File is empty")
        
        return True

def process_uploaded_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Process an uploaded file and return extracted text and metadata."""
    try:
        # Validate file
        DocumentProcessor.validate_file(file_content, filename)
        
        # Extract text
        text = DocumentProcessor.extract_text_from_file(file_content, filename)
        
        # Clean text
        cleaned_text = DocumentProcessor.clean_text(text)
        
        # Get metadata
        metadata = DocumentProcessor.get_file_metadata(filename, len(file_content))
        
        return {
            "text": cleaned_text,
            "metadata": metadata,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Failed to process file {filename}: {e}")
        return {
            "text": "",
            "metadata": {},
            "success": False,
            "error": str(e)
        }

def get_supported_file_types() -> List[str]:
    """Get list of supported file types."""
    return ['.pdf', '.docx', '.doc', '.txt']

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
