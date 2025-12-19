# Quickstart: Embedding Pipeline

## Prerequisites

- Python 3.11 or higher
- UV package manager installed
- Cohere API key
- Qdrant instance (local or cloud)

## Setup

1. **Install UV package manager** (if not already installed):
   ```bash
   # For macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # For Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Create project directory**:
   ```bash
   mkdir backend
   cd backend
   ```

3. **Initialize project with UV**:
   ```bash
   uv init
   ```

4. **Install required dependencies**:
   ```bash
   uv add cohere qdrant-client requests beautifulsoup4
   ```

5. **Set environment variables**:
   ```bash
   export COHERE_API_KEY="your-cohere-api-key-here"
   export QDRANT_URL="your-qdrant-url"  # or leave empty for local instance
   export QDRANT_API_KEY="your-qdrant-api-key"  # if using cloud instance
   ```

## Running the Embedding Pipeline

1. **Create the main.py file** with the implementation as specified

2. **Run the pipeline**:
   ```bash
   python main.py
   ```

## Environment Variables

- `COHERE_API_KEY`: Your Cohere API key for generating embeddings
- `QDRANT_URL`: URL of your Qdrant instance (default: http://localhost:6333 for local)
- `QDRANT_API_KEY`: API key for Qdrant instance (if required)

## Expected Output

The pipeline will:
1. Crawl the target Docusaurus site (https://physical-ai-book-with-rag.vercel.app/)
2. Extract text content from all pages
3. Chunk the content into manageable pieces
4. Generate embeddings using Cohere
5. Store the embeddings in Qdrant with metadata
6. Create a collection named "rag_embedding" if it doesn't exist

## Verification

After running, you can verify the results by:
1. Checking the Qdrant instance for the "rag_embedding" collection
2. Confirming that points with your document metadata exist in the collection
3. Testing similarity searches to ensure embeddings are working correctly