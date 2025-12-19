"""JSON formatting utilities for responses."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def format_response(response_dict: Dict[str, Any]) -> str:
    """Format response as clean JSON.

    Args:
        response_dict: Response dictionary

    Returns:
        JSON string

    Raises:
        ValueError: If formatting fails
    """
    try:
        return json.dumps(response_dict, indent=2, default=str)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to format response: {str(e)}")
        raise ValueError(f"Failed to format response: {str(e)}")


def validate_json_response(response_dict: Dict[str, Any]) -> bool:
    """Validate response structure.

    Args:
        response_dict: Response dictionary

    Returns:
        True if valid
    """
    required_fields = ["query", "status", "results", "execution", "errors"]
    return all(field in response_dict for field in required_fields)


def format_error_response(
    query: str, errors: list[str], latency_ms: int = 0
) -> Dict[str, Any]:
    """Format error response.

    Args:
        query: Original query
        errors: List of error messages
        latency_ms: Response latency

    Returns:
        Error response dictionary
    """
    return {
        "query": query,
        "status": "error",
        "results": [],
        "execution": {
            "latency_ms": latency_ms,
            "result_count": 0,
            "threshold_applied": 0.0,
        },
        "errors": errors,
    }
