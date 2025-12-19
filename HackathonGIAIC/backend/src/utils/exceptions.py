"""Custom exceptions for Retrieval Service."""


class RetrievalServiceException(Exception):
    """Base exception for Retrieval Service."""

    pass


class QueryValidationError(RetrievalServiceException):
    """Raised when query parameters are invalid."""

    pass


class EmbeddingError(RetrievalServiceException):
    """Raised when embedding generation fails."""

    pass


class QdrantError(RetrievalServiceException):
    """Raised when Qdrant operations fail."""

    pass


class QdrantConnectionError(QdrantError):
    """Raised when connection to Qdrant fails."""

    pass


class DataIntegrityError(RetrievalServiceException):
    """Raised when data integrity check fails."""

    pass


class ValidationError(RetrievalServiceException):
    """Raised when validation fails."""

    pass


class NotFoundError(RetrievalServiceException):
    """Raised when requested resource not found."""

    pass
