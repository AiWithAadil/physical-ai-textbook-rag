# Embedding Pipeline for Docusaurus Content

This project implements an embedding pipeline that extracts text from deployed Docusaurus URLs, generates embeddings using Cohere, and stores them in Qdrant for RAG-based retrieval.

## Features

- Crawls Docusaurus sites to extract all accessible URLs
- Extracts clean text content while preserving document structure
- Chunks text appropriately for embedding generation
- Generates high-quality embeddings using Cohere API
- Stores embeddings in Qdrant vector database with metadata
- Creates a collection named "rag_embedding" as specified

## Prerequisites

- Python 3.11 or higher
- UV package manager
- Cohere API key
- Qdrant instance (local or cloud)

## Setup

1. **Install UV package manager**:
   ```bash
   # For macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # For Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   uv pip install -r requirements.txt
   # Or using pyproject.toml:
   uv sync
   ```

3. **Set environment variables**:
   ```bash
   export COHERE_API_KEY="your-cohere-api-key-here"
   export QDRANT_URL="your-qdrant-url"  # or leave empty for local instance
   export QDRANT_API_KEY="your-qdrant-api-key"  # if using cloud instance
   ```

## Usage

Run the complete pipeline:

```bash
cd backend
python main.py
```

The pipeline will:
1. Crawl the target Docusaurus site (https://physical-ai-book-with-rag.vercel.app/)
2. Extract text content from all pages
3. Chunk the content into manageable pieces
4. Generate embeddings using Cohere
5. Store the embeddings in Qdrant with metadata
6. Create a collection named "rag_embedding" if it doesn't exist

## Architecture

The implementation follows the specification with these key functions in `main.py`:

- `get_all_urls`: Crawls the deployed site and extracts all valid URLs
- `extract_text_from_url`: Extracts clean text from a given URL
- `chunk_text`: Splits large text into smaller chunks for embedding
- `embed`: Generates embeddings using Cohere API
- `create_collection`: Initializes Qdrant collection named 'rag_embedding'
- `save_chunk_to_qdrant`: Stores embeddings with metadata in Qdrant

## Testing

Run the tests:

```bash
pip install pytest
pytest tests/
```

## Configuration

- `COHERE_API_KEY`: Your Cohere API key for generating embeddings
- `QDRANT_URL`: URL of your Qdrant instance (default: http://localhost:6333 for local)
- `QDRANT_API_KEY`: API key for Qdrant instance (if required)

## Files Structure

```
backend/
├── main.py             # Single file implementation with all required functions
├── pyproject.toml      # Project configuration with dependencies
├── requirements.txt    # Dependencies managed by uv
└── README.md           # This file
```