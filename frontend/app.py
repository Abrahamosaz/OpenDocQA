"""
Streamlit frontend for the RAG Document QA System.
Modular architecture for better maintainability.
"""
import streamlit as st
import logging
from pathlib import Path

# Import configuration
from config.constants import PAGE_CONFIG, CUSTOM_CSS, TABS

# Import utilities
from utils.session import initialize_session_state
from utils.database import check_database_connection

# Import components
from components.header import display_header
from components.sidebar import sidebar

# Import pages
from pages.upload import upload_documents_section
from pages.manage import document_management_section
from pages.chat import chat_section

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Check database connection
    if not check_database_connection():
        st.error("Please check your database configuration and try again.")
        return
    
    # Display header
    display_header()
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(TABS)
    
    with tab1:
        upload_documents_section()
    
    with tab2:
        document_management_section()
    
    with tab3:
        chat_section()
    
    # Display sidebar
    sidebar()

if __name__ == "__main__":
    main()
