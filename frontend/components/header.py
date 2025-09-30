"""
Header and navigation components.
"""
import streamlit as st

def display_header():
    """Display the main header."""
    st.markdown('<h1 class="main-header">📚 RAG Document QA System</h1>', unsafe_allow_html=True)
    st.markdown("Upload documents, ask questions, and get AI-powered answers based on your content.")
