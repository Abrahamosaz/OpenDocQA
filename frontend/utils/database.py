"""
Database connection and initialization utilities.
"""
import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.db import init_database, test_connection

def check_database_connection():
    """Check and initialize database connection."""
    if not st.session_state.database_initialized:
        with st.spinner("Initializing database..."):
            try:
                if test_connection():
                    init_database()
                    st.session_state.database_initialized = True
                else:
                    st.error("Failed to connect to database. Please check your configuration.")
                    return False
            except Exception as e:
                st.error(f"Database initialization failed: {str(e)}")
                return False
    return True
