"""Application constants and language definitions."""

from typing import Dict, List, Tuple
from enum import Enum


class TranslationProvider(str, Enum):
    """Available translation service providers."""
    GOOGLE = "google"
    DEEP_TRANSLATOR = "deep_translator"
    AZURE = "azure"


class TTSProvider(str, Enum):
    """Available text-to-speech providers."""
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"


# Language codes and names (ISO 639-1 standard)
LANGUAGES: Dict[str, str] = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "am": "Amharic",
    "ar": "Arabic",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "eu": "Basque",
    "be": "Belarusian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "ny": "Chichewa",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "co": "Corsican",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "fy": "Frisian",
    "gl": "Galician",
    "ka": "Georgian",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "ht": "Haitian Creole",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "iw": "Hebrew",
    "hi": "Hindi",
    "hmn": "Hmong",
    "hu": "Hungarian",
    "is": "Icelandic",
    "ig": "Igbo",
    "id": "Indonesian",
    "ga": "Irish",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "kn": "Kannada",
    "kk": "Kazakh",
    "km": "Khmer",
    "ko": "Korean",
    "ku": "Kurdish (Kurmanji)",
    "ky": "Kyrgyz",
    "lo": "Lao",
    "la": "Latin",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "lb": "Luxembourgish",
    "mk": "Macedonian",
    "mg": "Malagasy",
    "ms": "Malay",
    "ml": "Malayalam",
    "mt": "Maltese",
    "mi": "Maori",
    "mr": "Marathi",
    "mn": "Mongolian",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "no": "Norwegian",
    "ps": "Pashto",
    "fa": "Persian",
    "pl": "Polish",
    "pt": "Portuguese",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sm": "Samoan",
    "gd": "Scots Gaelic",
    "sr": "Serbian",
    "st": "Sesotho",
    "sn": "Shona",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "so": "Somali",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "tg": "Tajik",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "cy": "Welsh",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "zu": "Zulu",
}

# Popular languages (for quick access)
POPULAR_LANGUAGES: List[str] = [
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "de",  # German
    "zh-CN",  # Chinese (Simplified)
    "ja",  # Japanese
    "ko",  # Korean
    "ar",  # Arabic
    "ru",  # Russian
    "pt",  # Portuguese
    "hi",  # Hindi
    "it",  # Italian
]

# Languages supported by gTTS (for text-to-speech)
GTTS_SUPPORTED_LANGUAGES: List[str] = [
    "af", "ar", "bn", "bs", "ca", "cs", "cy", "da", "de", "el",
    "en", "eo", "es", "et", "fi", "fr", "gu", "hi", "hr", "hu",
    "id", "is", "it", "iw", "ja", "jw", "km", "kn", "ko", "la",
    "lv", "mk", "ml", "mr", "my", "ne", "nl", "no", "pl", "pt",
    "ro", "ru", "si", "sk", "sq", "sr", "su", "sv", "sw", "ta",
    "te", "th", "tl", "tr", "uk", "ur", "vi", "zh-CN", "zh-TW",
]

# Auto-detect option
AUTO_DETECT_CODE = "auto"
AUTO_DETECT_NAME = "Auto-detect"

# Maximum text lengths for different contexts
MAX_TEXT_LENGTH_DEFAULT = 5000
MAX_TEXT_LENGTH_TTS = 2000  # TTS providers often have lower limits
MIN_TEXT_LENGTH = 1

# Character limits for display
PREVIEW_LENGTH = 100  # Characters to show in preview
HISTORY_ITEM_LENGTH = 50  # Characters in history items

# API rate limiting
API_RATE_LIMIT_DELAY = 0.1  # Seconds between consecutive requests
API_MAX_RETRIES = 3
API_TIMEOUT_SECONDS = 10

# Cache settings
DEFAULT_CACHE_SIZE = 1000
DEFAULT_CACHE_TTL_HOURS = 24

# UI Constants
UI_EMOJI_TRANSLATE = "🔄"
UI_EMOJI_COPY = "📋"
UI_EMOJI_LISTEN = "🔊"
UI_EMOJI_SWAP = "⇄"
UI_EMOJI_CLEAR = "🗑️"
UI_EMOJI_HISTORY = "📜"
UI_EMOJI_SUCCESS = "✅"
UI_EMOJI_ERROR = "❌"
UI_EMOJI_WARNING = "⚠️"

# Error messages
ERROR_EMPTY_INPUT = "Please enter text to translate"
ERROR_TEXT_TOO_LONG = "Text exceeds maximum length of {max_length} characters"
ERROR_TRANSLATION_FAILED = "Translation failed. Please try again."
ERROR_NETWORK = "Network error. Please check your connection."
ERROR_API_KEY_MISSING = "API key not configured"
ERROR_INVALID_LANGUAGE = "Selected language is not supported"
ERROR_TTS_FAILED = "Text-to-speech generation failed"

# Success messages
SUCCESS_TRANSLATION = "Translation completed successfully"
SUCCESS_COPY = "Copied to clipboard!"
SUCCESS_TTS = "Playing audio..."

# Helper functions
def get_language_name(code: str) -> str:
    """Get language name from code."""
    if code == AUTO_DETECT_CODE:
        return AUTO_DETECT_NAME
    return LANGUAGES.get(code, code)


def get_language_code(name: str) -> str:
    """Get language code from name."""
    if name == AUTO_DETECT_NAME:
        return AUTO_DETECT_CODE
    
    for code, lang_name in LANGUAGES.items():
        if lang_name.lower() == name.lower():
            return code
    return name


def get_all_languages_with_auto() -> Dict[str, str]:
    """Get all languages including auto-detect option."""
    return {AUTO_DETECT_CODE: AUTO_DETECT_NAME, **LANGUAGES}


def get_language_list() -> List[Tuple[str, str]]:
    """Get list of (code, name) tuples for all languages."""
    return [(code, name) for code, name in LANGUAGES.items()]


def get_popular_language_names() -> List[str]:
    """Get list of popular language names."""
    return [LANGUAGES[code] for code in POPULAR_LANGUAGES if code in LANGUAGES]


def is_tts_supported(lang_code: str) -> bool:
    """Check if language is supported by gTTS."""
    return lang_code in GTTS_SUPPORTED_LANGUAGES


def validate_language_code(code: str) -> bool:
    """Validate if language code exists."""
    return code in LANGUAGES or code == AUTO_DETECT_CODE


# Language direction (for UI layout)
RTL_LANGUAGES = ["ar", "iw", "fa", "ur"]  # Right-to-left languages


def is_rtl_language(code: str) -> bool:
    """Check if language is right-to-left."""
    return code in RTL_LANGUAGES