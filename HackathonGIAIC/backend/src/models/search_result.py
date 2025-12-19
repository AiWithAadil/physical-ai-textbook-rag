"""Search result models."""

from typing import List

from pydantic import BaseModel, Field

from src.models.metadata import ChunkMetadata


class SearchResult(BaseModel):
    """Single search result."""

    rank: int = Field(..., ge=1, description="Rank in result set (1-indexed)")
    text: str = Field(..., min_length=1, description="Retrieved chunk text")
    similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Cosine similarity score"
    )
    metadata: ChunkMetadata = Field(..., description="Source metadata")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rank": 1,
                "text": "To set up a vector database, first install...",
                "similarity_score": 0.92,
                "metadata": {
                    "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                    "url": "https://docs.example.com/guide/setup",
                    "position": 245,
                    "timestamp": "2025-12-15T10:30:00Z",
                    "document_title": "Vector Database Setup Guide",
                },
            }
        }
