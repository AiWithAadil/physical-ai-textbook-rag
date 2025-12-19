"""RAG Agent - Retrieval-Augmented Generation Agent Implementation.

This module provides the core RAGAgent class that orchestrates the complete
RAG pipeline: query validation, retrieval from Qdrant, context formatting,
and answer generation using Gemini LLM.

The agent integrates with:
- Cohere Embeddings (via RetrievalService)
- Qdrant Vector Database (via RetrievalService)
- Google Generative AI (Gemini API)
"""

# Add these imports
import sys
sys.path.append('.')  # Add current directory to path

from src.services.retrieval_service import RetrievalService
from src.services.qdrant_client import QdrantService
from src.services.embedding_service import EmbeddingService

import asyncio
import logging
import time
import os
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================


class RAGAgentResponse(BaseModel):
    """Structured response from RAG agent."""

    answer: str = Field(..., description="Generated answer from Gemini")
    sources: List[str] = Field(
        default_factory=list, description="Source URLs from retrieved chunks"
    )
    matched_chunks: List[Dict] = Field(
        default_factory=list, description="Retrieved chunks with metadata"
    )
    execution_metadata: Dict = Field(
        default_factory=dict, description="Execution metrics and statistics"
    )
    error: Optional[str] = Field(default=None, description="Error message if applicable")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "answer": "The RAG agent retrieves documents and uses Gemini to generate answers.",
                "sources": ["https://example.com/doc1", "https://example.com/doc2"],
                "matched_chunks": [
                    {
                        "rank": 1,
                        "text": "Sample chunk text...",
                        "similarity_score": 0.92,
                        "source": "https://example.com/doc1",
                    }
                ],
                "execution_metadata": {
                    "latency_ms": 1250,
                    "chunk_count": 3,
                    "token_usage": {"input_tokens": 256, "output_tokens": 128},
                },
                "error": None,
            }
        }


class QueryRequest(BaseModel):
    """Request model for /ask endpoint."""
    query: str = Field(..., description="User question")
    top_k: Optional[int] = Field(default=5, description="Number of chunks to retrieve")
    threshold: Optional[float] = Field(default=0.6, description="Similarity threshold")


# ============================================================================
# Exception Classes
# ============================================================================


class QueryError(Exception):
    """Raised when query validation fails."""
    pass


class RetrievalError(Exception):
    """Raised when retrieval from Qdrant/Cohere fails."""
    pass


class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded."""
    pass


class LLMUnexpectedError(LLMError):
    """Raised for unexpected LLM API errors."""
    pass


# ============================================================================
# RAG Agent Class
# ============================================================================


class RAGAgent:
    """Retrieval-Augmented Generation Agent.

    Orchestrates the RAG pipeline: query validation, retrieval, context
    formatting, and answer generation using Gemini LLM.
    """

    def __init__(
        self,
        retrieval_service=None,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 30,
        gemini_api_key: Optional[str] = None,
    ):
        """Initialize RAG Agent.

        Args:
            retrieval_service: RetrievalService instance (for embedding + search)
            model: Gemini model name (default: gemini-1.5-flash)
            temperature: LLM temperature for response generation
            max_tokens: Maximum tokens in LLM response
            timeout: Request timeout in seconds
            gemini_api_key: Gemini API key (if not provided, uses env variable)

        Raises:
            LLMError: If Gemini client initialization fails
        """
        self.retrieval_service = retrieval_service
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # Initialize Gemini client
        try:
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
            elif not genai:
                raise LLMUnexpectedError(
                    "google.generativeai not installed. "
                    "Install with: pip install google-generativeai"
                )
            self.gemini_client = genai
            logger.info(
                f"RAGAgent initialized with model={model}, "
                f"temperature={temperature}, max_tokens={max_tokens}, timeout={timeout}s"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            raise LLMUnexpectedError(f"Gemini initialization failed: {str(e)}")

    async def answer(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.6,
    ) -> RAGAgentResponse:
        """Generate an answer to a query using RAG.

        Args:
            query: User question/query
            top_k: Number of chunks to retrieve (default: 5)
            threshold: Similarity score threshold (default: 0.6)

        Returns:
            RAGAgentResponse with answer, sources, and matched_chunks

        Raises:
            QueryError: If query validation fails
            RetrievalError: If retrieval fails
            LLMError: If LLM generation fails
        """
        start_time = time.time()

        try:
            # Validate query
            self._validate_query(query)

            # Retrieve relevant chunks
            logger.info(f"Retrieving chunks for query: {query[:100]}...")
            retrieved_results = await self._retrieve(query, top_k, threshold)

            # Format context from retrieved chunks
            context = self._format_context(retrieved_results)

            # Generate answer using Gemini
            logger.info("Generating answer with Gemini...")
            answer_text = await self._generate_answer(query, context)

            # Extract sources from retrieved results
            sources = self._extract_sources(retrieved_results)

            # Format matched chunks for response
            matched_chunks = self._format_matched_chunks(retrieved_results)

            # Calculate execution metadata
            latency_ms = int((time.time() - start_time) * 1000)
            execution_metadata = {
                "latency_ms": latency_ms,
                "chunk_count": len(retrieved_results),
                "top_k": top_k,
                "threshold": threshold,
            }

            logger.info(
                f"Answer generated successfully in {latency_ms}ms "
                f"using {len(retrieved_results)} chunks"
            )

            return RAGAgentResponse(
                answer=answer_text,
                sources=sources,
                matched_chunks=matched_chunks,
                execution_metadata=execution_metadata,
                error=None,
            )

        except QueryError as e:
            logger.error(f"Query validation error: {str(e)}")
            raise

        except RetrievalError as e:
            logger.error(f"Retrieval error: {str(e)}")
            # Graceful degradation - return response with no results
            latency_ms = int((time.time() - start_time) * 1000)
            return RAGAgentResponse(
                answer="I don't have enough information to answer this query.",
                sources=[],
                matched_chunks=[],
                execution_metadata={"latency_ms": latency_ms},
                error=f"Retrieval failed: {str(e)}",
            )

        except LLMError as e:
            logger.error(f"LLM error: {str(e)}")
            latency_ms = int((time.time() - start_time) * 1000)
            return RAGAgentResponse(
                answer="Failed to generate answer due to LLM error.",
                sources=[],
                matched_chunks=[],
                execution_metadata={"latency_ms": latency_ms},
                error=f"LLM error: {str(e)}",
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            latency_ms = int((time.time() - start_time) * 1000)
            return RAGAgentResponse(
                answer="An unexpected error occurred.",
                sources=[],
                matched_chunks=[],
                execution_metadata={"latency_ms": latency_ms},
                error=f"Unexpected error: {str(e)}",
            )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    async def _retry_with_backoff(
        self,
        func,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
    ):
        """Retry a function with exponential backoff."""
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_retries + 1}")
                return await func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    is_rate_limit = "429" in str(e) or "rate" in str(e).lower()
                    if is_rate_limit:
                        delay = min(delay * backoff_factor, max_delay)
                        logger.warning(
                            f"Rate limited, retrying in {delay}s... "
                            f"({attempt + 1}/{max_retries})"
                        )
                    else:
                        delay = min(delay * backoff_factor, max_delay)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {str(e)}, "
                            f"retrying in {delay}s..."
                        )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_retries + 1} retries failed")

        raise last_exception or LLMUnexpectedError("Retry failed with unknown error")

    def _validate_query(self, query: str) -> None:
        """Validate query input."""
        if not query or not query.strip():
            raise QueryError("Query cannot be empty")

        if len(query) > 10000:
            logger.warning(f"Query length {len(query)} exceeds 10k chars, truncating")

    async def _retrieve(self, query: str, top_k: int, threshold: float) -> List[Dict]:
        """Retrieve relevant chunks from Qdrant."""
        try:
            if not self.retrieval_service:
                raise RetrievalError("RetrievalService not initialized")

            from src.models.search_query import SearchQuery

            search_query = SearchQuery(
                query_text=query, top_k=top_k, similarity_threshold=threshold
            )

            logger.info(f"Retrieving up to {top_k} chunks with threshold {threshold}")
            response = await self.retrieval_service.search(search_query)

            if response.status == "error":
                raise RetrievalError(f"Retrieval error: {response.errors}")

            results = []
            for result in response.results:
                results.append(
                    {
                        "rank": result.rank,
                        "text": result.text,
                        "similarity_score": result.similarity_score,
                        "metadata": result.metadata.dict() if result.metadata else {},
                    }
                )

            logger.info(f"Retrieved {len(results)} chunks")
            return results

        except RetrievalError:
            raise
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            raise RetrievalError(f"Failed to retrieve chunks: {str(e)}")

    def _format_context(self, results: List[Dict]) -> str:
        """Format retrieved chunks into context string."""
        if not results:
            return "No relevant context found."

        context_parts = ["Retrieved Context:"]
        for item in results:
            rank = item.get("rank", "?")
            text = item.get("text", "")
            score = item.get("similarity_score", 0.0)
            metadata = item.get("metadata", {})
            source = metadata.get("url") or metadata.get("source", "unknown")

            context_parts.append(
                f"\n[{rank}] \"{text[:200]}...\" "
                f"(Source: {source} | Score: {score:.2f})"
            )

        context = "\n".join(context_parts)
        logger.info(f"Formatted context from {len(results)} chunks")
        return context

    def _construct_system_prompt(self) -> str:
        """Construct the system prompt for Gemini."""
        return (
            "You are a helpful assistant that answers questions based on provided context.\n\n"
            "Instructions:\n"
            "1. Answer the user's question using ONLY the provided context\n"
            "2. If the context doesn't contain relevant information, say "
            "'I don\\'t have enough information to answer this'\n"
            "3. Always cite your sources by including [Source: URL] references\n"
            "4. Keep answers concise and focused\n"
        )

    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using Gemini LLM."""
        try:
            if not self.gemini_client:
                raise LLMUnexpectedError("Gemini client not initialized")

            system_prompt = self._construct_system_prompt()
            full_prompt = f"{system_prompt}\n\n{context}\n\nUser Query: {query}"

            async def _call_gemini():
                logger.debug("Calling Gemini API...")
                model = self.gemini_client.GenerativeModel(self.model)
                response = await asyncio.to_thread(
                    model.generate_content,
                    full_prompt,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )
                return response.text

            answer_text = await asyncio.wait_for(
                self._retry_with_backoff(_call_gemini), timeout=self.timeout
            )

            logger.info("Answer generated successfully")
            return answer_text

        except asyncio.TimeoutError:
            logger.error(f"Gemini request timed out after {self.timeout}s")
            raise LLMTimeoutError(f"Gemini request timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise LLMUnexpectedError(f"Failed to generate answer: {str(e)}")

    def _extract_sources(self, results: List[Dict]) -> List[str]:
        """Extract unique source URLs from results."""
        sources = set()
        for item in results:
            metadata = item.get("metadata", {})
            source = metadata.get("url") or metadata.get("source")
            if source:
                sources.add(source)

        return sorted(list(sources))

    def _format_matched_chunks(self, results: List[Dict]) -> List[Dict]:
        """Format retrieved chunks for response."""
        formatted = []
        for item in results:
            formatted.append(
                {
                    "rank": item.get("rank", 0),
                    "text": item.get("text", ""),
                    "similarity_score": item.get("similarity_score", 0.0),
                    "source": (
                        item.get("metadata", {}).get("url")
                        or item.get("metadata", {}).get("source")
                        or "unknown"
                    ),
                    "metadata": item.get("metadata", {}),
                }
            )

        return formatted

    async def disconnect(self) -> None:
        """Disconnect from services."""
        logger.info("Disconnecting RAG Agent")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="RAG Agent API",
    description="Retrieval-Augmented Generation API with Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "RAG Agent API is operational",
        "version": "1.0.0"
    }


@app.post("/ask", response_model=RAGAgentResponse)
async def ask_endpoint(request: QueryRequest):
    """Ask a question to the RAG agent.
    
    Args:
        request: QueryRequest with query text and optional parameters
        
    Returns:
        RAGAgentResponse with answer, sources, and matched chunks
    """
    try:
        # Get API keys from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")
        
        if not gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not found in environment variables"
            )
        
        # Initialize services
        qdrant_service = QdrantService(url=qdrant_url, api_key=qdrant_api_key)
        embedding_service = EmbeddingService(api_key=cohere_api_key)
        retrieval_service = RetrievalService(
            qdrant_service=qdrant_service,
            embedding_service=embedding_service,
            collection_name="rag_embedding"  # Your collection name from embedding pipeline
        )
        
        # Initialize RAG Agent with retrieval service
        agent = RAGAgent(
            retrieval_service=retrieval_service,
            gemini_api_key=gemini_api_key
        )
        
        # Generate answer
        response = await agent.answer(
            query=request.query,
            top_k=request.top_k,
            threshold=request.threshold
        )
        
        return response
        
    except QueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)