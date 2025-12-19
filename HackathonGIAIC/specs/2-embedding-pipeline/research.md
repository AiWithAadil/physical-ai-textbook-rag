# Research: Embedding Pipeline Implementation

## Decision: Use Python with UV package manager for project setup

**Rationale**: Python is ideal for web scraping, text processing, and API integration. UV is a fast Rust-based package manager that provides faster dependency resolution than pip. The user specifically requested using UV package manager.

**Alternatives considered**:
- pip + venv: Standard but slower than UV
- Poetry: Feature-rich but potentially overkill for this simple project
- Conda: Good for data science but heavier than needed

## Decision: Cohere API for embeddings

**Rationale**: Cohere provides high-quality embeddings with good documentation and Python SDK. The user specifically requested Cohere for embeddings generation.

**Alternatives considered**:
- OpenAI embeddings: Also high quality but different pricing model
- Hugging Face transformers: Self-hosted option but requires more infrastructure
- Sentence Transformers: Free alternative but less consistent quality

## Decision: Qdrant for vector storage

**Rationale**: Qdrant is a dedicated vector database with good Python client, filtering capabilities, and scalable architecture. The user specifically requested Qdrant for storage.

**Alternatives considered**:
- Pinecone: Cloud-native but vendor lock-in
- Weaviate: Good alternative but user specified Qdrant
- Chroma: Lightweight but less scalable
- FAISS: Facebook's library but requires more manual management

## Decision: Beautiful Soup for HTML parsing

**Rationale**: Beautiful Soup is the standard Python library for parsing HTML and extracting content. It handles malformed HTML well and has excellent documentation.

**Alternatives considered**:
- Scrapy: More powerful but overkill for simple URL extraction
- Selenium: Good for JavaScript-heavy sites but unnecessary here
- lxml: Faster but more complex API

## Decision: Single main.py file structure with specified functions

**Rationale**: The user explicitly requested a single file with specific functions: get_all_urls, extract_text_from_url, chunk_text, embed, create_collection named rag_embedding, save_chunk_to_qdrant

**Function breakdown**:
- get_all_urls: Crawl the deployed site and extract all valid URLs
- extract_text_from_url: Extract clean text from a given URL
- chunk_text: Split large text into smaller chunks for embedding
- embed: Generate embeddings using Cohere API
- create_collection: Initialize Qdrant collection named 'rag_embedding'
- save_chunk_to_qdrant: Store embeddings with metadata in Qdrant

## Technical considerations for chunk size

**Rationale**: Cohere recommends chunk sizes between 256-512 tokens for optimal performance. For text, this typically translates to 1-2 paragraphs or roughly 500-1000 characters.

**Decision**: Use 1000 character chunks with 200 character overlap to maintain context while staying within API limits.

## URL crawling strategy for Docusaurus site

**Rationale**: Docusaurus sites have predictable URL structures and sitemaps that can be leveraged for efficient crawling.

**Approach**:
1. Check for /sitemap.xml to get all page URLs
2. If no sitemap, use robots.txt to understand site structure
3. Crawl starting from the provided URL: https://physical-ai-book-with-rag.vercel.app/