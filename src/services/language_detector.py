"""Language detection service."""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

from src.config.settings import settings
from src.utils.constants import AUTO_DETECT_CODE, validate_language_code
from src.utils.validators import validate_text_input

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of language detection."""
    
    success: bool
    detected_lang: str
    confidence: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "detected_lang": self.detected_lang,
            "confidence": self.confidence,
            "error": self.error,
        }


class LanguageDetector:
    """
    Language detection service.
    
    Detects the language of input text using various methods.
    """
    
    def __init__(self):
        """Initialize language detector."""
        self._translator = None
        
        if GOOGLETRANS_AVAILABLE:
            try:
                self._translator = Translator()
                logger.info("Language detector initialized (googletrans)")
            except Exception as e:
                logger.warning(f"Failed to initialize language detector: {e}")
        else:
            logger.warning("googletrans not available, language detection disabled")
    
    def detect(self, text: str) -> DetectionResult:
        """
        Detect language of text.
        
        Args:
            text: Text to analyze
        
        Returns:
            DetectionResult object
        """
        # Validate input
        is_valid, error = validate_text_input(text)
        if not is_valid:
            logger.error(f"Invalid input for detection: {error}")
            return DetectionResult(
                success=False,
                detected_lang="",
                error=error
            )
        
        # Check if detector is available
        if self._translator is None:
            logger.error("Language detector not available")
            return DetectionResult(
                success=False,
                detected_lang="",
                error="Language detection service not available"
            )
        
        try:
            # Detect language
            detection = self._translator.detect(text)
            
            detected_lang = detection.lang
            confidence = detection.confidence if hasattr(detection, 'confidence') else 0.0
            
            # Validate detected language
            if not validate_language_code(detected_lang):
                logger.warning(f"Invalid language code detected: {detected_lang}")
                return DetectionResult(
                    success=False,
                    detected_lang=detected_lang,
                    error="Invalid language detected"
                )
            
            logger.info(
                f"Language detected: {detected_lang} "
                f"(confidence: {confidence:.2f})"
            )
            
            return DetectionResult(
                success=True,
                detected_lang=detected_lang,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return DetectionResult(
                success=False,
                detected_lang="",
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """
        Check if language detection is available.
        
        Returns:
            True if detector is available
        """
        return self._translator is not None


# Global detector instance
_detector_instance: Optional[LanguageDetector] = None


def get_language_detector() -> LanguageDetector:
    """
    Get or create global language detector instance.
    
    Returns:
        LanguageDetector instance
    """
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    
    return _detector_instance