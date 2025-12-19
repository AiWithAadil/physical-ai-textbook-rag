"""Response models."""

from typing import List, Literal

from pydantic import BaseModel, Field

from src.models.metadata import ExecutionMetadata
from src.models.search_result import SearchResult


class RetrievalResponse(BaseModel):
    """Complete retrieval response."""

    query: str = Field(..., description="Echo of original query")
    status: Literal["success", "error"] = Field(..., description="Request status")
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    execution: ExecutionMetadata = Field(..., description="Execution metadata")
    errors: List[str] = Field(default_factory=list, description="Error messages")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "query": "How do I set up a vector database?",
                "status": "success",
                "results": [],
                "execution": {
                    "latency_ms": 145,
                    "result_count": 0,
                    "threshold_applied": 0.7,
                },
                "errors": [],
            }
        }
