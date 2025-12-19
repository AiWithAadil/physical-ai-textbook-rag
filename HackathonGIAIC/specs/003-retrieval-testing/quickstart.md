# Quick Start: Retrieval Service Development

**Feature**: Retrieval + Pipeline Testing for RAG Ingestion
**Date**: 2025-12-16

## Development Setup

### Prerequisites

- Python 3.11+
- Qdrant running locally or accessible via network
- Cohere API key (for query embedding)
- pip or uv for package management

### Installation

**1. Set up environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**2. Install dependencies**:
```bash
pip install -r requirements.txt
```

**Or with uv**:
```bash
uv venv
uv pip install -r requirements.txt
```

**3. Configure environment variables**:
```bash
# Create .env file in backend/ directory
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional, if Qdrant requires authentication
COHERE_API_KEY=your_cohere_api_key_here
LOG_LEVEL=INFO
```

### Start Qdrant Locally

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or using docker-compose (recommended)
# See docker-compose.yml in project root
docker-compose up qdrant
```

### Verify Setup

```bash
# Test Qdrant connection
python -c "
from src.services.qdrant_client import QdrantService
client = QdrantService()
print(client.health_check())
"

# Should output: {"status": "ok"}
```

---

## Project Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── search_query.py         # SearchQuery, QueryValidation
│   │   ├── search_result.py        # SearchResult, ChunkMetadata
│   │   └── metadata.py             # ExecutionMetadata, RetrievalResponse
│   ├── services/
│   │   ├── retrieval_service.py    # Main retrieval logic (orchestrator)
│   │   ├── embedding_service.py    # Query embedding generation
│   │   ├── qdrant_client.py        # Qdrant wrapper (async operations)
│   │   └── validation_service.py   # Data integrity verification
│   ├── api/
│   │   └── retrieval.py            # FastAPI endpoints (optional)
│   ├── utils/
│   │   ├── json_formatter.py       # Response formatting
│   │   └── error_handler.py        # Error handling utilities
│   └── config.py                   # Configuration management
├── tests/
│   ├── unit/
│   │   ├── test_retrieval_service.py
│   │   ├── test_embedding_service.py
│   │   ├── test_validation_service.py
│   │   └── test_qdrant_client.py
│   ├── integration/
│   │   ├── test_end_to_end_retrieval.py
│   │   ├── test_metadata_accuracy.py
│   │   └── test_chunk_matching.py
│   └── contract/
│       └── test_response_schema.py
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
└── README.md                       # Development guide
```

---

## Example: Semantic Search

### Basic Usage

```python
from src.services.retrieval_service import RetrievalService
from src.models.search_query import SearchQuery

# Initialize service
retrieval_service = RetrievalService()

# Create a search query
query = SearchQuery(
    query_text="How do I set up a vector database?",
    top_k=5,
    similarity_threshold=0.7
)

# Execute search
response = await retrieval_service.search(query)

# Process response
print(f"Query: {response.query}")
print(f"Results: {len(response.results)} matches found")
print(f"Latency: {response.execution.latency_ms}ms")

for i, result in enumerate(response.results, 1):
    print(f"\n{i}. {result.metadata.document_title}")
    print(f"   URL: {result.metadata.url}")
    print(f"   Similarity: {result.similarity_score:.2%}")
    print(f"   Text: {result.text[:100]}...")
```

### Expected Output

```
Query: How do I set up a vector database?
Results: 3 matches found
Latency: 145ms

1. Vector Database Setup Guide
   URL: https://docs.example.com/guide/setup
   Similarity: 92.00%
   Text: To set up a vector database, first install the Qdrant Docker image...

2. Qdrant Installation Instructions
   URL: https://docs.example.com/install
   Similarity: 88.00%
   Text: Install Qdrant using Docker Compose for production deployments...

3. Getting Started with Vector Search
   URL: https://docs.example.com/getting-started
   Similarity: 79.00%
   Text: Vector databases enable semantic search capabilities...
```

---

## Example: Data Validation

### Verify Chunk Integrity

```python
from src.services.validation_service import ValidationService

validation_service = ValidationService()

# Validate specific chunks
chunk_ids = ["550e8400-e29b-41d4-a716-446655440000"]
original_texts = ["To set up a vector database..."]

results = await validation_service.validate_chunks(
    chunk_ids=chunk_ids,
    original_texts=original_texts
)

# Check results
for result in results:
    if result.matches:
        print(f"✓ {result.chunk_id}: Data integrity verified")
    else:
        print(f"✗ {result.chunk_id}: Data mismatch detected")
        print(f"  Details: {result.mismatch_details}")
```

---

## Example: End-to-End Pipeline Test

### Complete Flow

```python
import asyncio
from src.services.retrieval_service import RetrievalService
from src.models.search_query import SearchQuery

async def test_complete_pipeline():
    """Test: input query → embedding → Qdrant search → JSON output"""

    service = RetrievalService()

    # 1. Input: Test query
    query_text = "What is semantic similarity?"
    query = SearchQuery(query_text=query_text, top_k=3, similarity_threshold=0.7)

    # 2. Execute retrieval (handles embedding + search internally)
    response = await service.search(query)

    # 3. Verify response structure
    assert response.query == query_text
    assert response.status == "success"
    assert len(response.results) <= 3
    assert response.execution.latency_ms < 2000

    # 4. Validate results
    for i, result in enumerate(response.results):
        assert result.rank == i + 1
        assert 0.7 <= result.similarity_score <= 1.0
        assert result.metadata.url is not None
        assert result.metadata.chunk_id is not None
        assert len(result.text) > 0

    # 5. Clean JSON output
    import json
    json_output = json.dumps(response.model_dump(), indent=2)
    print(json_output)

    return response

# Run test
response = asyncio.run(test_complete_pipeline())
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_retrieval_service.py

# Run with verbose output
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src/services --cov-report=html
```

### Integration Tests

```bash
# Requires Qdrant to be running
pytest tests/integration/

# Run with fixtures
pytest tests/integration/test_end_to_end_retrieval.py -v
```

### Contract Tests

```bash
# Validate API response schema
pytest tests/contract/ -v

# Should verify:
# - Response is valid JSON
# - All required fields present
# - Field types match specification
# - Error responses have proper format
```

### All Tests

```bash
# Run full test suite
pytest tests/ -v --tb=short

# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

---

## API Usage (if using FastAPI)

### Start API Server

```bash
# Install FastAPI if not in requirements.txt
pip install fastapi uvicorn

# Start server
uvicorn src.api.retrieval:app --reload

# Server will be available at http://localhost:8000
```

### Example API Calls

**Semantic Search**:
```bash
curl -X POST "http://localhost:8000/api/v1/retrieval/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I set up a vector database?",
    "top_k": 5,
    "similarity_threshold": 0.7
  }'
```

**Validate Chunks**:
```bash
curl -X POST "http://localhost:8000/api/v1/retrieval/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_ids": ["550e8400-e29b-41d4-a716-446655440000"],
    "original_texts": ["To set up a vector database..."]
  }'
```

### Response Example

```json
{
  "query": "How do I set up a vector database?",
  "status": "success",
  "results": [
    {
      "rank": 1,
      "text": "To set up a vector database, first install the Qdrant Docker image...",
      "similarity_score": 0.92,
      "metadata": {
        "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
        "url": "https://docs.example.com/guide/setup",
        "position": 245,
        "timestamp": "2025-12-15T10:30:00Z",
        "document_title": "Vector Database Setup Guide"
      }
    }
  ],
  "execution": {
    "latency_ms": 145,
    "result_count": 1,
    "threshold_applied": 0.7,
    "query_embedded_at": "2025-12-16T14:30:01Z",
    "qdrant_query_time_ms": 120
  },
  "errors": []
}
```

---

## Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all services will log detailed information
```

### Common Issues

**Issue**: "Qdrant service unavailable"
```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# If not, start it
docker run -p 6333:6333 qdrant/qdrant
```

**Issue**: "Failed to embed query"
```bash
# Check Cohere API key
echo $COHERE_API_KEY

# Verify API key is valid
python -c "import cohere; cohere.Client(api_key='your_key').embed(['test'])"
```

**Issue**: "No results found"
```python
# Check if Qdrant has data
from src.services.qdrant_client import QdrantService
client = QdrantService()
collection_info = client.get_collection_info()
print(f"Points in collection: {collection_info.points_count}")

# If 0, you need to run Feature 2 (embedding pipeline) first
```

---

## Next Steps

1. **Review Plan**: Read [plan.md](./plan.md) for design decisions and architecture
2. **Check Data Model**: See [data-model.md](./data-model.md) for entity specifications
3. **Review API Contract**: Check [contracts/](./contracts/) for OpenAPI schema
4. **Start Implementation**: Follow `/sp.tasks` task list for step-by-step development
5. **Run Tests**: Execute full test suite to verify implementation

---

## Performance Tips

### Query Optimization

```python
# Good: Specific query
query = SearchQuery(query_text="exact search term", top_k=5)

# Less optimal: Generic query
query = SearchQuery(query_text="tell me about everything", top_k=1000)
```

### Connection Pooling

```python
# Service manages connection pool automatically
# But you can configure it in config.py
QDRANT_POOL_SIZE=20  # Number of concurrent connections
QDRANT_TIMEOUT=5  # Request timeout in seconds
```

### Result Filtering

```python
# Use similarity_threshold to filter low-quality results
query = SearchQuery(
    query_text="...",
    top_k=100,
    similarity_threshold=0.8  # Only highly relevant results
)
```

---

## Resources

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **Cohere API**: https://docs.cohere.com/
- **AsyncIO Guide**: https://docs.python.org/3/library/asyncio.html
- **Pydantic**: https://docs.pydantic.dev/
- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
