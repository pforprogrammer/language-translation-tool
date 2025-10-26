"""Input validation and sanitization utilities."""

import re
from typing import Tuple, Optional
import logging

from src.config.settings import settings
from src.utils.constants import (
    MAX_TEXT_LENGTH_DEFAULT,
    MIN_TEXT_LENGTH,
    validate_language_code,
    ERROR_EMPTY_INPUT,
    ERROR_TEXT_TOO_LONG,
    ERROR_INVALID_LANGUAGE,
    AUTO_DETECT_CODE,
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_text_input(text: str, max_length: Optional[int] = None) -> Tuple[bool, str]:
    """
    Validate user text input.
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed length (default from settings)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if max_length is None:
        max_length = settings.max_text_length

    # Check if empty
    if not text or not text.strip():
        return False, ERROR_EMPTY_INPUT

    # Check minimum length
    if len(text.strip()) < MIN_TEXT_LENGTH:
        return False, ERROR_EMPTY_INPUT

    # Check maximum length
    if len(text) > max_length:
        return False, ERROR_TEXT_TOO_LONG.format(max_length=max_length)

    return True, ""


def sanitize_text(text: str) -> str:
    """
    Sanitize input text by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def validate_language_pair(
    source_lang: str,
    target_lang: str
) -> Tuple[bool, str]:
    """
    Validate source and target language codes.
    
    Args:
        source_lang: Source language code
        target_lang: Target language code
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate source language
    if source_lang != AUTO_DETECT_CODE and not validate_language_code(source_lang):
        return False, f"{ERROR_INVALID_LANGUAGE}: {source_lang}"

    # Validate target language
    if target_lang == AUTO_DETECT_CODE:
        return False, "Target language cannot be auto-detect"
    
    if not validate_language_code(target_lang):
        return False, f"{ERROR_INVALID_LANGUAGE}: {target_lang}"

    # Check if languages are the same (when source is not auto)
    if source_lang != AUTO_DETECT_CODE and source_lang == target_lang:
        return False, "Source and target languages cannot be the same"

    return True, ""


def validate_translation_request(
    text: str,
    source_lang: str,
    target_lang: str
) -> Tuple[bool, str]:
    """
    Validate complete translation request.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate text
    is_valid, error = validate_text_input(text)
    if not is_valid:
        return False, error

    # Validate language pair
    is_valid, error = validate_language_pair(source_lang, target_lang)
    if not is_valid:
        return False, error

    return True, ""


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def normalize_language_code(code: str) -> str:
    """
    Normalize language code to standard format.
    
    Args:
        code: Language code
    
    Returns:
        Normalized language code
    """
    if not code:
        return AUTO_DETECT_CODE
    
    code = code.lower().strip()
    
    # Handle special cases
    if code in ["zh-cn", "zh_cn", "zh-hans"]:
        return "zh-CN"
    elif code in ["zh-tw", "zh_tw", "zh-hant"]:
        return "zh-TW"
    
    return code


def extract_text_preview(text: str, max_length: int = 100) -> str:
    """
    Extract preview of text for display.
    
    Args:
        text: Full text
        max_length: Maximum preview length
    
    Returns:
        Text preview
    """
    text = text.strip()
    if len(text) <= max_length:
        return text
    
    # Try to break at sentence or word boundary
    preview = text[:max_length]
    
    # Find last sentence ending
    last_sentence = max(
        preview.rfind('.'),
        preview.rfind('!'),
        preview.rfind('?')
    )
    
    if last_sentence > max_length * 0.5:  # At least 50% of max length
        return preview[:last_sentence + 1]
    
    # Find last word boundary
    last_space = preview.rfind(' ')
    if last_space > 0:
        return preview[:last_space] + "..."
    
    return preview + "..."


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
    
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split on whitespace and filter empty strings
    words = [word for word in text.split() if word]
    return len(words)


def estimate_translation_time(text: str) -> float:
    """
    Estimate translation time in seconds.
    
    Args:
        text: Text to translate
    
    Returns:
        Estimated time in seconds
    """
    # Base time + time per character
    base_time = 0.5  # seconds
    time_per_char = 0.001  # seconds
    
    return base_time + (len(text) * time_per_char)