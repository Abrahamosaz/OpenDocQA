"""
Document management page functionality.
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.rag_pipeline import get_rag_pipeline

def document_management_section():
    """Handle document management section with enhanced UI."""
    st.markdown('<h2 class="section-header">📋 Document Management</h2>', unsafe_allow_html=True)
    
    try:
        rag_pipeline = get_rag_pipeline()
        
        # Get document list
        documents = rag_pipeline.get_document_list()
        
        if documents:
            # Display summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Documents", len(documents))
            with col2:
                total_chunks = sum(doc['chunks'] for doc in documents)
                st.metric("Total Chunks", total_chunks)
            with col3:
                if documents:
                    latest_doc = max(documents, key=lambda x: x['created_at'])
                    st.metric("Latest Upload", latest_doc['filename'][:20] + "..." if len(latest_doc['filename']) > 20 else latest_doc['filename'])
            
            st.markdown("---")
            
            # Search and filter options
            search_term = st.text_input("🔍 Search documents", placeholder="Enter filename to search...")
            
            # Filter documents based on search
            filtered_documents = documents
            if search_term:
                filtered_documents = [doc for doc in documents if search_term.lower() in doc['filename'].lower()]
            
            if not filtered_documents and search_term:
                st.warning(f"No documents found matching '{search_term}'")
                return
            
            # Display documents in a more organized way
            st.markdown(f"### 📚 Documents ({len(filtered_documents)} found)")
            
            for i, doc in enumerate(filtered_documents):
                with st.container():
                    # Create a card-like display for each document
                    st.markdown(f"""
                    <div class="document-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: #2c3e50;">📄 {doc['filename']}</h4>
                                <div class="document-info">
                                    <strong>Chunks:</strong> {doc['chunks']} | 
                                    <strong>Created:</strong> {doc['created_at'].strftime('%Y-%m-%d %H:%M') if hasattr(doc['created_at'], 'strftime') else str(doc['created_at'])}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons in columns
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        # Show document metadata if available
                        if doc.get('metadata'):
                            with st.expander("📋 View Metadata"):
                                st.json(doc['metadata'])
                    
                    with col2:
                        if st.button("📝 Summarize", key=f"summarize_{doc['filename']}_{i}", help="Generate AI summary"):
                            summarize_document(doc['filename'])
                    
                    with col3:
                        if st.button("👁️ View", key=f"view_{doc['filename']}_{i}", help="View document details"):
                            view_document(doc['filename'])
                    
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_{doc['filename']}_{i}", 
                                   help="Permanently delete document", 
                                   type="secondary"):
                            # Add confirmation dialog
                            if st.session_state.get(f"confirm_delete_{doc['filename']}", False):
                                delete_document(doc['filename'])
                                st.session_state[f"confirm_delete_{doc['filename']}"] = False
                            else:
                                st.session_state[f"confirm_delete_{doc['filename']}"] = True
                                st.warning(f"⚠️ Click 'Delete' again to confirm deletion of '{doc['filename']}'")
                                st.rerun()
                    
                    st.markdown("---")
            
            # Bulk actions
            st.markdown("### 🔧 Bulk Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Delete All Documents", type="secondary", help="Delete all documents (use with caution)"):
                    if st.session_state.get("confirm_delete_all", False):
                        delete_all_documents()
                        st.session_state["confirm_delete_all"] = False
                    else:
                        st.session_state["confirm_delete_all"] = True
                        st.warning("⚠️ Click 'Delete All Documents' again to confirm deletion of ALL documents")
                        st.rerun()
            
            with col2:
                if st.button("🔄 Refresh List", help="Refresh the document list"):
                    st.rerun()
                    
        else:
            st.info("📭 No documents uploaded yet. Please upload some documents first.")
            
            # Show upload instructions
            st.markdown("""
            ### How to upload documents:
            1. Go to the **Upload** tab
            2. Select your PDF, DOCX, or TXT files
            3. Click "Process" to upload and analyze your documents
            4. Come back to this tab to manage your documents
            """)
            
    except Exception as e:
        st.error(f"❌ Error loading documents: {str(e)}")
        st.info("Please check your database connection and try again.")

def summarize_document(filename: str):
    """Summarize a document with enhanced display."""
    try:
        with st.spinner(f"🤖 Generating summary for {filename}..."):
            rag_pipeline = get_rag_pipeline()
            result = rag_pipeline.summarize_document(filename)
            
            if result["success"]:
                st.markdown(f"### 📝 Summary of {filename}")
                
                # Display summary in a nice container
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #007bff;">
                    {result["summary"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Show intermediate steps if available
                if result.get("intermediate_steps"):
                    with st.expander("🔍 View Summary Process"):
                        for i, step in enumerate(result["intermediate_steps"], 1):
                            st.write(f"**Step {i}:** {step}")
            else:
                st.error(f"❌ Failed to summarize {filename}")
                
    except Exception as e:
        st.error(f"❌ Error summarizing document: {str(e)}")

def view_document(filename: str):
    """View document details with enhanced information."""
    try:
        st.markdown(f"### 📄 Document Details: {filename}")
        
        rag_pipeline = get_rag_pipeline()
        
        # Get document information
        documents = rag_pipeline.get_document_list()
        doc_info = next((doc for doc in documents if doc['filename'] == filename), None)
        
        if doc_info:
            # Display document information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **📊 Document Statistics:**
                - **Filename:** {doc_info['filename']}
                - **Number of Chunks:** {doc_info['chunks']}
                - **Created:** {doc_info['created_at']}
                """)
            
            with col2:
                if doc_info.get('metadata'):
                    st.markdown("**📋 Metadata:**")
                    st.json(doc_info['metadata'])
            
            # Show a preview of the document content
            st.markdown("**📖 Document Preview:**")
            st.info("Document content preview feature - to be implemented")
            
        else:
            st.error(f"Document '{filename}' not found")
            
    except Exception as e:
        st.error(f"❌ Error viewing document: {str(e)}")

def delete_document(filename: str):
    """Delete a document with confirmation."""
    try:
        rag_pipeline = get_rag_pipeline()
        success = rag_pipeline.delete_document(filename)
        
        if success:
            st.success(f"✅ Successfully deleted document: {filename}")
            # Add to deleted documents list for tracking
            st.session_state.deleted_documents.append(filename)
            st.rerun()
        else:
            st.error(f"❌ Failed to delete document: {filename}")
            
    except Exception as e:
        st.error(f"❌ Error deleting document: {str(e)}")

def delete_all_documents():
    """Delete all documents with confirmation."""
    try:
        rag_pipeline = get_rag_pipeline()
        documents = rag_pipeline.get_document_list()
        
        if not documents:
            st.info("No documents to delete.")
            return
        
        deleted_count = 0
        failed_count = 0
        
        with st.spinner(f"Deleting {len(documents)} documents..."):
            for doc in documents:
                success = rag_pipeline.delete_document(doc['filename'])
                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
        
        if deleted_count > 0:
            st.success(f"✅ Successfully deleted {deleted_count} documents")
        if failed_count > 0:
            st.error(f"❌ Failed to delete {failed_count} documents")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error deleting all documents: {str(e)}")
