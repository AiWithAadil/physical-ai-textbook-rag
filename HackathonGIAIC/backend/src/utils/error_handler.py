"""Error handling utilities for Retrieval Service."""

import logging
from typing import Any, Dict, Optional

from src.utils.exceptions import RetrievalServiceException

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response."""

    def __init__(
        self,
        status: str = "error",
        errors: Optional[list[str]] = None,
        query: str = "",
    ):
        """Initialize error response."""
        self.status = status
        self.errors = errors or []
        self.query = query
        self.results = []
        self.execution = {
            "latency_ms": 0,
            "result_count": 0,
            "threshold_applied": 0.0,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "status": self.status,
            "results": self.results,
            "execution": self.execution,
            "errors": self.errors,
        }


def handle_exception(
    exc: Exception, query: str = "", logger_obj: Optional[logging.Logger] = None
) -> ErrorResponse:
    """Handle exception and return error response."""
    if logger_obj is None:
        logger_obj = logger

    error_response = ErrorResponse(query=query)

    if isinstance(exc, RetrievalServiceException):
        logger_obj.error(f"Service error: {str(exc)}")
        error_response.errors.append(str(exc))
    else:
        logger_obj.error(f"Unexpected error: {str(exc)}", exc_info=True)
        error_response.errors.append("Internal server error")

    return error_response
