# Quickstart Guide: RAG Agent Frontend Integration

## Overview
This guide provides step-by-step instructions to set up and run the RAG Agent frontend integration with the Docusaurus site. The integration adds a chat widget in the bottom-right corner that connects to the backend RAG API.

## Prerequisites
- Node.js 16+ installed
- Python 3.9+ installed
- Backend RAG Agent service running and accessible
- Docusaurus project set up in the `physical-ai` directory

## Backend Setup
Before running the frontend, ensure the backend RAG Agent service is running:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Run the backend service:
   ```bash
   # If there's a FastAPI main file (to be created):
   uvicorn main:app --reload --port 8000
   ```

## Frontend Setup
1. Navigate to the Docusaurus project:
   ```bash
   cd physical-ai
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Environment Configuration
1. Create a `.env` file in the `physical-ai` directory:
   ```env
   REACT_APP_RAG_API_URL=http://localhost:8000
   ```

2. The API URL can be configured in the environment variable or passed as a prop to the component.

## Running the Application
1. Start the Docusaurus development server:
   ```bash
   npm run start
   ```

2. The RAG chat widget will appear in the bottom-right corner of the page and is integrated globally via the custom Layout wrapper.

## API Endpoints Used
The frontend communicates with the following backend endpoints:

- `GET /ask` - Submit a query and receive an answer with sources and matched chunks
- `POST /ask` - Alternative POST endpoint for submitting queries
- `GET /health` - Check the health status of the backend service

## Component Structure
The RAG Chat widget is implemented as a React component with the following structure:

```
physical-ai/src/components/RagChat/
├── RagChat.jsx          # Main chat component
├── RagChat.css          # Styling for the chat widget
├── api.js               # API service for backend communication
├── README.md            # Component documentation
└── RagChat.types.js     # TypeScript definitions (if needed)
```

The component is integrated globally through the Layout wrapper at `physical-ai/src/theme/Layout.js`.

## Features
The RAG Chat widget includes the following features:

- Floating chat interface in the bottom-right corner
- Input validation with length limits (max 10,000 characters)
- Real-time display of answers, sources, and matched chunks
- Loading indicators during processing
- Error handling with user-friendly messages and retry functionality
- Keyboard support (Enter to submit)
- Accessibility features (ARIA labels, roles)
- Local storage to remember widget open/closed state
- Concurrent submission prevention
- Response validation against expected data model
- Exponential backoff retry logic for failed requests

## Configuration Options
The chat widget can be configured with the following options:

- `backendUrl`: URL of the backend RAG API (default: `http://localhost:8000`)
- Environment variable `REACT_APP_RAG_API_URL` for backend URL

## Troubleshooting
1. **CORS Errors**: Ensure the backend allows requests from your frontend origin
2. **API Not Responding**: Verify the backend service is running and accessible
3. **Widget Not Appearing**: Check that the custom Layout wrapper is properly set up in `physical-ai/src/theme/Layout.js`
4. **Environment Variables**: Ensure `REACT_APP_RAG_API_URL` is set correctly in `.env` file
5. **Build Issues**: Run `npm install` to ensure all dependencies are installed

## Next Steps
1. Customize the styling to match your site's design
2. Implement analytics to track usage
3. Add more sophisticated error handling if needed
4. Review the component README in `physical-ai/src/components/RagChat/README.md` for detailed documentation