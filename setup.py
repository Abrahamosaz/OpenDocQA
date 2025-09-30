#!/usr/bin/env python3
"""
Setup script for RAG Document QA System.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required")
        return False
    logger.info(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def check_database_connection():
    """Check if database is accessible."""
    try:
        from backend.db import test_connection
        if test_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def initialize_database():
    """Initialize database with required tables."""
    try:
        from backend.db import init_database
        if init_database():
            logger.info("✅ Database initialized successfully")
            return True
        else:
            logger.error("❌ Database initialization failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

def check_environment():
    """Check environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY", "DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please update your .env file with the required variables")
        return False
    
    logger.info("✅ Environment variables configured")
    return True

def main():
    """Main setup function."""
    logger.info("🚀 Setting up RAG Document QA System")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        logger.error("Please configure your environment variables first")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        logger.error("Please ensure PostgreSQL is running and configured correctly")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database")
        sys.exit(1)
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("You can now run the application with: streamlit run frontend/app.py")

if __name__ == "__main__":
    main()
