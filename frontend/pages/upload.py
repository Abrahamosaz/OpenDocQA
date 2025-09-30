"""
Document upload page functionality.
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.utils import process_uploaded_file, get_supported_file_types, format_file_size
from backend.rag_pipeline import get_rag_pipeline

def upload_documents_section():
    """Handle document upload section."""
    st.markdown('<h2 class="section-header">📁 Upload Documents</h2>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=get_supported_file_types(),
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files:
        st.markdown("### Uploaded Files:")
        
        for uploaded_file in uploaded_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"📄 {uploaded_file.name}")
                st.write(f"Size: {format_file_size(uploaded_file.size)}")
            
            with col2:
                if st.button("Process", key=f"process_{uploaded_file.name}"):
                    process_single_file(uploaded_file)
            
            with col3:
                if st.button("Remove", key=f"remove_{uploaded_file.name}"):
                    st.rerun()

def process_single_file(uploaded_file):
    """Process a single uploaded file."""
    try:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            # Read file content
            file_content = uploaded_file.read()
            
            # Process the file
            result = process_uploaded_file(file_content, uploaded_file.name)
            
            if result["success"]:
                # Get RAG pipeline
                rag_pipeline = get_rag_pipeline()
                
                # Process and store document
                success = rag_pipeline.process_and_store_document(
                    content=result["text"],
                    filename=uploaded_file.name,
                    metadata=result["metadata"]
                )
                
                if success:
                    st.success(f"✅ Successfully processed and stored: {uploaded_file.name}")
                    st.session_state.documents.append(uploaded_file.name)
                    st.rerun()  # Refresh to show updated document list
                else:
                    st.error(f"❌ Failed to store document: {uploaded_file.name}")
            else:
                st.error(f"❌ Failed to process file: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
