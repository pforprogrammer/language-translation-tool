"""Tests for configuration and constants."""

import pytest
from src.config.settings import Settings, settings
from src.utils.constants import (
    get_language_name,
    get_language_code,
    validate_language_code,
    is_tts_supported,
)
from src.utils.validators import (
    validate_text_input,
    validate_language_pair,
    sanitize_text,
    count_words,
)
from src.utils.cache import TranslationCache, CacheEntry


class TestSettings:
    """Test settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        test_settings = Settings()
        assert test_settings.app_title == "AI Language Translation Tool"
        assert test_settings.max_text_length == 5000
        assert test_settings.cache_enabled is True
    
    def test_cache_ttl_conversion(self):
        """Test cache TTL conversion to seconds."""
        test_settings = Settings(cache_ttl_hours=24)
        assert test_settings.get_cache_ttl_seconds() == 86400


class TestConstants:
    """Test language constants."""
    
    def test_get_language_name(self):
        """Test getting language name from code."""
        assert get_language_name("en") == "English"
        assert get_language_name("es") == "Spanish"
        assert get_language_name("auto") == "Auto-detect"
    
    def test_get_language_code(self):
        """Test getting language code from name."""
        assert get_language_code("English") == "en"
        assert get_language_code("Spanish") == "es"
        assert get_language_code("Auto-detect") == "auto"
    
    def test_validate_language_code(self):
        """Test language code validation."""
        assert validate_language_code("en") is True
        assert validate_language_code("es") is True
        assert validate_language_code("auto") is True
        assert validate_language_code("invalid") is False
    
    def test_tts_support(self):
        """Test TTS language support."""
        assert is_tts_supported("en") is True
        assert is_tts_supported("es") is True
        # Some languages may not be supported
        assert isinstance(is_tts_supported("hmn"), bool)


class TestValidators:
    """Test validation functions."""
    
    def test_validate_text_input_empty(self):
        """Test empty text validation."""
        is_valid, error = validate_text_input("")
        assert is_valid is False
        assert "enter text" in error.lower()
    
    def test_validate_text_input_too_long(self):
        """Test text too long validation."""
        long_text = "a" * 6000
        is_valid, error = validate_text_input(long_text, max_length=5000)
        assert is_valid is False
        assert "exceeds" in error.lower()
    
    def test_validate_text_input_valid(self):
        """Test valid text input."""
        is_valid, error = validate_text_input("Hello world")
        assert is_valid is True
        assert error == ""
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        text = "  Hello   world  \n  test  "
        sanitized = sanitize_text(text)
        assert sanitized == "Hello world test"
    
    def test_validate_language_pair_valid(self):
        """Test valid language pair."""
        is_valid, error = validate_language_pair("en", "es")
        assert is_valid is True
        assert error == ""
    
    def test_validate_language_pair_same(self):
        """Test same language validation."""
        is_valid, error = validate_language_pair("en", "en")
        assert is_valid is False
    
    def test_validate_language_pair_invalid_target(self):
        """Test invalid target language."""
        is_valid, error = validate_language_pair("en", "auto")
        assert is_valid is False
    
    def test_count_words(self):
        """Test word counting."""
        assert count_words("Hello world") == 2
        assert count_words("") == 0
        assert count_words("One two three four") == 4


class TestCache:
    """Test caching functionality."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = TranslationCache(max_size=10, ttl_hours=1)
        assert cache.max_size == 10
        assert cache.ttl_hours == 1
    
    def test_cache_set_get(self):
        """Test setting and getting cache entries."""
        cache = TranslationCache(max_size=10)
        cache.set("Hello", "Hola", "en", "es", "google")
        
        result = cache.get("Hello", "en", "es")
        assert result == "Hola"
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = TranslationCache(max_size=10)
        result = cache.get("Nonexistent", "en", "es")
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction."""
        cache = TranslationCache(max_size=2)
        
        cache.set("Text1", "Translation1", "en", "es")
        cache.set("Text2", "Translation2", "en", "es")
        cache.set("Text3", "Translation3", "en", "es")  # Should evict Text1
        
        # Text1 should be evicted
        assert cache.get("Text1", "en", "es") is None
        # Text2 and Text3 should still be there
        assert cache.get("Text2", "en", "es") == "Translation2"
        assert cache.get("Text3", "en", "es") == "Translation3"
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = TranslationCache(max_size=10)
        
        cache.set("Hello", "Hola", "en", "es")
        cache.get("Hello", "en", "es")  # Hit
        cache.get("Goodbye", "en", "es")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
    
    def test_cache_clear(self):
        """Test clearing cache."""
        cache = TranslationCache(max_size=10)
        
        cache.set("Hello", "Hola", "en", "es")
        cache.clear()
        
        assert cache.get("Hello", "en", "es") is None
        stats = cache.get_stats()
        assert stats["size"] == 0