"""
Settings - Application configuration loaded from environment.

Uses pydantic-settings for validation and .env file support.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Supports .env file in the project root for local development.

    Attributes:
        openai_api_key: API key for OpenAI
        openai_model: Model to use for completions
        log_level: Logging level
        data_dir: Directory containing data files

    Example:
        >>> settings = Settings()
        >>> print(settings.openai_model)
        "gpt-4o-mini"
    """

    # OpenAI configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # Data directories
    data_dir: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / "data",
        description="Directory containing data files"
    )

    # Future API configuration (for Phase 4+)
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def taxonomy_file(self) -> Path:
        """Path to taxonomy JSON file."""
        return self.data_dir / "taxonomy.json"

    @property
    def risk_matrix_file(self) -> Path:
        """Path to risk matrix JSON file."""
        return self.data_dir / "risk_matrix.json"

    @property
    def incident_history_file(self) -> Path:
        """Path to incident history JSON file."""
        return self.data_dir / "incident_history.json"

    @property
    def standards_file(self) -> Path:
        """Path to standards JSON file."""
        return self.data_dir / "standards.json"


def get_settings() -> Settings:
    """
    Get application settings singleton.

    Returns:
        Settings instance
    """
    return Settings()
