"""Translation service with multi-provider support."""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

try:
    from googletrans import Translator as GoogleTranslator
except ImportError:
    GoogleTranslator = None

try:
    from deep_translator import GoogleTranslator as DeepGoogleTranslator
except ImportError:
    DeepGoogleTranslator = None

import httpx

from src.config.settings import settings
from src.utils.constants import (
    TranslationProvider,
    AUTO_DETECT_CODE,
    ERROR_TRANSLATION_FAILED,
    ERROR_NETWORK,
)
from src.utils.validators import validate_translation_request, sanitize_text
from src.utils.cache import get_cache

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Result of a translation operation."""
    
    success: bool
    translated_text: str
    source_lang: str
    target_lang: str
    detected_lang: Optional[str] = None
    confidence: float = 0.0
    provider: str = "unknown"
    cached: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "translated_text": self.translated_text,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "detected_lang": self.detected_lang,
            "confidence": self.confidence,
            "provider": self.provider,
            "cached": self.cached,
            "error": self.error,
        }


class TranslationService:
    """
    Translation service with multiple provider support.
    
    Supports:
    - Google Translate (via googletrans)
    - Google Translate (via deep-translator)
    - Fallback mechanism
    - Caching
    - Retry logic
    """
    
    def __init__(self):
        """Initialize translation service."""
        self.cache = get_cache()
        self.timeout = settings.translation_timeout
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay
        
        # Initialize providers
        self._google_translator = None
        self._deep_translator = None
        
        self._init_providers()
        
        logger.info("Translation service initialized")
    
    def _init_providers(self) -> None:
        """Initialize translation providers."""
        # Initialize googletrans
        if GoogleTranslator is not None:
            try:
                self._google_translator = GoogleTranslator()
                logger.info("Google Translate (googletrans) initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize googletrans: {e}")
        
        # deep-translator doesn't need initialization
        if DeepGoogleTranslator is not None:
            logger.info("Deep Translator available")
    
    def translate(
        self,
        text: str,
        source_lang: str = AUTO_DETECT_CODE,
        target_lang: str = "es",
        use_cache: bool = True
    ) -> TranslationResult:
        """
        Translate text from source to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (or 'auto' for detection)
            target_lang: Target language code
            use_cache: Whether to use caching
        
        Returns:
            TranslationResult object
        """
        # Validate request
        is_valid, error = validate_translation_request(text, source_lang, target_lang)
        if not is_valid:
            logger.error(f"Validation failed: {error}")
            return TranslationResult(
                success=False,
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                error=error
            )
        
        # Sanitize input
        text = sanitize_text(text)
        
        # Check cache
        if use_cache and settings.cache_enabled:
            cached_result = self.cache.get(text, source_lang, target_lang)
            if cached_result:
                logger.info("Translation retrieved from cache")
                return TranslationResult(
                    success=True,
                    translated_text=cached_result,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    provider="cache",
                    cached=True
                )
        
        # Try translation with retry logic
        for attempt in range(self.max_retries):
            try:
                result = self._translate_with_providers(
                    text, source_lang, target_lang
                )
                
                if result.success:
                    # Cache the result
                    if use_cache and settings.cache_enabled:
                        self.cache.set(
                            text=text,
                            translated_text=result.translated_text,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            provider=result.provider
                        )
                    
                    logger.info(
                        f"Translation successful (provider: {result.provider}, "
                        f"attempt: {attempt + 1})"
                    )
                    return result
                
            except Exception as e:
                logger.warning(
                    f"Translation attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
        
        # All attempts failed
        logger.error("All translation attempts failed")
        return TranslationResult(
            success=False,
            translated_text="",
            source_lang=source_lang,
            target_lang=target_lang,
            error=ERROR_TRANSLATION_FAILED
        )
    
    def _translate_with_providers(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Try translation with available providers.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            TranslationResult object
        """
        # Try googletrans first
        if self._google_translator is not None:
            try:
                result = self._translate_with_googletrans(
                    text, source_lang, target_lang
                )
                if result.success:
                    return result
            except Exception as e:
                logger.warning(f"googletrans failed: {e}")
        
        # Try deep-translator as fallback
        if DeepGoogleTranslator is not None:
            try:
                result = self._translate_with_deep_translator(
                    text, source_lang, target_lang
                )
                if result.success:
                    return result
            except Exception as e:
                logger.warning(f"deep-translator failed: {e}")
        
        # All providers failed
        raise Exception("All translation providers failed")
    
    def _translate_with_googletrans(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Translate using googletrans library.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            TranslationResult object
        """
        try:
            result = self._google_translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            detected_lang = None
            confidence = 0.0
            
            if source_lang == AUTO_DETECT_CODE and hasattr(result, 'src'):
                detected_lang = result.src
                confidence = getattr(result, 'confidence', 0.0) or 0.0
            
            return TranslationResult(
                success=True,
                translated_text=result.text,
                source_lang=detected_lang or source_lang,
                target_lang=target_lang,
                detected_lang=detected_lang,
                confidence=confidence,
                provider=TranslationProvider.GOOGLE.value
            )
            
        except Exception as e:
            logger.error(f"googletrans translation failed: {e}")
            raise
    
    def _translate_with_deep_translator(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResult:
        """
        Translate using deep-translator library.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            TranslationResult object
        """
        try:
            # Handle auto-detect
            src_lang = source_lang if source_lang != AUTO_DETECT_CODE else "auto"
            
            translator = DeepGoogleTranslator(source=src_lang, target=target_lang)
            translated = translator.translate(text)
            
            return TranslationResult(
                success=True,
                translated_text=translated,
                source_lang=source_lang,
                target_lang=target_lang,
                provider=TranslationProvider.DEEP_TRANSLATOR.value
            )
            
        except Exception as e:
            logger.error(f"deep-translator translation failed: {e}")
            raise
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str = AUTO_DETECT_CODE,
        target_lang: str = "es",
        use_cache: bool = True
    ) -> List[TranslationResult]:
        """
        Translate multiple texts.
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            use_cache: Whether to use caching
        
        Returns:
            List of TranslationResult objects
        """
        results = []
        
        for text in texts:
            result = self.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                use_cache=use_cache
            )
            results.append(result)
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available translation providers.
        
        Returns:
            List of provider names
        """
        providers = []
        
        if self._google_translator is not None:
            providers.append(TranslationProvider.GOOGLE.value)
        
        if DeepGoogleTranslator is not None:
            providers.append(TranslationProvider.DEEP_TRANSLATOR.value)
        
        return providers


# Global service instance
_service_instance: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """
    Get or create global translation service instance.
    
    Returns:
        TranslationService instance
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = TranslationService()
    
    return _service_instance