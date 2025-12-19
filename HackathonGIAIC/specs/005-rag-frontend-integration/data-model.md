# Data Model: RAG Agent Frontend Integration

## Frontend State Models

### ChatState
- `inputValue: string` - Current value in the question input field
- `isLoading: boolean` - Whether the backend is processing a request
- `response: RAGAgentResponse | null` - The most recent response from the backend
- `error: string | null` - Any error message to display
- `isChatOpen: boolean` - Whether the chat widget is expanded or minimized

### RAGAgentResponse (Backend Response Model)
- `answer: string` - The generated answer from the RAG agent
- `sources: Array<string>` - List of source URLs from retrieved chunks
- `matched_chunks: Array<MatchedChunk>` - Text chunks that were matched and used
- `execution_metadata: ExecutionMetadata` - Execution metrics and statistics
- `error: string | null` - Error message if applicable

### MatchedChunk
- `rank: number` - Rank of the chunk in the retrieval results
- `text: string` - The text content of the matched chunk
- `similarity_score: number` - How similar this chunk was to the query (0-1)
- `source: string` - Source of the chunk
- `metadata: Object` - Additional metadata about the chunk

### ExecutionMetadata
- `latency_ms: number` - Processing time in milliseconds
- `chunk_count: number` - Number of chunks retrieved
- `top_k: number` - Number of chunks requested
- `threshold: number` - Similarity threshold used

## Frontend UI Elements

### ChatWidgetProps
- `backendUrl: string` - Base URL for the backend RAG API
- `initiallyOpen: boolean` - Whether the widget should start open or minimized

### API Request Models
- `query: string` - The user's question to send to the RAG agent
- `top_k: number` - Number of chunks to retrieve (default: 5)
- `threshold: number` - Similarity score threshold (default: 0.6)

## API Contracts

### GET /ask
- **Request Parameters**:
  - `query: string` (required) - The question to ask the RAG Agent
  - `top_k: number` (optional) - Number of chunks to retrieve (default: 5)
  - `threshold: number` (optional) - Similarity score threshold (default: 0.6)
- **Response**: `RAGAgentResponse` object with answer, sources, and matched chunks

### POST /ask
- **Request Body**:
  - `query: string` (required) - The question to ask the RAG Agent
  - `top_k: number` (optional) - Number of chunks to retrieve (default: 5)
  - `threshold: number` (optional) - Similarity score threshold (default: 0.6)
- **Response**: `RAGAgentResponse` object with answer, sources, and matched chunks

### GET /health
- **Response**: Health check object with status and timestamp

## Validation Rules

### Input Validation
- `inputValue` must be non-empty before submitting
- `inputValue` length should be reasonable (e.g., less than 10000 characters)
- `top_k` should be between 1 and 20
- `threshold` should be between 0.0 and 1.0

### Response Validation
- `answer` field must be present in backend response
- `sources` and `matched_chunks` must be arrays (empty if no results)
- Each matched chunk must have `rank`, `text`, `similarity_score`, and `source`

## State Transitions

### Chat Widget States
1. **Minimized** → User clicks widget → **Expanded**
2. **Expanded** → User submits query → **Loading**
3. **Loading** → Response received → **Response Display**
4. **Response Display** → User submits new query → **Loading**
5. **Loading** → Error occurs → **Error Display**
6. **Any State** → User clicks minimize → **Minimized**

### Loading State Transitions
- `isLoading` starts as `false`
- When query is submitted → `isLoading` becomes `true`
- When response is received → `isLoading` becomes `false`
- When error occurs → `isLoading` becomes `false`