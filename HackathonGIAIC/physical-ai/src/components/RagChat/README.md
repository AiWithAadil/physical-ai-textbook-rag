# RagChat Component

The RagChat component is a floating chat widget that allows users to interact with a RAG (Retrieval-Augmented Generation) Agent. It provides a seamless way for users to ask questions and receive intelligent answers based on the knowledge base.

## Features

- Floating chat widget positioned in the bottom-right corner
- Real-time communication with the RAG Agent backend
- Display of answers, sources, and matched text chunks
- Loading states and error handling
- Keyboard support (Enter to submit)
- Accessibility features with ARIA labels
- Local storage to remember widget state (open/closed)
- Retry functionality for failed requests
- Input validation with length limits

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| backendUrl | string | `process.env.REACT_APP_RAG_API_URL \|\| 'http://localhost:8000'` | The base URL for the RAG Agent API |

## Environment Variables

The component uses the following environment variable:

- `REACT_APP_RAG_API_URL` - The URL of the RAG Agent backend API (defaults to `http://localhost:8000`)

## Usage

The RagChat component is integrated into the Docusaurus site via the custom Layout wrapper at `physical-ai/src/theme/Layout.js`. It will appear on all pages automatically.

## API Endpoints Used

- `GET /ask` - Submit a query and receive an answer with sources and matched chunks
- `POST /ask` - Alternative POST endpoint for submitting queries
- `GET /health` - Check the health status of the backend service

## Data Model

The component expects responses in the following format:

```json
{
  "answer": "The generated answer from the RAG Agent",
  "sources": ["Array of source URLs"],
  "matched_chunks": [
    {
      "rank": 1,
      "text": "The text content of the matched chunk",
      "similarity_score": 0.92,
      "source": "The source of the chunk"
    }
  ],
  "execution_metadata": {
    "latency_ms": 1250,
    "chunk_count": 3
  },
  "error": null
}
```

## Error Handling

The component handles various error conditions:

- Network errors (backend unreachable)
- HTTP errors (4xx, 5xx responses)
- Invalid response formats
- Input validation errors
- Timeout errors

Users can retry failed requests using the retry button in the error message.

## Accessibility

The component includes accessibility features:

- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Focus management

## Local Storage

The component remembers its open/closed state using local storage with the key `ragChatIsOpen`.