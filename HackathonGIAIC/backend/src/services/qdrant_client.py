"""Qdrant client wrapper for async operations."""

import logging
from typing import Any, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qd_models

from src.config import config
from src.utils.exceptions import QdrantConnectionError, QdrantError

logger = logging.getLogger(__name__)


class QdrantService:
    """Wrapper for Qdrant operations."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """Initialize Qdrant client.

        Args:
            url: Qdrant server URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.url = url or config.QDRANT_URL
        self.api_key = api_key or config.QDRANT_API_KEY
        self.timeout = timeout or config.QDRANT_TIMEOUT
        self.client: Optional[AsyncQdrantClient] = None

    async def connect(self) -> None:
        """Establish connection to Qdrant."""
        try:
            self.client = AsyncQdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=self.timeout,
            )
            logger.info(f"Connected to Qdrant at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise QdrantConnectionError(f"Failed to connect to Qdrant: {str(e)}")

    async def disconnect(self) -> None:
        """Close connection to Qdrant."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Qdrant")

    async def search(
        self,
        collection_name: str,
        vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """Search for similar vectors.

        Args:
            collection_name: Name of collection
            vector: Query vector
            limit: Number of results to return
            score_threshold: Minimum score filter

        Returns:
            List of search results

        Raises:
            QdrantError: If search fails
        """
        if not self.client:
            raise QdrantError("Not connected to Qdrant")

        try:
            # Use query_points method for newer versions of qdrant-client
            results = await self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                score_threshold=score_threshold,
            )
            return results.points
        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}")
            raise QdrantError(f"Qdrant search failed: {str(e)}")

    async def get_point(
        self, collection_name: str, point_id: str
    ) -> Optional[Any]:
        """Get a specific point from collection.

        Args:
            collection_name: Name of collection
            point_id: Point ID

        Returns:
            Point data or None if not found
        """
        if not self.client:
            raise QdrantError("Not connected to Qdrant")

        try:
            point = await self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=False,
            )
            return point[0] if point else None
        except Exception as e:
            logger.error(f"Failed to get point: {str(e)}")
            return None

    async def health_check(self) -> bool:
        """Check Qdrant health.

        Returns:
            True if healthy
        """
        if not self.client:
            raise QdrantError("Not connected to Qdrant")

        try:
            await self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
