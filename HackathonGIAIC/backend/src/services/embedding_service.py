"""Embedding service for query vectorization."""

import logging
from typing import List

import cohere

from src.config import config
from src.utils.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Cohere."""

    def __init__(self, api_key: str = "", model: str = ""):
        """Initialize embedding service.

        Args:
            api_key: Cohere API key
            model: Model name
        """
        self.api_key = api_key or config.COHERE_API_KEY
        self.model = model or config.COHERE_MODEL
        
        if not self.api_key:
            raise EmbeddingError("COHERE_API_KEY not configured")
        
        self.client = cohere.ClientV2(api_key=self.api_key)

    def embed_query(self, query_text: str) -> List[float]:
        """Generate embedding for a query.

        Args:
            query_text: Query text to embed

        Returns:
            Embedding vector

        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            response = self.client.embed(
                texts=[query_text],
                model=self.model,
                input_type="search_query",
            )
            if response.embeddings:
    # Cohere v2 API returns embeddings differently
                if hasattr(response.embeddings, 'float_'):
                    return response.embeddings.float_[0]
                elif hasattr(response.embeddings, 'embeddings'):
                    return response.embeddings.embeddings[0]
                else:
                    return list(response.embeddings)[0]
                
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise EmbeddingError(f"Failed to embed query: {str(e)}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            EmbeddingError: If embedding fails
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type="search_document",
            )
            return response.embeddings if response.embeddings else []
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise EmbeddingError(f"Failed to embed texts: {str(e)}")
