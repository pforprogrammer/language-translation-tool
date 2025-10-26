"""Tests for core services."""

import pytest
from src.services.translator import (
    TranslationService,
    get_translation_service,
    TranslationResult
)
from src.services.language_detector import (
    LanguageDetector,
    get_language_detector,
    DetectionResult
)
from src.services.tts_service import (
    TTSService,
    get_tts_service,
    TTSResult
)


class TestTranslationService:
    """Test translation service."""
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        service = TranslationService()
        assert service is not None
        assert service.cache is not None
    
    def test_get_translation_service(self):
        """Test global service instance."""
        service1 = get_translation_service()
        service2 = get_translation_service()
        assert service1 is service2  # Same instance
    
    def test_translate_basic(self):
        """Test basic translation."""
        service = get_translation_service()
        result = service.translate(
            text="Hello",
            source_lang="en",
            target_lang="es"
        )
        
        assert isinstance(result, TranslationResult)
        # Note: Actual translation depends on API availability
        if result.success:
            assert result.translated_text != ""
            assert result.source_lang == "en"
            assert result.target_lang == "es"
    
    def test_translate_empty_text(self):
        """Test translation with empty text."""
        service = get_translation_service()
        result = service.translate(
            text="",
            source_lang="en",
            target_lang="es"
        )
        
        assert result.success is False
        assert result.error is not None
    
    def test_translate_invalid_languages(self):
        """Test translation with invalid language codes."""
        service = get_translation_service()
        result = service.translate(
            text="Hello",
            source_lang="invalid",
            target_lang="es"
        )
        
        assert result.success is False
    
    def test_translate_with_cache(self):
        """Test translation caching."""
        service = get_translation_service()
        
        # First translation
        result1 = service.translate(
            text="Test caching",
            source_lang="en",
            target_lang="es",
            use_cache=True
        )
        
        # Second translation (should be cached)
        result2 = service.translate(
            text="Test caching",
            source_lang="en",
            target_lang="es",
            use_cache=True
        )
        
        if result1.success and result2.success:
            assert result2.cached or result2.translated_text == result1.translated_text
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        service = get_translation_service()
        providers = service.get_available_providers()
        
        assert isinstance(providers, list)


class TestLanguageDetector:
    """Test language detection service."""
    
    def test_detector_initialization(self):
        """Test detector initializes correctly."""
        detector = LanguageDetector()
        assert detector is not None
    
    def test_get_language_detector(self):
        """Test global detector instance."""
        detector1 = get_language_detector()
        detector2 = get_language_detector()
        assert detector1 is detector2
    
    def test_detect_language(self):
        """Test language detection."""
        detector = get_language_detector()
        
        if detector.is_available():
            result = detector.detect("Hello world")
            
            assert isinstance(result, DetectionResult)
            if result.success:
                assert result.detected_lang != ""
                assert 0 <= result.confidence <= 1
    
    def test_detect_empty_text(self):
        """Test detection with empty text."""
        detector = get_language_detector()
        result = detector.detect("")
        
        assert result.success is False
        assert result.error is not None
    
    def test_is_available(self):
        """Test availability check."""
        detector = get_language_detector()
        is_available = detector.is_available()
        
        assert isinstance(is_available, bool)


class TestTTSService:
    """Test text-to-speech service."""
    
    def test_service_initialization(self):
        """Test TTS service initializes correctly."""
        service = TTSService()
        assert service is not None
    
    def test_get_tts_service(self):
        """Test global TTS service instance."""
        service1 = get_tts_service()
        service2 = get_tts_service()
        assert service1 is service2
    
    def test_generate_speech(self):
        """Test speech generation."""
        service = get_tts_service()
        
        if service.is_available():
            result = service.generate_speech(
                text="Hello world",
                lang="en"
            )
            
            assert isinstance(result, TTSResult)
            if result.success:
                assert result.audio_base64 is not None
                assert result.provider != ""
    
    def test_generate_speech_empty_text(self):
        """Test TTS with empty text."""
        service = get_tts_service()
        result = service.generate_speech(text="", lang="en")
        
        assert result.success is False
        assert result.error is not None
    
    def test_is_available(self):
        """Test TTS availability check."""
        service = get_tts_service()
        is_available = service.is_available()
        
        assert isinstance(is_available, bool)
    
    def test_get_available_providers(self):
        """Test getting available TTS providers."""
        service = get_tts_service()
        providers = service.get_available_providers()
        
        assert isinstance(providers, list)