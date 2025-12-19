# API Contract: Embedding Pipeline Internal Functions

## Function: get_all_urls

**Purpose**: Crawl the deployed Docusaurus site and extract all valid URLs

**Input**:
- `base_url` (string): The base URL of the Docusaurus site to crawl
- `max_depth` (integer, optional): Maximum depth to crawl (default: 2)

**Output**:
- `urls` (array[string]): List of all discovered URLs
- `status` (string): Status of the crawling operation

**Error Cases**:
- Invalid base URL
- Network connectivity issues
- Site blocks crawling

## Function: extract_text_from_url

**Purpose**: Extract clean text content from a given URL

**Input**:
- `url` (string): The URL to extract text from

**Output**:
- `content` (string): Clean text content extracted from the page
- `title` (string): Title of the page
- `status` (string): Status of the extraction operation

**Error Cases**:
- URL is inaccessible
- Content extraction fails
- Page contains no readable text

## Function: chunk_text

**Purpose**: Split large text into smaller chunks for embedding

**Input**:
- `text` (string): The text to chunk
- `chunk_size` (integer, default: 1000): Maximum size of each chunk in characters
- `overlap` (integer, default: 200): Overlap between chunks in characters

**Output**:
- `chunks` (array[object]): Array of text chunks with metadata
  - `id` (string): Unique ID for the chunk
  - `content` (string): The chunk content
  - `position` (integer): Position in the original text

**Error Cases**:
- Text is empty
- Chunk size is invalid

## Function: embed

**Purpose**: Generate embeddings using Cohere API

**Input**:
- `texts` (array[string]): Array of text chunks to embed
- `model` (string, optional): Cohere model to use (default: "embed-english-v3.0")

**Output**:
- `embeddings` (array[object]): Array of embedding results
  - `chunk_id` (string): Reference to the original chunk
  - `embedding` (array[float]): The embedding vector
  - `model` (string): The model used

**Error Cases**:
- Cohere API unavailable
- Rate limit exceeded
- Invalid text input

## Function: create_collection

**Purpose**: Initialize Qdrant collection named 'rag_embedding'

**Input**:
- `collection_name` (string, default: "rag_embedding"): Name of the collection
- `vector_size` (integer, default: 1024): Size of the embedding vectors
- `distance` (string, default: "Cosine"): Distance metric for similarity search

**Output**:
- `status` (string): Status of the collection creation
- `collection_exists` (boolean): Whether the collection already existed

**Error Cases**:
- Qdrant unavailable
- Insufficient permissions
- Invalid collection parameters

## Function: save_chunk_to_qdrant

**Purpose**: Store embeddings with metadata in Qdrant

**Input**:
- `chunk_id` (string): Unique identifier for the chunk
- `embedding` (array[float]): The embedding vector
- `content` (string): Original text content
- `source_url` (string): URL where content was found
- `title` (string): Title of the source page
- `position` (integer): Position in the original document

**Output**:
- `status` (string): Status of the storage operation
- `point_id` (string): ID of the stored point in Qdrant

**Error Cases**:
- Qdrant unavailable
- Invalid embedding format
- Collection doesn't exist