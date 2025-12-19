"""Search query models."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SearchQuery(BaseModel):
    """Search query request model."""

    query_text: str = Field(
        ..., min_length=1, max_length=10000, description="Search query text"
    )
    top_k: int = Field(default=5, ge=1, le=1000, description="Number of top results")
    similarity_threshold: float = Field(
        default=0.0, ge=0.0, lt=1.0, description="Minimum similarity score filter"
    )

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, v: str) -> str:
        """Validate query text is not empty."""
        if not v.strip():
            raise ValueError("query_text cannot be empty or whitespace-only")
        return v.strip()

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "query_text": "How do I set up a vector database?",
                "top_k": 5,
                "similarity_threshold": 0.7,
            }
        }
