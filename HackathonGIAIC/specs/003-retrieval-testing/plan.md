# Implementation Plan: Retrieval + Pipeline Testing for RAG Ingestion

**Branch**: `003-retrieval-testing` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-retrieval-testing/spec.md`

## Summary

Implement a semantic search and retrieval system that queries embeddings stored in Qdrant, verifies data integrity by comparing retrieved chunks against original extracted content, returns accurate metadata, and provides end-to-end pipeline testing with clean JSON responses. This feature validates the entire RAG ingestion flow from query → embedding → Qdrant search → formatted output.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: qdrant-client, cohere (for query embedding), pydantic (validation), fastapi (if API wrapper needed)
**Storage**: Qdrant vector database (external service)
**Testing**: pytest, pytest-asyncio (async Qdrant operations)
**Target Platform**: Linux/macOS backend service
**Project Type**: Backend service (single project)
**Performance Goals**: < 2 second latency for typical queries (< 100 tokens), support 100+ concurrent queries
**Constraints**: Qdrant availability, network latency, vector similarity accuracy > 95%
**Scale/Scope**: Support thousands of indexed chunks, real-time retrieval with sub-second response

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Specification-First ✅
- Feature spec is complete and unambiguous with clear user stories, functional requirements, and success criteria
- All acceptance scenarios are testable and define behavior precisely

### Modular Design ✅
- Retrieval module is self-contained and independently testable
- Clear interfaces: QueryRequest → RetrievalService → SearchResponse
- Can be tested independently from embedding pipeline (Feature 2)

### AI-Assisted Development ✅
- Plan uses specification-driven approach
- Testing strategy supports AI-generated test cases
- Code structure supports automated code generation

**GATE RESULT**: PASSED - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/003-retrieval-testing/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions & best practices
├── data-model.md        # Phase 1: Data structures & entities
├── quickstart.md        # Phase 1: Development setup & examples
├── contracts/           # Phase 1: API schemas
│   └── retrieval-api.openapi.yaml
└── checklists/
    └── requirements.md
```

### Source Code (backend folder - per user request)

```text
backend/
├── src/
│   ├── models/
│   │   ├── search_query.py       # Query request models
│   │   ├── search_result.py      # Result response models
│   │   └── metadata.py           # Metadata structures
│   ├── services/
│   │   ├── retrieval_service.py  # Core retrieval logic
│   │   ├── embedding_service.py  # Query embedding generation
│   │   ├── qdrant_client.py      # Qdrant wrapper
│   │   └── validation_service.py # Data integrity verification
│   ├── api/
│   │   └── retrieval.py          # API endpoints (if needed)
│   ├── utils/
│   │   ├── json_formatter.py     # Response formatting
│   │   └── error_handler.py      # Error handling
│   └── config.py
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
└── requirements.txt
```

**Structure Decision**: Backend service model with separation of concerns:
- **models/**: Pydantic data classes for type safety and validation
- **services/**: Business logic (retrieval, embedding, validation)
- **api/**: Optional REST endpoints for programmatic access
- **tests/**: Comprehensive test coverage with unit, integration, and contract tests

## Complexity Tracking

No violations detected. Constitution Check PASSED.

---

## Phase 0: Research & Technology Decisions

### Decision 1: Qdrant Query Interface

**Decision**: Use qdrant-client Python library with asyncio for concurrent query support

**Rationale**:
- Native Python support for type hints and async operations
- Efficient connection pooling for concurrent queries
- Direct REST API access as fallback

**Alternatives Considered**:
- Raw gRPC: More complex setup, overkill for this feature
- REST API only: Simpler but slower for many concurrent queries

**Implementation Details**:
```python
from qdrant_client.http import models as qd_models
from qdrant_client.http.client_async import AsyncQdrantClient

# Async client for concurrent queries
client = AsyncQdrantClient(
    url="http://localhost:6333",  # or env config
    timeout=5.0
)
```

### Decision 2: Query Embedding Strategy

**Decision**: Generate query embeddings using Cohere API (same as pipeline Feature 2) for consistency

**Rationale**:
- Vectors must be in same embedding space as stored document vectors
- Cohere embeddings are already integrated in Feature 2
- Ensures semantic similarity calculations are valid

**Alternatives Considered**:
- Local embedding model (e.g., sentence-transformers): Reduces dependency but may have different embedding space
- Cache query embeddings: Complex invalidation logic, marginal performance gain

**Implementation Details**:
```python
import cohere

co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

def embed_query(query: str) -> list[float]:
    response = co.embed(texts=[query], model="embed-english-v3.0")
    return response.embeddings[0]
```

### Decision 3: Data Integrity Verification

**Decision**: Store original chunk text as payload in Qdrant and compare on retrieval for 100% accuracy validation

**Rationale**:
- Guarantees retrieved content matches original stored content
- Enables local verification without external database access
- Supports validation testing requirement (FR-005)

**Alternatives Considered**:
- Query separate database: Additional complexity, network latency
- Hash-based verification: Loss of information, cannot display original text

**Implementation Details**:
```python
# Store during Feature 2 (embedding pipeline):
point = PointStruct(
    id=chunk_id,
    vector=embedding_vector,
    payload={
        "url": source_url,
        "chunk_id": chunk_id,
        "text": original_text,  # Store for verification
        "timestamp": created_at
    }
)
```

### Decision 4: JSON Response Format

**Decision**: Standardized response envelope with query, results array, and metadata

**Rationale**:
- Consistent structure for all responses (success and error cases)
- Includes query echo for verification
- Metadata supports timing and debugging

**Alternatives Considered**:
- GraphQL: Overkill for single retrieval operation
- Minimal JSON: Loses context and debugging info

**Implementation Details**:
```python
{
    "query": "original query string",
    "status": "success|error",
    "results": [
        {
            "rank": 1,
            "text": "retrieved chunk text",
            "metadata": {
                "url": "source url",
                "chunk_id": "chunk identifier",
                "similarity_score": 0.92
            }
        }
    ],
    "execution": {
        "latency_ms": 125,
        "result_count": 10,
        "threshold": 0.7
    },
    "errors": []
}
```

### Decision 5: Concurrency & Performance

**Decision**: Use asyncio with connection pooling for 100+ concurrent query support

**Rationale**:
- Non-blocking I/O prevents thread saturation
- Connection pooling reduces Qdrant connection overhead
- Meets performance requirement (< 2s latency)

**Alternatives Considered**:
- Threading: Higher memory overhead, GIL limitations
- Multiple processes: Complex state management

**Implementation Details**:
```python
# Connection pool configuration
client = AsyncQdrantClient(
    url="http://localhost:6333",
    timeout=5.0,
    grpc_options={"grpc.max_receive_message_length": 16 * 1024 * 1024}
)
```

---

## Phase 1: Design & Data Structures

### Data Model

See [data-model.md](./data-model.md) for complete entity specifications.

**Core Entities**:

1. **SearchQuery**
   - Fields: query_text, top_k, similarity_threshold
   - Validation: query_text non-empty, 0 < top_k ≤ 1000, 0 ≤ threshold < 1.0

2. **SearchResult**
   - Fields: rank, text, similarity_score, metadata (url, chunk_id, timestamp)
   - Invariants: results sorted by similarity_score descending

3. **RetrievalResponse**
   - Fields: query (echo), status, results[], execution metadata, errors[]
   - Structure: Envelope pattern for consistency

### API Contracts

See [contracts/retrieval-api.openapi.yaml](./contracts/retrieval-api.openapi.yaml) for complete OpenAPI specification.

**Endpoint 1: Semantic Search**
```
POST /api/v1/retrieval/search
Content-Type: application/json

{
  "query": "string (required)",
  "top_k": "integer (default: 5)",
  "similarity_threshold": "float (default: 0.0)"
}

Response (200):
{
  "query": "...",
  "status": "success",
  "results": [...],
  "execution": {...}
}

Response (400): Invalid query
Response (503): Qdrant unavailable
```

**Endpoint 2: Validation Test (for testing data integrity)**
```
POST /api/v1/retrieval/validate
Content-Type: application/json

{
  "chunk_ids": ["id1", "id2"],
  "original_texts": ["text1", "text2"]
}

Response (200):
{
  "validation_results": [
    {"chunk_id": "id1", "matches": true, "stored_text": "..."}
  ]
}
```

### Quick Start

See [quickstart.md](./quickstart.md) for development setup and example usage.

---

## Next Steps

1. **Phase 0 Complete**: All research decisions documented
2. **Phase 1 Complete**: Data model and API contracts defined
3. **Phase 2 Ready**: Proceed to `/sp.tasks` to generate testable implementation tasks
4. **ADR Recommendation**: Document query embedding strategy and data integrity verification as architectural decisions (run `/sp.adr retrieval-embedding-consistency` if significant)

---

## Implementation Readiness

✅ Technical context fully specified
✅ Constitution check passed
✅ Design decisions documented with rationale
✅ Data structures defined
✅ API contracts specified
✅ Project structure finalized
✅ Ready for implementation tasks phase
