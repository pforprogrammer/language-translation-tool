"""Application settings and configuration management."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_title: str = Field(
        default="AI Language Translation Tool",
        description="Application title"
    )
    app_icon: str = Field(
        default="🌍",
        description="Application icon emoji"
    )
    max_text_length: int = Field(
        default=5000,
        description="Maximum text length for translation",
        ge=1,
        le=10000
    )
    default_source_lang: str = Field(
        default="auto",
        description="Default source language"
    )
    default_target_lang: str = Field(
        default="es",
        description="Default target language"
    )

    # Translation API Configuration
    google_translate_api_key: Optional[str] = Field(
        default=None,
        description="Google Translate API key (optional)"
    )
    azure_translator_key: Optional[str] = Field(
        default=None,
        description="Azure Translator API key (optional)"
    )
    azure_translator_region: str = Field(
        default="eastus",
        description="Azure Translator region"
    )

    # Cache Configuration
    cache_enabled: bool = Field(
        default=True,
        description="Enable translation caching"
    )
    cache_ttl_hours: int = Field(
        default=24,
        description="Cache time-to-live in hours",
        ge=1,
        le=168  # Max 1 week
    )
    cache_max_size: int = Field(
        default=1000,
        description="Maximum number of cached translations",
        ge=10,
        le=10000
    )

    # Text-to-Speech Settings
    tts_enabled: bool = Field(
        default=True,
        description="Enable text-to-speech functionality"
    )
    tts_provider: str = Field(
        default="gtts",
        description="TTS provider: 'gtts' or 'pyttsx3'"
    )
    tts_speed: float = Field(
        default=1.0,
        description="TTS playback speed",
        ge=0.5,
        le=2.0
    )

    # Development Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )

    # Feature Flags
    enable_translation_history: bool = Field(
        default=True,
        description="Enable translation history tracking"
    )
    enable_language_detection: bool = Field(
        default=True,
        description="Enable automatic language detection"
    )
    enable_copy_button: bool = Field(
        default=True,
        description="Enable copy to clipboard button"
    )
    enable_tts_button: bool = Field(
        default=True,
        description="Enable text-to-speech button"
    )

    # Performance Settings
    translation_timeout: int = Field(
        default=10,
        description="Translation API timeout in seconds",
        ge=5,
        le=30
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of API retry attempts",
        ge=1,
        le=5
    )
    retry_delay: float = Field(
        default=1.0,
        description="Delay between retries in seconds",
        ge=0.5,
        le=5.0
    )

    def get_cache_ttl_seconds(self) -> int:
        """Convert cache TTL from hours to seconds."""
        return self.cache_ttl_hours * 3600

    def is_api_key_configured(self) -> bool:
        """Check if any translation API key is configured."""
        return bool(self.google_translate_api_key or self.azure_translator_key)


# Global settings instance
settings = Settings()


# Logging configuration
def configure_logging() -> None:
    """Configure application logging."""
    import logging
    import sys

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Set third-party library log levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# Initialize logging on import
configure_logging()