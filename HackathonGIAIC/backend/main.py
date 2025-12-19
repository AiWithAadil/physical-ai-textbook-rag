import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
import time
import logging
from typing import List, Dict, Tuple
import re
import uuid

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")
co = cohere.Client(cohere_api_key)

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    prefer_grpc=False
)


def get_all_urls(base_url: str, max_depth: int = 2) -> List[str]:
    """
    Crawl the deployed Docusaurus site and extract all valid URLs
    """
    urls = set()
    urls.add(base_url)
    visited = set()

    # First try to get URLs from sitemap
    sitemap_url = urljoin(base_url, "sitemap.xml")
    try:
        sitemap_response = requests.get(sitemap_url, timeout=10)
        if sitemap_response.status_code == 200:
            soup = BeautifulSoup(sitemap_response.content, 'xml')
            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                if url.startswith(base_url):
                    urls.add(url)
    except Exception as e:
        logger.warning(f"Could not fetch sitemap: {e}")

    # If no sitemap or for additional crawling, do manual crawling
    to_visit = [base_url]
    current_depth = 0

    while to_visit and current_depth < max_depth:
        current_urls = to_visit[:]
        to_visit = []

        for url in current_urls:
            if url in visited:
                continue
            visited.add(url)

            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find all links on the page
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        full_url = urljoin(url, href)

                        # Only add URLs that are within the same domain
                        if urlparse(full_url).netloc == urlparse(base_url).netloc:
                            if full_url.startswith(base_url) and full_url not in urls:
                                urls.add(full_url)
                                to_visit.append(full_url)

                # Be respectful with requests
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")

        current_depth += 1

    return list(urls)


def extract_text_from_url(url: str) -> Tuple[str, str]:
    """
    Extract clean text content from a given URL
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get the title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "No Title"

        # Try to find the main content area in a Docusaurus site
        # Common selectors for Docusaurus content
        content_selectors = [
            'main article',
            'main div',
            '.main-wrapper',
            '.container',
            'article',
            '.markdown'
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        # If no specific content area found, use the body
        if not content_element:
            content_element = soup.find('body')

        if content_element:
            # Get text and clean it up
            text = content_element.get_text(separator=' ')
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
        else:
            text = ""

        return text, title

    except Exception as e:
        logger.error(f"Error extracting text from {url}: {e}")
        return "", "Error Page"


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    Split large text into smaller chunks for embedding
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        # If this is not the last chunk and we have overlap
        if end < text_length:
            # Try to break at sentence boundary near the end
            chunk_text = text[start:end]
            last_sentence_end = max(
                chunk_text.rfind('. ', overlap),
                chunk_text.rfind('? ', overlap),
                chunk_text.rfind('! ', overlap)
            )

            if last_sentence_end != -1 and last_sentence_end > overlap:
                end = start + last_sentence_end + 1
            else:
                # If no good sentence break, use word boundary
                last_space = chunk_text.rfind(' ', overlap)
                if last_space != -1 and last_space > overlap:
                    end = start + last_space

        # Ensure we don't go beyond the text length
        end = min(end, text_length)

        chunk_content = text[start:end].strip()
        if chunk_content:
            chunks.append({
                'id': f"chunk_{start}_{end}",
                'content': chunk_content,
                'position': start
            })

        # Move start to create overlap or next chunk
        if end == text_length:
            break

        start = end - overlap if overlap < end - start else start + chunk_size

    return chunks


def embed(texts: List[str], model: str = "embed-english-v3.0") -> List[Dict]:
    """
    Generate embeddings using Cohere API
    """
    if not texts:
        return []

    # Batch embeddings to optimize API usage
    batch_size = 96  # Cohere's recommended batch size
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        try:
            response = co.embed(
                texts=batch,
                model=model,
                input_type="search_document"  # Appropriate for RAG use case
            )

            for j, embedding in enumerate(response.embeddings):
                embeddings.append({
                    'chunk_id': f"batch_{i}_item_{j}",
                    'embedding': embedding,
                    'model': model
                })

            # Be respectful with API limits
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error generating embeddings for batch {i}: {e}")
            # Add placeholder for failed embeddings
            for j in range(len(batch)):
                embeddings.append({
                    'chunk_id': f"batch_{i}_item_{j}",
                    'embedding': [0.0] * 1024,  # Placeholder vector
                    'model': model,
                    'error': str(e)
                })

    return embeddings


def create_collection(collection_name: str = "rag_embedding", vector_size: int = 1024) -> bool:
    """
    Initialize Qdrant collection named 'rag_embedding'
    """
    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_exists = any(col.name == collection_name for col in collections.collections)

        if not collection_exists:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created new collection: {collection_name}")
        else:
            logger.info(f"Collection already exists: {collection_name}")

        return True
    except Exception as e:
        logger.error(f"Error creating collection {collection_name}: {e}")
        return False


def save_chunk_to_qdrant(
    chunk_id: str,
    embedding: List[float],
    content: str,
    source_url: str,
    title: str,
    position: int
) -> bool:
    """
    Store embeddings with metadata in Qdrant
    """
    try:
        # Generate a proper UUID for the point ID
        point_id = str(uuid.uuid4())

        points = [
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "source_url": source_url,
                    "title": title,
                    "position": position,
                    "original_chunk_id": chunk_id,  # Keep original chunk ID in payload
                    "created_at": time.time()
                }
            )
        ]

        qdrant_client.upsert(
            collection_name="rag_embedding",
            points=points
        )

        logger.info(f"Saved chunk {chunk_id} to Qdrant with point ID {point_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving chunk {chunk_id} to Qdrant: {e}")
        return False


def main():
    """
    Main function to execute the entire pipeline
    """
    logger.info("Starting embedding pipeline...")

    # Step 1: Create collection
    logger.info("Creating Qdrant collection...")
    if not create_collection():
        logger.error("Failed to create Qdrant collection")
        return

    # Step 2: Get all URLs from the target site
    target_url = "https://physical-ai-book-with-rag.vercel.app/"
    logger.info(f"Extracting URLs from {target_url}...")
    urls = get_all_urls(target_url, max_depth=2)
    logger.info(f"Found {len(urls)} URLs to process")

    # Step 3: Process each URL
    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

        # Extract text and title from URL
        content, title = extract_text_from_url(url)

        if not content.strip():
            logger.warning(f"No content extracted from {url}, skipping")
            continue

        # Chunk the content
        chunks = chunk_text(content, chunk_size=1000, overlap=200)
        logger.info(f"Created {len(chunks)} chunks from {url}")

        # Process each chunk
        for j, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {j+1}/{len(chunks)} for {url}")

            # Embed the chunk content
            embeddings = embed([chunk['content']])

            if embeddings and 'error' not in embeddings[0]:
                # Save to Qdrant
                success = save_chunk_to_qdrant(
                    chunk_id=f"{url_hash(url)}_{chunk['id']}",
                    embedding=embeddings[0]['embedding'],
                    content=chunk['content'],
                    source_url=url,
                    title=title,
                    position=chunk['position']
                )

                if not success:
                    logger.error(f"Failed to save chunk {chunk['id']} to Qdrant")
            else:
                logger.error(f"Failed to generate embedding for chunk {chunk['id']}")

    logger.info("Embedding pipeline completed!")


def url_hash(url: str) -> str:
    """
    Simple hash function to create a shorter identifier from URL
    """
    import hashlib
    return hashlib.md5(url.encode()).hexdigest()[:12]


if __name__ == "__main__":
    main()