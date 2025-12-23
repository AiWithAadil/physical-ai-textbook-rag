# Implementation Plan: RAG Agent with Retrieval Integration

**Feature Branch**: `004-rag-agent`
**Created**: 2025-12-16
**Status**: Draft
**Specification**: [spec.md](./spec.md)

---

## Executive Summary

This plan details the implementation of a RAG (Retrieval-Augmented Generation) Agent backend that integrates OpenRouter LLM, Cohere embeddings, and Qdrant vector storage. The implementation focuses on the agent logic layer (`backend/agent.py`) that orchestrates query processing, retrieval, and answer generation - no FastAPI endpoint layer in this phase.

**Key Deliverable**: `backend/agent.py` - A pure agent implementation using openai library with OpenRouter as the LLM provider.

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  RAG Agent (backend/agent.py)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ RAGAgent Class                               │  │
│  │  - Initialization with services              │  │
│  │  - Query processing pipeline                 │  │
│  │  - Context assembly from retrieved chunks    │  │
│  │  - LLM prompt engineering                    │  │
│  │  - Error handling & graceful degradation     │  │
│  └──────────────────────────────────────────────┘  │
│         ↓                    ↓                      │
│  ┌──────────────┐   ┌───────────────┐             │
│  │ Retrieval    │   │ OpenRouter    │             │
│  │ Service      │   │ LLM (via      │             │
│  │ (embedding + │   │  openai)      │             │
│  │  Qdrant)     │   │               │             │
│  └──────────────┘   └───────────────┘             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: User query string
2. **Retrieval**:
   - Query validated
   - Cohere embedding generated
   - Qdrant similarity search → top-k chunks retrieved
3. **Context Assembly**:
   - Retrieved chunks formatted with metadata
   - Context string constructed
4. **LLM Processing**:
   - Prompt engineered with context + query
   - Sent to OpenRouter API
   - Response generated
5. **Output**: Structured response with answer, sources, matched_chunks

### Integration Points

The agent integrates with existing backend services:

- **RetrievalService** (`src/services/retrieval_service.py`): Orchestrates embedding + search
- **EmbeddingService** (`src/services/embedding_service.py`): Cohere embeddings
- **QdrantService** (`src/services/qdrant_client.py`): Vector store access
- **Models**: Pydantic models for type safety and validation

---

## Design Decisions

### 1. Agent Framework Choice: Pure OpenRouter Integration (Not OpenAI Agents SDK)

**Decision**: Use `openai` library directly instead of OpenAI Agents SDK

**Rationale**:
- OpenAI Agents SDK is optimized for OpenAI LLMs; using OpenRouter requires workarounds
- `openai` library has native support for function calling and tool use
- Simpler, more direct integration with fewer abstractions
- OpenRouter API is production-ready and fully supports the RAG pattern
- Reduces dependency bloat and deployment complexity

**Trade-off**: Less framework abstraction, but gains clarity and direct control over LLM interactions

### 2. OpenRouter Configuration

**Model**: `mistralai/devstral-2512:free` (default)
- Fast inference for RAG scenarios
- Cost-effective
- Supports large context windows

**Configuration**:
- API key from environment: `OPENROUTER_API_KEY`
- Base URL: `https://openrouter.ai/api/v1`
- Temperature: 0.7 (balanced between creativity and consistency)
- Max tokens: 1024 (reasonable for RAG answers)
- Timeout: 30 seconds with retry logic

### 3. Retrieval Pipeline

**Top-k chunks**: 5 (configurable)
- Balance between context richness and token efficiency
- Gemini's large context window allows this without issues

**Similarity threshold**: 0.6 (configurable)
- Filters low-relevance results
- Improves answer quality

**Chunk formatting in context**:
```
Retrieved Context:
[1] "chunk_text" (Source: url | Position: 245 | Score: 0.92)
[2] "chunk_text" (Source: url | Position: 512 | Score: 0.88)
...
```

### 4. Error Handling Strategy

| Scenario | Response | HTTP Status (Future) |
|----------|----------|---------------------|
| Empty/missing query | QueryError exception | 400 |
| Query too long (>10k chars) | Truncate + warn in response | 200 |
| No search results | Answer: "No relevant documents found" | 200 |
| Cohere embedding fails | EmbeddingError exception | 503 |
| Qdrant unavailable | QdrantError exception | 503 |
| OpenRouter API fails | LLMError exception | 503 |
| OpenRouter rate limited | Retry with exponential backoff | 429 |
| Timeout (>30s) | Return best-effort partial response | 504 |

### 5. Prompt Engineering

**System Prompt Template**:
```
You are a helpful assistant that answers questions based on provided context.

Instructions:
1. Answer the user's question using ONLY the provided context
2. If the context doesn't contain relevant information, say "I don't have enough information to answer this"
3. Always cite your sources by including [Source: URL] references
4. Keep answers concise and focused

Retrieved Context:
{context}

User Query:
{query}
```

**Why this approach**:
- Explicitly constrains LLM to use provided context (reduces hallucination)
- Enforces source attribution (improves traceability)
- Clear instructions prevent off-topic responses

---

## Implementation Phases

### Phase 1: Core Agent Implementation (This PR)

**File**: `backend/agent.py`

**Components**:
1. **RAGAgent class** - Main orchestrator
   - Constructor: Initialize services, OpenRouter client, configuration
   - `answer(query: str) -> RAGAgentResponse` - Main entry point
   - `_retrieve(query: str) -> List[SearchResult]` - Wrapper around RetrievalService
   - `_format_context(results: List[SearchResult]) -> str` - Format chunks for LLM
   - `_generate_answer(query: str, context: str) -> str` - Call OpenRouter
   - Error handling throughout

2. **Data Models** - Response structure
   - `RAGAgentResponse` (Pydantic):
     - `answer: str`
     - `sources: List[str]` (URLs from retrieved chunks)
     - `matched_chunks: List[Dict]` (chunk text + metadata)
     - `execution_metadata: Dict` (latency, token counts, etc.)
     - `error: Optional[str]` (if applicable)

3. **Configuration**
   - Add `OPENROUTER_API_KEY` to `src/config.py`
   - Add `OPENROUTER_MODEL`, `OPENROUTER_TEMPERATURE`, `OPENROUTER_MAX_TOKENS`, `OPENROUTER_TIMEOUT`, `OPENROUTER_BASE_URL` (with defaults)

4. **Dependencies**
   - Add `openai>=1.0.0` to `requirements.txt`

### Phase 2: FastAPI Integration (Future PR)

**File**: `backend/src/api/ask.py` or similar

- Create `/ask` endpoint that wraps `RAGAgent.answer()`
- Request validation (query parameter)
- Response mapping to HTTP 200/400/503
- Logging and metrics

### Phase 3: Testing & Deployment (Future PR)

- Unit tests: Agent logic, error paths, prompt formatting
- Integration tests: Full workflow with real Qdrant/Cohere
- Performance tests: Latency, token usage
- Deployment configuration

---

## Key Files

### New/Modified

| File | Type | Status | Purpose |
|------|------|--------|---------|
| `backend/agent.py` | NEW | This PR | Core RAG agent implementation |
| `backend/src/config.py` | MODIFY | This PR | Add Gemini configuration |
| `backend/requirements.txt` | MODIFY | This PR | Add google-generativeai |
| `backend/.env` | MODIFY | This PR | Add GEMINI_API_KEY (already provided in spec) |
| `specs/004-rag-agent/plan.md` | NEW | This PR | Implementation plan |

### Reused (No Changes)

- `backend/src/services/retrieval_service.py` - Used as-is
- `backend/src/services/embedding_service.py` - Used as-is
- `backend/src/services/qdrant_client.py` - Used as-is
- `backend/src/models/search_result.py` - Used as-is
- `backend/src/models/metadata.py` - Used as-is

---

## API Contract

### RAGAgent Class

```python
class RAGAgent:
    def __init__(
        self,
        retrieval_service: RetrievalService = None,
        model: str = "mistralai/devstral-2512:free",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        """Initialize RAG Agent."""

    async def answer(self, query: str, top_k: int = 5, threshold: float = 0.6) -> RAGAgentResponse:
        """
        Generate an answer to a query using retrieval-augmented generation.

        Args:
            query: User question
            top_k: Number of chunks to retrieve
            threshold: Similarity score threshold

        Returns:
            RAGAgentResponse with answer, sources, and matched_chunks

        Raises:
            QueryError: If query is empty or invalid
            RetrievalError: If retrieval fails
            LLMError: If OpenRouter API fails
        """
```

### RAGAgentResponse Model

```python
class RAGAgentResponse(BaseModel):
    answer: str  # Generated answer from LLM
    sources: List[str]  # List of source URLs
    matched_chunks: List[Dict]  # List of retrieved chunks with metadata
    execution_metadata: Dict  # Latency, token counts, etc.
    error: Optional[str] = None  # Error message if applicable
```

---

## Error Handling

### Exception Hierarchy

```
BaseException
├── QueryError (empty/invalid query)
├── RetrievalError (embedding/Qdrant failure)
├── LLMError (OpenRouter API failure)
│   ├── LLMTimeoutError (request timeout)
│   ├── LLMRateLimitError (quota exceeded)
│   └── LLMUnexpectedError (other failures)
└── AgentError (orchestration failure)
```

### Retry Logic

- **OpenRouter API failures**: Retry 3x with exponential backoff (1s, 2s, 4s)
- **Rate limits (429)**: Retry with longer backoff (10s, 30s, 60s)
- **Timeouts**: Return best-effort response with partial context

### Graceful Degradation

- No results from retrieval → Return message: "I don't have enough information..."
- OpenRouter timeout → Return retrieved chunks as-is with explanation
- Context truncation → Warn in response but continue processing

---

## Configuration

### Environment Variables (in `.env`)

```env
# Existing
QDRANT_URL=https://fa01c593-...
QDRANT_API_KEY=eyJhbGc...
COHERE_API_KEY=O9iwwwjk3q...

# New for OpenRouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=mistralai/devstral-2512:free
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_MAX_TOKENS=1024
OPENROUTER_TIMEOUT=30
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Python Configuration (in `src/config.py`)

```python
class Config:
    # ... existing config ...

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
    OPENROUTER_TEMPERATURE: float = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "1024"))
    OPENROUTER_TIMEOUT: int = int(os.getenv("OPENROUTER_TIMEOUT", "30"))
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
```

---

## Dependencies

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `openai` | >=1.0.0 | OpenRouter API client |
| `tenacity` | >=8.2.0 | Retry logic (already in requirements) |

### Existing Dependencies Used

| Package | Purpose |
|---------|---------|
| `qdrant-client` | Vector store access |
| `cohere` | Query embeddings |
| `pydantic` | Data validation |
| `python-dotenv` | Environment config |

---

## Testing Strategy

### Unit Tests

1. **Agent initialization**: Verify services are configured
2. **Query validation**: Test empty/invalid inputs
3. **Context formatting**: Verify chunk formatting with metadata
4. **Prompt construction**: Test system prompt + context assembly
5. **Error handling**: Test all exception paths
6. **Response formatting**: Verify RAGAgentResponse structure

### Integration Tests

1. **End-to-end workflow**: Query → retrieve → generate → response
2. **Real Qdrant integration**: Verify with actual vector store
3. **Real OpenRouter integration**: Test LLM response quality
4. **Timeout handling**: Verify retry and timeout behavior

### Performance Tests

1. **Latency**: Measure end-to-end time (target: <2s)
2. **Token usage**: Track OpenRouter token consumption
3. **Concurrency**: Test multiple simultaneous queries (target: 50 concurrent)

---

## Success Criteria (From Spec)

| Criterion | Implementation Detail |
|-----------|----------------------|
| `/ask` endpoint equivalent | RAGAgent.answer() method |
| Cohere + Qdrant integration | RetrievalService integration |
| Response format | RAGAgentResponse with answer/sources/chunks |
| Error handling | Exception hierarchy + graceful degradation |
| <2s latency (p99) | OpenRouter fast model + efficient context |
| 95% relevance | Similarity threshold + chunk selection |
| 100% proper errors | Comprehensive exception handling |
| Valid JSON | Pydantic models enforce structure |

---

## Non-Goals (Out of Scope)

- ❌ FastAPI endpoint (Phase 2)
- ❌ Authentication/authorization
- ❌ Persistent conversation history
- ❌ Advanced search features
- ❌ Frontend integration
- ❌ Deployment infrastructure

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenRouter API quota exhaustion | Service unavailability | Implement rate limiting, monitor usage, set alerts |
| Large context → token overflow | LLM errors | Implement context truncation, chunk selection optimization |
| Qdrant unavailability | Retrieval failure | Graceful error handling, retry logic, fallback messages |
| Cohere embedding variance | Inconsistent results | Version lock, similarity threshold tuning |
| Latency SLA miss | User experience | Profile and optimize, consider caching, batch queries |

---

## Architectural Decisions (ADR Candidates)

1. **Use OpenRouter instead of OpenAI SDK**: Direct integration simplifies code, reduces dependencies
2. **Sync vs Async**: Phase 1 uses async for compatibility with existing async stack
3. **Prompt engineering**: System prompt constrains hallucination, enforces source attribution
4. **Error types**: Custom exception hierarchy for precise error handling

---

## Timeline & Milestones

### Milestone 1: Core Implementation ✓
- [ ] Implement RAGAgent class
- [ ] Create RAGAgentResponse model
- [ ] Update Config with Gemini settings
- [ ] Update requirements.txt

### Milestone 2: Testing & Documentation
- [ ] Unit tests (all paths)
- [ ] Integration tests
- [ ] API documentation
- [ ] Example usage

### Milestone 3: FastAPI Integration (Phase 2)
- [ ] Create `/ask` endpoint
- [ ] Request/response mapping
- [ ] Logging and metrics

---

## Assumptions

1. Qdrant vector store is pre-populated with embedded documents
2. OpenRouter API credentials are valid and have sufficient quota
3. Network connectivity to Qdrant and OpenRouter APIs is available
4. Document chunks in Qdrant have `text` and `url` fields in payload
5. Query strings are UTF-8 encoded
6. LLM responses fit within configured max_tokens

---

## Open Questions & Decisions Needed

| Question | Current Decision | Needs Review? |
|----------|------------------|---------------|
| Should agent be sync or async? | Async for consistency with existing code | ✓ |
| Should we cache Gemini responses? | No - keep stateless for now | ✓ |
| How many retries for API failures? | 3 with exponential backoff | ✓ |
| Context window size limit? | Let Gemini handle (100k available) | ✓ |

---

## Next Steps

1. **Review & Approve Plan**: Get feedback on architecture and decisions
2. **Implement Agent**: Write `backend/agent.py` with all components
3. **Add Tests**: Comprehensive unit + integration test coverage
4. **Code Review**: Internal review before merge to main
5. **Plan Phase 2**: FastAPI endpoint integration

