# Data Model: Retrieval + Pipeline Testing

**Feature**: Retrieval Testing for RAG Ingestion
**Date**: 2025-12-16
**Version**: 1.0

## Core Entities

### 1. SearchQuery

**Purpose**: Represents a user's search request for semantic retrieval.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| query_text | string | Yes | Non-empty, max 10000 chars | The search query text to embed and match |
| top_k | integer | No | 1 ≤ top_k ≤ 1000, default 5 | Number of top results to return |
| similarity_threshold | float | No | 0.0 ≤ threshold < 1.0, default 0.0 | Minimum similarity score filter |

**Validation Rules**:
- `query_text` must not be empty or whitespace-only
- `top_k` must be positive and not exceed system limits (1000)
- `similarity_threshold` must be between 0.0 and 1.0
- If any field is invalid, return HTTP 400 with descriptive error

**State Transitions**: None (immutable request)

**Example**:
```json
{
  "query_text": "How do I set up a vector database?",
  "top_k": 10,
  "similarity_threshold": 0.7
}
```

---

### 2. ChunkMetadata

**Purpose**: Represents metadata about a document chunk stored in Qdrant.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| chunk_id | string | Yes | UUID format | Unique identifier for the chunk |
| url | string | Yes | Valid URL | Source document URL |
| position | integer | No | Non-negative | Position in document (word count or chunk index) |
| timestamp | string | No | ISO 8601 format | When chunk was created/indexed |
| document_title | string | No | Max 500 chars | Title of source document |

**Validation Rules**:
- `chunk_id` must be a valid UUID or string identifier matching pipeline Feature 2
- `url` must be a valid, accessible URL
- `timestamp` must be ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- All fields should be retrievable from Qdrant payload

**State Transitions**: None (immutable from retrieval perspective)

**Example**:
```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://docs.example.com/guide/setup",
  "position": 245,
  "timestamp": "2025-12-15T10:30:00Z",
  "document_title": "Vector Database Setup Guide"
}
```

---

### 3. SearchResult

**Purpose**: Represents a single search result returned from Qdrant.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| rank | integer | Yes | Positive, 1-indexed | Rank in result set (1st, 2nd, etc.) |
| text | string | Yes | Non-empty | The actual retrieved chunk text |
| similarity_score | float | Yes | 0.0 ≤ score ≤ 1.0 | Cosine similarity with query |
| metadata | ChunkMetadata | Yes | Valid ChunkMetadata | Source information |

**Validation Rules**:
- `rank` must start at 1 and increment by 1
- `text` must match original stored text exactly (100% verification)
- `similarity_score` must be computed by Qdrant (cosine similarity)
- `metadata` must be complete and match Qdrant payload
- Results must be sorted by similarity_score in descending order

**Invariants**:
- For a given query, results[i].similarity_score ≥ results[i+1].similarity_score
- All results must pass similarity_score ≥ similarity_threshold from query

**State Transitions**: None (immutable result)

**Example**:
```json
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
```

---

### 4. ExecutionMetadata

**Purpose**: Tracks performance and debugging information for a search request.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| latency_ms | integer | Yes | Non-negative | Time from query to response (milliseconds) |
| result_count | integer | Yes | Non-negative | Number of results returned |
| threshold_applied | float | Yes | 0.0 ≤ threshold < 1.0 | Similarity threshold used |
| query_embedded_at | string | No | ISO 8601 | When query was embedded |
| qdrant_query_time_ms | integer | No | Non-negative | Time Qdrant took to search |

**Validation Rules**:
- `latency_ms` should be < 2000 for typical queries (success criterion)
- `result_count` must match length of results array
- `threshold_applied` must match threshold from SearchQuery
- Timestamps must be ISO 8601 format

**Example**:
```json
{
  "latency_ms": 145,
  "result_count": 5,
  "threshold_applied": 0.7,
  "query_embedded_at": "2025-12-16T14:30:01Z",
  "qdrant_query_time_ms": 120
}
```

---

### 5. RetrievalResponse

**Purpose**: Complete response envelope for a search request.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| query | string | Yes | Non-empty | Echo of original query text |
| status | enum | Yes | "success" \| "error" | Request status |
| results | SearchResult[] | Yes | Valid SearchResult array | Array of results (0+ items) |
| execution | ExecutionMetadata | Yes | Valid ExecutionMetadata | Performance metadata |
| errors | string[] | No | Array of strings | Error messages if status="error" |

**Validation Rules**:
- `query` must be the exact original query from SearchQuery
- `status` must be "success" when results are returned, "error" when issues occur
- If `status="success"`, results array must be valid (may be empty if no matches)
- If `status="error"`, errors array must contain at least one error message
- `execution` metadata must be present and complete
- Total response must be valid JSON (parseable with any JSON parser)

**Invariants**:
- `len(results) ≤ top_k` from original SearchQuery
- `len(results) == execution.result_count`
- All results have `similarity_score ≥ similarity_threshold`
- Response is always valid JSON, never truncated

**Example Success**:
```json
{
  "query": "How do I set up a vector database?",
  "status": "success",
  "results": [
    {
      "rank": 1,
      "text": "To set up a vector database, first install...",
      "similarity_score": 0.92,
      "metadata": {...}
    }
  ],
  "execution": {
    "latency_ms": 145,
    "result_count": 1,
    "threshold_applied": 0.7
  },
  "errors": []
}
```

**Example Error**:
```json
{
  "query": "How do I set up a vector database?",
  "status": "error",
  "results": [],
  "execution": {
    "latency_ms": 50,
    "result_count": 0,
    "threshold_applied": 0.0
  },
  "errors": [
    "Qdrant service unavailable at http://localhost:6333",
    "Connection timeout after 5 seconds"
  ]
}
```

---

### 6. ValidationResult

**Purpose**: Data integrity validation result for testing chunk accuracy.

**Fields**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-----------|-------------|
| chunk_id | string | Yes | UUID format | The chunk being validated |
| matches | boolean | Yes | True \| False | Whether stored text matches original |
| stored_text | string | Yes | Non-empty | Text currently stored in Qdrant |
| original_text | string | Yes | Non-empty | Original text from pipeline |
| validation_passed | boolean | Yes | True \| False | Overall validation status |
| mismatch_details | string | No | Details if mismatch | Description of differences |

**Validation Rules**:
- `chunk_id` must exist in Qdrant
- `matches` is true only if stored_text === original_text (exact match)
- If `matches=false`, mismatch_details must describe the difference
- `validation_passed` must be true only if matches=true and no corruption

**Example Pass**:
```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
  "matches": true,
  "stored_text": "To set up a vector database...",
  "original_text": "To set up a vector database...",
  "validation_passed": true,
  "mismatch_details": null
}
```

**Example Fail**:
```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
  "matches": false,
  "stored_text": "To set up a vector dat...",
  "original_text": "To set up a vector database...",
  "validation_passed": false,
  "mismatch_details": "Stored text truncated or corrupted (length mismatch: 24 vs 32 chars)"
}
```

---

## Relationships

```
SearchQuery
    ↓ (embedded by embedding_service)
    → Query Vector (float[])
    ↓ (searched in)
Qdrant Vector Store
    ↓ (retrieves)
    → SearchResult[] (contains rank, text, similarity_score)
    → ChunkMetadata (from Qdrant payload)
    ↓ (formatted as)
RetrievalResponse
    → ExecutionMetadata (timing, result count)
    → errors[] (if applicable)
```

---

## Data Integrity & Validation

### Verification Strategy

**Requirement FR-005**: System MUST verify that retrieved chunk text matches exactly with the original stored content.

**Implementation**:
1. During Feature 2 (embedding pipeline): Store original text in Qdrant payload
2. During Feature 3 (retrieval): Retrieve text from payload with each search result
3. In tests: Compare retrieved text against original extracted text with byte-by-byte comparison

**Validation Endpoints**:
- Unit tests: Compare SearchResult.text against original chunks from pipeline
- Integration tests: End-to-end flow with known test data
- Contract tests: Validate JSON response schema matches RetrievalResponse

---

## Performance Constraints

**Table Size Estimates**:
- SearchQuery: ~100 bytes per request
- SearchResult: ~500-2000 bytes per result (depends on text length)
- RetrievalResponse: ~100 bytes overhead + results + execution metadata
- Typical response: 5-10 results × 1000 bytes = 5-10 KB

**Memory Estimates**:
- Async client connection pool: ~5-10 MB
- Query embedding cache (if added): ~100 MB per 100k queries
- In-memory result set (top-k ≤ 1000): ~2-5 MB per concurrent query

**Latency Targets**:
- Query embedding (Cohere API): 100-200 ms
- Qdrant search: 50-100 ms
- Response formatting: < 10 ms
- **Total**: < 2000 ms (success criterion)

---

## Error Handling

**Error Categories**:

| Category | Example | HTTP Status | Message |
|----------|---------|-------------|---------|
| Validation | Empty query_text | 400 | "query_text cannot be empty" |
| Validation | Invalid top_k | 400 | "top_k must be between 1 and 1000" |
| Service Unavailable | Qdrant down | 503 | "Qdrant service unavailable at {url}" |
| Service Unavailable | Cohere API error | 503 | "Failed to embed query: {reason}" |
| Not Found | Chunk doesn't exist (for validate) | 404 | "Chunk {chunk_id} not found" |
| Internal Server Error | Unexpected exception | 500 | "Internal server error: {reason}" |

**Error Response Structure**:
```json
{
  "status": "error",
  "results": [],
  "errors": [
    "Primary error message",
    "Secondary error if applicable"
  ],
  "execution": {
    "latency_ms": 50,
    "result_count": 0,
    "threshold_applied": 0.0
  }
}
```

---

## API Contract Versions

**Current Version**: 1.0 (2025-12-16)

**Compatibility**:
- Backward compatible: New optional fields may be added
- Not backward compatible: Removing fields or changing field types requires version bump
- Plan for v2 if significant changes needed

**Example v1 → v2 scenario**:
- Add support for multiple queries in one request
- Change similarity_score to include confidence intervals
- Support multiple embedding models (not just Cohere)
