"""Metadata models."""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ChunkMetadata(BaseModel):
    """Metadata about a stored chunk."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    url: str = Field(..., description="Source document URL")
    position: Optional[int] = Field(None, ge=0, description="Position in document")
    timestamp: Optional[str] = Field(None, description="Creation timestamp (ISO 8601)")
    document_title: Optional[str] = Field(
        None, max_length=500, description="Title of source document"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://docs.example.com/guide/setup",
                "position": 245,
                "timestamp": "2025-12-15T10:30:00Z",
                "document_title": "Vector Database Setup Guide",
            }
        }


class ExecutionMetadata(BaseModel):
    """Execution metadata for a retrieval response."""

    latency_ms: int = Field(ge=0, description="Request-response latency")
    result_count: int = Field(ge=0, description="Number of results returned")
    threshold_applied: float = Field(
        ge=0.0, lt=1.0, description="Similarity threshold used"
    )
    query_embedded_at: Optional[str] = Field(None, description="When query was embedded")
    qdrant_query_time_ms: Optional[int] = Field(
        None, ge=0, description="Qdrant search time"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "latency_ms": 145,
                "result_count": 5,
                "threshold_applied": 0.7,
                "query_embedded_at": "2025-12-16T14:30:01Z",
                "qdrant_query_time_ms": 120,
            }
        }
