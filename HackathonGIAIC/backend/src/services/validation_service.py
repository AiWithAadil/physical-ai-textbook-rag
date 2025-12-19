"""Data validation service for integrity checking."""

import logging
from typing import List, Dict, Any

from pydantic import BaseModel, Field

from src.utils.exceptions import DataIntegrityError

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of chunk validation."""

    chunk_id: str = Field(..., description="Chunk ID")
    matches: bool = Field(..., description="Whether stored matches original")
    stored_text: str = Field(..., description="Text from Qdrant")
    original_text: str = Field(..., description="Original text")
    validation_passed: bool = Field(..., description="Overall validation status")
    mismatch_details: str = Field(default="", description="Details if mismatch")


class ValidationService:
    """Service for data integrity validation."""

    @staticmethod
    def validate_chunks(
        chunk_ids: List[str],
        stored_texts: List[str],
        original_texts: List[str],
    ) -> List[ValidationResult]:
        """Validate chunk integrity.

        Args:
            chunk_ids: List of chunk IDs
            stored_texts: List of stored texts
            original_texts: List of original texts

        Returns:
            List of validation results
        """
        results = []

        if not (len(chunk_ids) == len(stored_texts) == len(original_texts)):
            raise DataIntegrityError("Array lengths do not match")

        for chunk_id, stored_text, original_text in zip(
            chunk_ids, stored_texts, original_texts
        ):
            try:
                matches = stored_text == original_text
                mismatch_details = ""

                if not matches:
                    # Analyze mismatch
                    if len(stored_text) != len(original_text):
                        mismatch_details = (
                            f"Length mismatch: {len(stored_text)} vs {len(original_text)} chars"
                        )
                    elif stored_text in original_text:
                        mismatch_details = "Stored text is truncated"
                    else:
                        mismatch_details = "Content mismatch detected"

                result = ValidationResult(
                    chunk_id=chunk_id,
                    matches=matches,
                    stored_text=stored_text,
                    original_text=original_text,
                    validation_passed=matches,
                    mismatch_details=mismatch_details,
                )
                results.append(result)

                if not matches:
                    logger.warning(
                        f"Chunk {chunk_id} validation failed: {mismatch_details}"
                    )

            except Exception as e:
                logger.error(f"Error validating chunk {chunk_id}: {str(e)}")
                raise DataIntegrityError(f"Validation failed for {chunk_id}: {str(e)}")

        return results

    @staticmethod
    def verify_search_result(
        result_text: str, original_text: str
    ) -> Dict[str, Any]:
        """Verify a search result matches original.

        Args:
            result_text: Text from search result
            original_text: Original text

        Returns:
            Verification result dictionary
        """
        matches = result_text == original_text
        return {
            "matches": matches,
            "stored_length": len(result_text),
            "original_length": len(original_text),
            "verification_passed": matches,
        }
