"""
Session state management utilities.
"""
import streamlit as st
from typing import Any, Dict

def initialize_session_state():
    """Initialize session state variables."""
    session_keys = {
        "messages": [],
        "documents": [],
        "database_initialized": False,
        "deleted_documents": [],
        "current_chat_session_id": None
    }
    
    for key, default_value in session_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_session_value(key: str, default: Any = None) -> Any:
    """Get a value from session state."""
    return st.session_state.get(key, default)

def set_session_value(key: str, value: Any) -> None:
    """Set a value in session state."""
    st.session_state[key] = value

def clear_session_value(key: str) -> None:
    """Clear a value from session state."""
    if key in st.session_state:
        del st.session_state[key]
