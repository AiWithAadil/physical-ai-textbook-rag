"""Configuration management for Retrieval Service."""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Qdrant Configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_TIMEOUT: float = float(os.getenv("QDRANT_TIMEOUT", "5.0"))

    # Cohere Configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "embed-english-v3.0")

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "mistralai/devstral-2512:free")
    OPENROUTER_TEMPERATURE: float = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))
    OPENROUTER_MAX_TOKENS: int = int(os.getenv("OPENROUTER_MAX_TOKENS", "1024"))
    OPENROUTER_TIMEOUT: int = int(os.getenv("OPENROUTER_TIMEOUT", "30"))
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def setup_logging(cls) -> None:
        """Configure logging for the application."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Initialize config
config = Config()
config.setup_logging()
logger = logging.getLogger(__name__)
