"""Validation utilities for Retrieval Service."""

import logging
from typing import Optional

from src.utils.exceptions import QueryValidationError

logger = logging.getLogger(__name__)


def validate_query(
    query_text: str,
    top_k: Optional[int] = None,
    similarity_threshold: Optional[float] = None,
) -> None:
    """Validate query parameters.

    Args:
        query_text: Search query text
        top_k: Number of top results to return
        similarity_threshold: Minimum similarity score filter

    Raises:
        QueryValidationError: If validation fails
    """
    # Validate query text
    if not query_text or not query_text.strip():
        raise QueryValidationError("query_text cannot be empty")

    if len(query_text) > 10000:
        raise QueryValidationError("query_text cannot exceed 10000 characters")

    # Validate top_k
    if top_k is not None:
        if top_k < 1 or top_k > 1000:
            raise QueryValidationError(
                f"top_k must be between 1 and 1000, got {top_k}"
            )

    # Validate similarity_threshold
    if similarity_threshold is not None:
        if similarity_threshold < 0.0 or similarity_threshold >= 1.0:
            raise QueryValidationError(
                f"similarity_threshold must be between 0.0 and 1.0, got {similarity_threshold}"
            )


def validate_chunk_metadata(
    chunk_id: str, url: str, text: str
) -> None:
    """Validate chunk metadata.

    Args:
        chunk_id: Chunk identifier
        url: Source URL
        text: Chunk text

    Raises:
        QueryValidationError: If validation fails
    """
    if not chunk_id:
        raise QueryValidationError("chunk_id cannot be empty")

    if not url:
        raise QueryValidationError("url cannot be empty")

    if not text:
        raise QueryValidationError("text cannot be empty")
