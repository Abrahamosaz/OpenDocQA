#!/bin/bash

echo "🔧 Installing pgvector extension for PostgreSQL..."

# Check if we're on Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "📦 Installing dependencies for Ubuntu/Debian..."
    
    # Update package list
    sudo apt-get update
    
    # Install PostgreSQL development headers
    sudo apt-get install -y postgresql-server-dev-all postgresql-contrib
    
    # Install build dependencies
    sudo apt-get install -y build-essential git
    
    # Clone and install pgvector
    echo "📥 Cloning pgvector repository..."
    cd /tmp
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
    cd pgvector
    
    echo "🔨 Building pgvector..."
    make
    
    echo "📦 Installing pgvector..."
    sudo make install
    
    echo "✅ pgvector installed successfully!"
    
elif command -v yum &> /dev/null; then
    echo "📦 Installing dependencies for CentOS/RHEL..."
    
    # Install PostgreSQL development headers
    sudo yum install -y postgresql-devel postgresql-contrib
    
    # Install build dependencies
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y git
    
    # Clone and install pgvector
    echo "📥 Cloning pgvector repository..."
    cd /tmp
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
    cd pgvector
    
    echo "🔨 Building pgvector..."
    make
    
    echo "📦 Installing pgvector..."
    sudo make install
    
    echo "✅ pgvector installed successfully!"
    
else
    echo "❌ Unsupported operating system. Please install pgvector manually."
    echo "Visit: https://github.com/pgvector/pgvector#installation"
    exit 1
fi

echo ""
echo "🔧 Next steps:"
echo "1. Restart PostgreSQL: sudo systemctl restart postgresql"
echo "2. Connect to your database and run: CREATE EXTENSION vector;"
echo "3. Then run the Streamlit app again"

