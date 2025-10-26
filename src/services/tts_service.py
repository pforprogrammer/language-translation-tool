"""Text-to-speech service."""

import io
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from src.config.settings import settings
from src.utils.constants import (
    TTSProvider,
    is_tts_supported,
    MAX_TEXT_LENGTH_TTS,
)
from src.utils.validators import validate_text_input, truncate_text

logger = logging.getLogger(__name__)


@dataclass
class TTSResult:
    """Result of text-to-speech operation."""
    
    success: bool
    audio_data: Optional[bytes] = None
    audio_base64: Optional[str] = None
    provider: str = "unknown"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "audio_base64": self.audio_base64,
            "provider": self.provider,
            "error": self.error,
        }


class TTSService:
    """
    Text-to-speech service.
    
    Supports:
    - Google Text-to-Speech (gTTS)
    - pyttsx3 (offline TTS)
    """
    
    def __init__(self):
        """Initialize TTS service."""
        self.provider = settings.tts_provider
        self.speed = settings.tts_speed
        
        self._gtts_available = GTTS_AVAILABLE
        self._pyttsx3_available = PYTTSX3_AVAILABLE
        
        logger.info(
            f"TTS service initialized (gTTS: {self._gtts_available}, "
            f"pyttsx3: {self._pyttsx3_available})"
        )
    
    def generate_speech(
        self,
        text: str,
        lang: str = "en",
        slow: bool = False
    ) -> TTSResult:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            lang: Language code
            slow: Whether to speak slowly
        
        Returns:
            TTSResult object
        """
        # Validate input
        is_valid, error = validate_text_input(text)
        if not is_valid:
            logger.error(f"Invalid TTS input: {error}")
            return TTSResult(
                success=False,
                error=error
            )
        
        # Truncate if too long
        if len(text) > MAX_TEXT_LENGTH_TTS:
            logger.warning(f"Text too long for TTS, truncating to {MAX_TEXT_LENGTH_TTS}")
            text = truncate_text(text, MAX_TEXT_LENGTH_TTS)
        
        # Check if language is supported
        if not is_tts_supported(lang):
            logger.warning(f"Language {lang} may not be supported by TTS")
        
        # Try primary provider
        if self.provider == TTSProvider.GTTS.value and self._gtts_available:
            result = self._generate_with_gtts(text, lang, slow)
            if result.success:
                return result
        
        # Try fallback providers
        if self._gtts_available:
            result = self._generate_with_gtts(text, lang, slow)
            if result.success:
                return result
        
        # All providers failed
        logger.error("All TTS providers failed")
        return TTSResult(
            success=False,
            error="Text-to-speech generation failed"
        )
    
    def _generate_with_gtts(
        self,
        text: str,
        lang: str,
        slow: bool
    ) -> TTSResult:
        """
        Generate speech using gTTS.
        
        Args:
            text: Text to convert
            lang: Language code
            slow: Whether to speak slowly
        
        Returns:
            TTSResult object
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            # Save to BytesIO
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Get audio data
            audio_data = audio_fp.read()
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            logger.info(f"TTS generated successfully (gTTS, lang: {lang})")
            
            return TTSResult(
                success=True,
                audio_data=audio_data,
                audio_base64=audio_base64,
                provider=TTSProvider.GTTS.value
            )
            
        except Exception as e:
            logger.error(f"gTTS generation failed: {e}")
            return TTSResult(
                success=False,
                error=str(e),
                provider=TTSProvider.GTTS.value
            )
    
    def _generate_with_pyttsx3(
        self,
        text: str,
        lang: str,
        slow: bool
    ) -> TTSResult:
        """
        Generate speech using pyttsx3 (offline).
        
        Note: pyttsx3 doesn't support all languages and direct audio export
        is platform-dependent.
        
        Args:
            text: Text to convert
            lang: Language code (limited support)
            slow: Whether to speak slowly
        
        Returns:
            TTSResult object
        """
        try:
            engine = pyttsx3.init()
            
            # Adjust rate based on slow parameter
            rate = engine.getProperty('rate')
            if slow:
                engine.setProperty('rate', rate * 0.75)
            
            # Save to file (pyttsx3 limitation)
            temp_file = io.BytesIO()
            
            # Note: pyttsx3 doesn't support direct BytesIO writing
            # This is a simplified implementation
            logger.warning("pyttsx3 TTS not fully implemented")
            
            return TTSResult(
                success=False,
                error="pyttsx3 provider not fully implemented",
                provider=TTSProvider.PYTTSX3.value
            )
            
        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            return TTSResult(
                success=False,
                error=str(e),
                provider=TTSProvider.PYTTSX3.value
            )
    
    def is_available(self) -> bool:
        """
        Check if TTS service is available.
        
        Returns:
            True if any TTS provider is available
        """
        return self._gtts_available or self._pyttsx3_available
    
    def get_available_providers(self) -> list[str]:
        """
        Get list of available TTS providers.
        
        Returns:
            List of provider names
        """
        providers = []
        
        if self._gtts_available:
            providers.append(TTSProvider.GTTS.value)
        
        if self._pyttsx3_available:
            providers.append(TTSProvider.PYTTSX3.value)
        
        return providers


# Global service instance
_tts_instance: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """
    Get or create global TTS service instance.
    
    Returns:
        TTSService instance
    """
    global _tts_instance
    
    if _tts_instance is None:
        _tts_instance = TTSService()
    
    return _tts_instance