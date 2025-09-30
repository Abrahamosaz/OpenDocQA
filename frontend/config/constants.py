"""
Configuration constants and settings for the RAG Document QA System.
"""

# Page configuration
PAGE_CONFIG = {
    "page_title": "RAG Document QA System",
    "page_icon": "📚",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Custom CSS styles
CUSTOM_CSS = """
<style>
    /* Hide Streamlit default navigation - more specific targeting */
    .stApp > div:first-child > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }
    
    /* Hide sidebar navigation items but preserve input fields */
    .stSidebar > div:first-child > div:first-child > div:first-child > div:first-child {
        display: none !important;
    }
    
    /* Hide navigation links specifically */
    .stSidebar [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Hide any default Streamlit navigation */
    .stSidebar .stSidebarNav {
        display: none !important;
    }
    
    /* Hide "Press Enter to apply" text - more aggressive targeting */
    .stSidebar .stTextInput > div > div > div > div {
        display: none !important;
    }
    
    /* Hide any overlay text in text inputs */
    .stSidebar .stTextInput > div > div > div {
        display: none !important;
    }
    
    /* Hide help text and overlays */
    .stSidebar .stTextInput > div > div > div > div > div {
        display: none !important;
    }
    
    /* Hide any text overlays in input containers */
    .stSidebar .stTextInput > div > div > div > div > span {
        display: none !important;
    }
    
    /* Hide any absolute positioned text overlays */
    .stSidebar .stTextInput > div > div > div > div[style*="position: absolute"] {
        display: none !important;
    }
    
    /* Hide any text that contains "Press Enter" */
    .stSidebar *:contains("Press Enter") {
        display: none !important;
    }
    
    /* More specific targeting for Streamlit text input overlays */
    .stSidebar .stTextInput > div > div > div > div > div > div {
        display: none !important;
    }
    
    /* Remove red border and hover effects from input fields */
    .stSidebar input[type="text"] {
        display: block !important;
        pointer-events: auto !important;
        border: 1px solid #ccc !important;
        border-radius: 4px !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    
    /* Remove focus/hover red effects */
    .stSidebar input[type="text"]:focus {
        border: 1px solid #007bff !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stSidebar input[type="text"]:hover {
        border: 1px solid #007bff !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Hide any overlay elements */
    .stSidebar .stTextInput > div > div > div > div > div > div > div {
        display: none !important;
    }
    
    /* Ensure buttons work properly */
    .stSidebar button {
        display: block !important;
        pointer-events: auto !important;
    }
    
    /* Ensure expanders work properly */
    .stSidebar .streamlit-expander {
        display: block !important;
    }
    
    /* Hide any help text overlays */
    .stSidebar .stTextInput > div > div > div > div {
        display: none !important;
    }
    
    /* Additional targeting for Streamlit's text input structure */
    .stSidebar .stTextInput > div > div > div > div > div > div > div > div {
        display: none !important;
    }
    
    /* Hide any text overlays that might be positioned absolutely */
    .stSidebar .stTextInput > div > div > div > div > div > div > div > div > div {
        display: none !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .document-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #fafafa;
    }
    .document-info {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .delete-button {
        background-color: #dc3545;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
    }
    .delete-button:hover {
        background-color: #c82333;
    }
    .chat-session-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
        border: 1px solid #e0e0e0;
    }
    .chat-session-item:hover {
        background-color: #f0f0f0;
    }
    .chat-session-item.active {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }
</style>
"""

# Session state keys
SESSION_KEYS = {
    "messages": "messages",
    "documents": "documents", 
    "database_initialized": "database_initialized",
    "deleted_documents": "deleted_documents",
    "current_chat_session_id": "current_chat_session_id"
}

# Tab configuration
TABS = ["📁 Upload", "📋 Manage", "💬 Chat"]
