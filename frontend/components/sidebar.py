"""
Sidebar components for chat sessions and system info.
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.db import get_db, create_chat_session, get_chat_sessions, get_chat_session, delete_chat_session
from backend.rag_pipeline import get_rag_pipeline

def sidebar():
    """Display sidebar with chat history and session management."""
    with st.sidebar:
        st.markdown("## 💬 Chat Sessions")
        
        try:
            db = get_db()
            
            # Create new chat session
            with st.expander("➕ Create New Session", expanded=False):
                # Use a more specific key and ensure the input is properly configured
                new_session_name = st.text_input(
                    "Session Name", 
                    placeholder="Enter session name...", 
                    key="new_session_name",
                    help="Enter a name for your new chat session"
                )
                
                if st.button("Create", key="create_session_btn"):
                    if new_session_name and new_session_name.strip():
                        session_id = create_chat_session(db, new_session_name.strip())
                        if session_id:
                            st.success(f"✅ Created: {new_session_name}")
                            st.session_state.current_chat_session_id = session_id
                            st.rerun()
                        else:
                            st.error("❌ Failed to create session")
                    else:
                        st.warning("Please enter a name")
            
            st.markdown("---")
            
            # Get and display chat sessions
            sessions = get_chat_sessions(db)
            
            if sessions:
                st.markdown(f"**Your Sessions ({len(sessions)})**")
                
                for session in sessions:
                    is_active = st.session_state.current_chat_session_id == session['id']
                    
                    # Session display with actions
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.button(
                            f"💬 {session['name']}", 
                            key=f"select_{session['id']}",
                            help=f"{session['message_count']} messages • {session['created_at'].strftime('%m/%d %H:%M') if hasattr(session['created_at'], 'strftime') else str(session['created_at'])}",
                            use_container_width=True
                        ):
                            st.session_state.current_chat_session_id = session['id']
                            st.rerun()
                    
                    with col2:
                        # Simplified delete button - no confirmation needed
                        if st.button("🗑️", key=f"delete_{session['id']}", help="Delete session"):
                            try:
                                if delete_chat_session(db, session['id']):
                                    st.success(f"✅ Deleted: {session['name']}")
                                    # Clear current session if it was deleted
                                    if st.session_state.current_chat_session_id == session['id']:
                                        st.session_state.current_chat_session_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete session")
                            except Exception as e:
                                st.error(f"❌ Error deleting session: {str(e)}")
                
                # Current session info
                if st.session_state.current_chat_session_id:
                    current_session = get_chat_session(db, st.session_state.current_chat_session_id)
                    if current_session:
                        st.markdown("---")
                        st.markdown(f"**Current:** {current_session['name']}")
                        st.markdown(f"Messages: {len(current_session['messages'])}")
                        
                        # Clear current session button
                        if st.button("🗑️ Clear Current Chat", key="clear_current"):
                            st.session_state.current_chat_session_id = None
                            st.rerun()
            else:
                st.info("📭 No chat sessions yet. Create your first session above!")
            
        except Exception as e:
            st.error(f"❌ Error loading sessions: {str(e)}")
        
        st.markdown("---")
        
        # System info
        st.markdown("## 📊 System Info")
        try:
            rag_pipeline = get_rag_pipeline()
            documents = rag_pipeline.get_document_list()
            st.write(f"📄 Documents: {len(documents)}")
        except Exception as e:
            st.write("📄 Documents: Error loading")
