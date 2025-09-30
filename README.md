# RAG Document QA System

A Retrieval-Augmented Generation (RAG) system built with LangChain, PostgreSQL + pgvector, and Streamlit for document question-answering.

## 🚀 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Question Answering**: Ask natural language questions about your documents
- **Document Summarization**: Get AI-powered summaries of your documents
- **Conversational Interface**: Chat with your document collection
- **Vector Search**: Fast similarity search using pgvector

## 🛠️ Tech Stack

- **Backend**: Python + LangChain
- **Database**: PostgreSQL + pgvector
- **Frontend**: Streamlit
- **Embeddings**: OpenAI (text-embedding-ada-002)
- **LLM**: OpenAI GPT-3.5-turbo

## 📋 Prerequisites

1. **PostgreSQL** with pgvector extension
2. **Python 3.8+**
3. **OpenAI API Key**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

1. Install PostgreSQL and pgvector:

   ```bash
   # On Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib

   # Install pgvector
   git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   sudo make install
   ```

2. Create database and run migrations:

   ```bash
   # Create database
   createdb rag_db

   # Run SQL migrations
   psql rag_db < migrations/init.sql
   ```

### 3. Environment Configuration

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/rag_db
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 4. Run the Application

```bash
streamlit run frontend/app.py
```

## 📁 Project Structure

```
rag-project/
├── backend/
│   ├── db.py              # Database connection and models
│   ├── embeddings.py      # Embedding generation
│   ├── rag_pipeline.py    # RAG pipeline implementation
│   └── utils.py           # Document processing utilities
├── frontend/
│   └── app.py             # Streamlit UI
├── migrations/
│   └── init.sql           # Database schema
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔧 Configuration

### Database Configuration

Update the database connection in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/rag_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_db
DB_USER=username
DB_PASSWORD=password
```

### OpenAI Configuration

Set your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 📖 Usage

### 1. Upload Documents

1. Navigate to the "Upload" tab
2. Select PDF, DOCX, or TXT files
3. Click "Process" to upload and process documents

### 2. Ask Questions

1. Go to the "Chat" tab
2. Type your question in the chat input
3. Get AI-powered answers based on your documents

### 3. Document Management

1. Use the "Manage" tab to:
   - View all uploaded documents
   - Generate summaries
   - Delete documents

## 🔍 How It Works

1. **Document Processing**: Documents are split into chunks and embedded using OpenAI embeddings
2. **Vector Storage**: Embeddings are stored in PostgreSQL with pgvector for fast similarity search
3. **Question Answering**: User questions are embedded and matched against document chunks
4. **Response Generation**: Relevant chunks are passed to the LLM for answer generation

## 🛠️ Development

### Running Tests

```bash
# Run database tests
python -c "from backend.db import test_connection; test_connection()"

# Test embeddings
python -c "from backend.embeddings import get_embedding_service; print('Embeddings working')"
```

### Database Management

```bash
# Reset database
psql rag_db -c "DROP TABLE IF EXISTS documents;"
psql rag_db < migrations/init.sql
```

## 📝 API Reference

### RAG Pipeline

```python
from backend.rag_pipeline import get_rag_pipeline

# Get pipeline instance
pipeline = get_rag_pipeline()

# Process document
pipeline.process_and_store_document(content, filename)

# Answer question
response = pipeline.answer_question("What is this document about?")

# Summarize document
summary = pipeline.summarize_document("document.pdf")
```

### Database Operations

```python
from backend.db import get_db, store_document, get_similar_documents

# Get database session
db = get_db()

# Store document
store_document(db, filename, content, embedding, metadata)

# Find similar documents
similar_docs = get_similar_documents(db, query_embedding, limit=5)
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure pgvector extension is installed

2. **OpenAI API Errors**

   - Verify API key is correct
   - Check API quota and billing

3. **Document Processing Errors**
   - Ensure file format is supported
   - Check file size limits
   - Verify file is not corrupted

### Logs

Check application logs for detailed error information:

```bash
# Run with debug logging
PYTHONPATH=. python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- [Streamlit](https://streamlit.io/) for the web interface
- [OpenAI](https://openai.com/) for embeddings and language models
