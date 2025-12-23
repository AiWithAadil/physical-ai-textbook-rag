"""Core retrieval service for semantic search."""

import logging
import time
from datetime import datetime
from typing import List, Optional

from src.models.metadata import ChunkMetadata, ExecutionMetadata
from src.models.response import RetrievalResponse
from src.models.search_query import SearchQuery
from src.models.search_result import SearchResult
from src.services.embedding_service import EmbeddingService
from src.services.qdrant_client import QdrantService
from src.utils.exceptions import QueryValidationError, EmbeddingError, QdrantError
from src.utils.validators import validate_query

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for semantic search and retrieval."""

    def __init__(
        self,
        qdrant_service: Optional[QdrantService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        collection_name: str = "documents",
    ):
        """Initialize retrieval service.

        Args:
            qdrant_service: Qdrant service instance
            embedding_service: Embedding service instance
            collection_name: Qdrant collection name
        """
        self.qdrant_service = qdrant_service or QdrantService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.collection_name = collection_name

    async def search(self, query: SearchQuery) -> RetrievalResponse:
        """Execute semantic search.

        Args:
            query: Search query

        Returns:
            RetrievalResponse with results

        Raises:
            QueryValidationError: If query is invalid
            EmbeddingError: If embedding fails
            QdrantError: If Qdrant search fails
        """
        start_time = time.time()
        query_embedded_at = datetime.utcnow().isoformat() + "Z"

        try:
            # Validate query
            validate_query(
                query.query_text,
                query.top_k,
                query.similarity_threshold,
            )
            logger.info(f"Searching for: {query.query_text}")

            # Connect to Qdrant if needed
            if not self.qdrant_service.client:
                await self.qdrant_service.connect()

            # Generate embedding for query
            logger.debug("Embedding query...")
            query_vector = self.embedding_service.embed_query(query.query_text)
            logger.debug(f"Query embedded (vector size: {len(query_vector)})")

            # Search in Qdrant
            logger.debug(f"Searching Qdrant with top_k={query.top_k}")
            search_start = time.time()
            qdrant_results = await self.qdrant_service.search(
                collection_name=self.collection_name,
                vector=query_vector,
                limit=query.top_k,
                score_threshold=query.similarity_threshold,
            )
            qdrant_query_time = int((time.time() - search_start) * 1000)

            # Format results
            results = self._format_results(qdrant_results)

            # Calculate total latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Build response
            execution = ExecutionMetadata(
                latency_ms=latency_ms,
                result_count=len(results),
                threshold_applied=query.similarity_threshold,
                query_embedded_at=query_embedded_at,
                qdrant_query_time_ms=qdrant_query_time,
            )

            response = RetrievalResponse(
                query=query.query_text,
                status="success",
                results=results,
                execution=execution,
                errors=[],
            )

            logger.info(
                f"Search completed: {len(results)} results in {latency_ms}ms"
            )
            return response

        except (QueryValidationError, EmbeddingError, QdrantError) as e:
            logger.error(f"Search error: {str(e)}")
            latency_ms = int((time.time() - start_time) * 1000)
            execution = ExecutionMetadata(
                latency_ms=latency_ms,
                result_count=0,
                threshold_applied=query.similarity_threshold,
                query_embedded_at=query_embedded_at,
            )
            return RetrievalResponse(
                query=query.query_text,
                status="error",
                results=[],
                execution=execution,
                errors=[str(e)],
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            latency_ms = int((time.time() - start_time) * 1000)
            execution = ExecutionMetadata(
                latency_ms=latency_ms,
                result_count=0,
                threshold_applied=query.similarity_threshold,
            )
            return RetrievalResponse(
                query=query.query_text,
                status="error",
                results=[],
                execution=execution,
                errors=["Internal server error"],
            )

    def _format_results(self, qdrant_results: List) -> List[SearchResult]:
        """Format Qdrant results.

        Args:
            qdrant_results: Raw Qdrant results

        Returns:
            List of SearchResult objects
        """
        results = []
        for rank, result in enumerate(qdrant_results, 1):
            try:
                # Extract metadata from payload
                payload = result.payload or {}

                # Handle different field names that might be in the payload
                # Prioritize content field if available (as seen in your Qdrant data)
                text_content = payload.get("content", "") or payload.get("text", "")

                # Handle timestamp field - convert from float (Unix timestamp) to ISO string if needed
                timestamp_value = payload.get("created_at", payload.get("timestamp"))
                if timestamp_value is not None:
                    # Check if it's a float (Unix timestamp) and convert to ISO string
                    if isinstance(timestamp_value, float):
                        import datetime
                        timestamp_value = datetime.datetime.fromtimestamp(timestamp_value, tz=datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
                    elif isinstance(timestamp_value, int):
                        import datetime
                        timestamp_value = datetime.datetime.fromtimestamp(timestamp_value, tz=datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

                # Create metadata with flexible field mapping
                metadata = ChunkMetadata(
                    chunk_id=payload.get("original_chunk_id", payload.get("chunk_id", "")),
                    url=payload.get("source_url", payload.get("url", "")),
                    position=payload.get("position"),
                    timestamp=timestamp_value,
                    document_title=payload.get("title", payload.get("document_title")),
                )

                # Create search result with proper text field
                search_result = SearchResult(
                    rank=rank,
                    text=text_content,
                    similarity_score=result.score or 0.0,
                    metadata=metadata,
                )
                results.append(search_result)
            except Exception as e:
                logger.error(f"Error formatting result: {str(e)}")
                continue

        return results

    async def disconnect(self) -> None:
        """Disconnect from Qdrant."""
        await self.qdrant_service.disconnect()
