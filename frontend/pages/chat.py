"""
Chat interface page functionality.
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.db import get_db, get_chat_session, add_message_to_session
from backend.rag_pipeline import get_rag_pipeline

def chat_section():
    """Handle chat interface section."""
    st.markdown('<h2 class="section-header">💬 Chat with Documents</h2>', unsafe_allow_html=True)
    
    try:
        db = get_db()
        
        # Check if we have a current chat session
        if st.session_state.current_chat_session_id is None:
            st.info("👆 Please select or create a chat session from the sidebar to start chatting.")
            return
        
        # Get current session info
        current_session = get_chat_session(db, st.session_state.current_chat_session_id)
        if not current_session:
            st.error("❌ Current chat session not found. Please select a different session.")
            st.session_state.current_chat_session_id = None
            return
        
        # Display current session info
        st.markdown(f"**Current Session:** {current_session['name']} ({len(current_session['messages'])} messages)")
    
        # Display chat messages
        for message in current_session['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if message.get("metadata", {}).get("sources"):
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(message["metadata"]["sources"], 1):
                            st.write(f"**Source {i}:** {source['filename']}")
                            st.write(f"**Relevance:** {source['similarity']:.2%}")
                            st.write(f"**Content:** {source['content']}")

        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to database
            add_message_to_session(db, st.session_state.current_chat_session_id, "user", prompt)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from RAG pipeline
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        rag_pipeline = get_rag_pipeline()
                        response = rag_pipeline.answer_question(prompt)
                        
                        # Display answer
                        st.markdown(response["answer"])
                        
                        # Prepare metadata for storage
                        metadata = {}
                        if response["sources"]:
                            metadata["sources"] = response["sources"]
                        
                        # Add assistant response to database
                        add_message_to_session(
                            db, 
                            st.session_state.current_chat_session_id, 
                            "assistant", 
                            response["answer"],
                            metadata
                        )
                        
                        # Display sources if available
                        if response["sources"]:
                            with st.expander("📚 Sources"):
                                for i, source in enumerate(response["sources"], 1):
                                    st.write(f"**Source {i}:** {source['filename']}")
                                    st.write(f"**Relevance:** {source['similarity']:.2%}")
                                    st.write(f"**Content:** {source['content']}")
                        
                        # Refresh the page to show the new messages
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error getting response: {str(e)}")
                        
    except Exception as e:
        st.error(f"❌ Error in chat section: {str(e)}")
