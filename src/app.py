"""
Language Translation Tool - Main Streamlit Application
A modern, AI-powered translation tool with TTS capabilities.
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
import base64
import logging
import json


# Configure page
st.set_page_config(
    page_title="AI Language Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import services
from src.services.translator import get_translation_service, TranslationResult
from src.services.language_detector import get_language_detector
from src.services.tts_service import get_tts_service
from src.utils.constants import (
    LANGUAGES,
    POPULAR_LANGUAGES,
    get_language_name,
    AUTO_DETECT_CODE,
    AUTO_DETECT_NAME,
    UI_EMOJI_TRANSLATE,
    UI_EMOJI_COPY,
    UI_EMOJI_LISTEN,
    UI_EMOJI_SWAP,
    UI_EMOJI_CLEAR,
    UI_EMOJI_HISTORY,
)
from src.utils.validators import validate_text_input, count_words
from src.utils.cache import get_cache
from src.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize and cache all services."""
    return {
        'translator': get_translation_service(),
        'detector': get_language_detector(),
        'tts': get_tts_service(),
        'cache': get_cache()
    }

services = get_services()


# Session state initialization
def init_session_state():
    """Initialize session state variables."""
    if 'translation_history' not in st.session_state:
        st.session_state.translation_history = []
    
    if 'current_translation' not in st.session_state:
        st.session_state.current_translation = None
    
    if 'source_lang' not in st.session_state:
        st.session_state.source_lang = settings.default_source_lang
    
    if 'target_lang' not in st.session_state:
        st.session_state.target_lang = settings.default_target_lang
    
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""
    
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False


# Helper functions
def add_to_history(result: TranslationResult, input_text: str):
    """Add translation to history."""
    if not settings.enable_translation_history:
        return
    
    history_item = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'source_text': input_text,
        'translated_text': result.translated_text,
        'source_lang': result.source_lang,
        'target_lang': result.target_lang,
        'provider': result.provider,
        'cached': result.cached
    }
    
    # Keep last 10 translations
    st.session_state.translation_history.insert(0, history_item)
    if len(st.session_state.translation_history) > 10:
        st.session_state.translation_history = st.session_state.translation_history[:10]


def swap_languages():
    """Swap source and target languages."""
    # Don't swap if source is auto-detect
    if st.session_state.source_lang == AUTO_DETECT_CODE:
        st.warning("Cannot swap when source is Auto-detect")
        return
    
    # Swap the values
    temp = st.session_state.source_lang
    st.session_state.source_lang = st.session_state.target_lang
    st.session_state.target_lang = temp
    
    # Clear current translation when swapping
    st.session_state.current_translation = None
        

def clear_input():
    """Clear input text and results."""
    st.session_state.input_text = ""
    st.session_state.current_translation = None


def get_audio_player_html(audio_base64: str) -> str:
    """Generate HTML for audio player."""
    return f"""
    <audio controls autoplay style="width: 100%;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """


def export_history_to_json():
    """Export translation history to JSON file."""
    if not st.session_state.translation_history:
        return None
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "translations": st.session_state.translation_history
    }
    
    return json.dumps(export_data, indent=2)


def get_dark_mode_css() -> str:
    """Get dark mode CSS."""
    return """
    <style>
    /* Dark Mode Styles */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .main .block-container {
        background-color: #0e1117;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
    
    .stTextArea textarea {
        background-color: #262730 !important;
        color: #fafafa !important;
        border-color: #464646 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #262730 !important;
        color: #fafafa !important;
    }
    
    .stButton > button {
        background-color: #262730 !important;
        color: #fafafa !important;
        border-color: #464646 !important;
    }
    
    .stButton > button:hover {
        background-color: #3d3d3d !important;
        border-color: #666666 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
    }
    
    .stMarkdown {
        color: #fafafa !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #fafafa !important;
    }
    
    .css-1629p8f, .css-16huue1 {
        color: #b0b0b0 !important;
    }
    </style>
    """


def toggle_dark_mode():
    """Toggle dark mode."""
    st.session_state.dark_mode = not st.session_state.dark_mode


# UI Components
def render_header():
    """Render application header."""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.title(f"{settings.app_icon} {settings.app_title}")
        st.markdown(
            "Translate text between 100+ languages with AI-powered accuracy. "
            "Features auto-detection, text-to-speech, and translation history."
        )


def render_sidebar():
    """Render sidebar with settings and information."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Dark mode toggle
        if st.button("🌙 Toggle Dark Mode"):
            toggle_dark_mode()
            st.rerun()
        
        # Provider information
        st.subheader("🔌 Active Providers")
        providers = services['translator'].get_available_providers()
        for provider in providers:
            st.success(f"✓ {provider}")
        
        # Feature status
        st.subheader("✨ Features")
        features = {
            "Translation": True,
            "Auto-detect": services['detector'].is_available(),
            "Text-to-Speech": services['tts'].is_available(),
            "Translation History": settings.enable_translation_history,
            "Caching": settings.cache_enabled
        }
        
        for feature, status in features.items():
            if status:
                st.success(f"✓ {feature}")
            else:
                st.warning(f"⚠ {feature} (unavailable)")
        
        # Cache statistics
        if settings.cache_enabled:
            st.subheader("📊 Cache Stats")
            cache_stats = services['cache'].get_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cache Size", f"{cache_stats['size']}/{cache_stats['max_size']}")
            with col2:
                st.metric("Hit Rate", f"{cache_stats['hit_rate']}%")
            
            if st.button("🗑️ Clear Cache"):
                services['cache'].clear()
                st.success("Cache cleared!")
                st.rerun()
        
        # About section
        st.divider()
        st.subheader("ℹ️ About")
        st.info(
            "Built with Python, Streamlit, and modern translation APIs. "
            "Part of CodeAlpha AI Internship Program."
        )
        
        # Version info
        st.caption("Version 1.0.0")


def render_language_selectors():
    """Render language selection controls."""
    col1, col2, col3 = st.columns([5, 1, 5])
    
    # Prepare language options
    all_languages = {AUTO_DETECT_CODE: AUTO_DETECT_NAME, **LANGUAGES}
    lang_options = list(all_languages.keys())
    lang_labels = [all_languages[code] for code in lang_options]
    
    with col1:
        # Source language
        source_index = lang_options.index(st.session_state.source_lang)
        source_lang = st.selectbox(
            "Source Language",
            options=lang_options,
            format_func=lambda x: all_languages[x],
            index=source_index,
            key="source_lang_selector"
        )
        st.session_state.source_lang = source_lang
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button(f"{UI_EMOJI_SWAP}", help="Swap languages", key="swap_btn"):
            swap_languages()
            st.rerun()  # Force UI update
    
    with col3:
        # Target language (no auto-detect)
        target_options = list(LANGUAGES.keys())
        target_index = target_options.index(st.session_state.target_lang)
        target_lang = st.selectbox(
            "Target Language",
            options=target_options,
            format_func=lambda x: LANGUAGES[x],
            index=target_index,
            key="target_lang_selector"
        )
        st.session_state.target_lang = target_lang


def render_translation_area():
    """Render main translation input/output area."""
    # Input area
    st.subheader("📝 Enter Text to Translate")
    
    input_text = st.text_area(
        "Input Text",
        value=st.session_state.input_text,
        height=150,
        max_chars=settings.max_text_length,
        placeholder="Type or paste text here...",
        label_visibility="collapsed"
    )
    
    # Character and word count
    char_count = len(input_text)
    word_count = count_words(input_text)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.caption(f"Characters: {char_count}/{settings.max_text_length}")
    with col2:
        st.caption(f"Words: {word_count}")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        translate_btn = st.button(
            f"{UI_EMOJI_TRANSLATE} Translate",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button(f"{UI_EMOJI_CLEAR} Clear", use_container_width=True):
            clear_input()
            st.rerun()
    
    with col3:
        # Auto-detect button
        if st.session_state.source_lang == AUTO_DETECT_CODE and input_text:
            if st.button("🔍 Detect Language", use_container_width=True):
                with st.spinner("Detecting language..."):
                    detection = services['detector'].detect(input_text)
                    if detection.success:
                        st.success(
                            f"Detected: {get_language_name(detection.detected_lang)} "
                            f"(Confidence: {detection.confidence:.0%})"
                        )
                    else:
                        st.error(f"Detection failed: {detection.error}")
    
    # Perform translation
    if translate_btn and input_text:
        # Validate input
        is_valid, error = validate_text_input(input_text)
        if not is_valid:
            st.error(error)
            return
        
        # Store input
        st.session_state.input_text = input_text
        
        # Translate
        with st.spinner("Translating..."):
            result = services['translator'].translate(
                text=input_text,
                source_lang=st.session_state.source_lang,
                target_lang=st.session_state.target_lang,
                use_cache=True
            )
        
        if result.success:
            # FIXED: Always update current_translation with new result
            st.session_state.current_translation = result
            add_to_history(result, input_text)
            st.success("Translation completed!")
            # Force rerun to update UI
            st.rerun()
        else:
            st.error(f"Translation failed: {result.error}")


def render_translation_result():
    """Render translation result area."""
    if st.session_state.current_translation is None:
        return
    
    result = st.session_state.current_translation
    
    st.divider()
    st.subheader("✅ Translation Result")
    
    # FIXED: Use unique key with timestamp to force refresh
    translation_key = f"translation_output_{id(result)}"
    
    # Display translation
    st.text_area(
        "Translated Text",
        value=result.translated_text,
        height=150,
        label_visibility="collapsed",
        key=translation_key,
        disabled=True  # Make read-only
    )
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source_name = get_language_name(result.source_lang)
        st.caption(f"**From:** {source_name}")
    
    with col2:
        target_name = get_language_name(result.target_lang)
        st.caption(f"**To:** {target_name}")
    
    with col3:
        provider_info = f"{result.provider}"
        if result.cached:
            provider_info += " (cached)"
        st.caption(f"**Provider:** {provider_info}")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        # Copy button
        if settings.enable_copy_button:
            if st.button(f"{UI_EMOJI_COPY} Copy", use_container_width=True, key="copy_btn"):
                # Use clipboard API via JavaScript
                st.write(
                    f'<textarea id="translation_copy" style="position:absolute;left:-9999px;">{result.translated_text}</textarea>',
                    unsafe_allow_html=True
                )
                st.write(
                    """
                    <script>
                    var copyText = document.getElementById("translation_copy");
                    copyText.select();
                    document.execCommand("copy");
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                st.code(result.translated_text, language=None)
                st.success("✅ Text displayed above - Select and copy with Ctrl+C (Cmd+C on Mac)")
                st.info("💡 Tip: Click the copy icon in the code block above to copy instantly!")
    
    with col2:
        # Text-to-Speech button
        if settings.enable_tts_button and services['tts'].is_available():
            if st.button(f"{UI_EMOJI_LISTEN} Listen", use_container_width=True):
                with st.spinner("Generating audio..."):
                    audio_result = services['tts'].generate_speech(
                        text=result.translated_text,
                        lang=result.target_lang
                    )
                
                if audio_result.success:
                    st.markdown(
                        get_audio_player_html(audio_result.audio_base64),
                        unsafe_allow_html=True
                    )
                else:
                    st.error(f"TTS failed: {audio_result.error}")


def render_translation_history():
    """Render translation history."""
    if not settings.enable_translation_history:
        return
    
    if not st.session_state.translation_history:
        return
    
    st.divider()
    st.subheader(f"{UI_EMOJI_HISTORY} Recent Translations")
    
    # Export history button
    json_data = export_history_to_json()
    if json_data:
        st.download_button(
            label="📥 Export History",
            data=json_data,
            file_name=f"translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Display history
    with st.expander("View History", expanded=False):
        for i, item in enumerate(st.session_state.translation_history):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                source_name = get_language_name(item['source_lang'])
                target_name = get_language_name(item['target_lang'])
                
                st.markdown(
                    f"**{source_name} → {target_name}**\n\n"
                    f"📄 *{item['source_text'][:50]}...*\n\n"
                    f"✓ *{item['translated_text'][:50]}...*"
                )
            
            with col2:
                st.caption(item['timestamp'])
                if item['cached']:
                    st.caption("💾 Cached")
            
            if i < len(st.session_state.translation_history) - 1:
                st.divider()
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.translation_history = []
            st.rerun()


def render_quick_phrases():
    """Render quick phrase shortcuts."""
    st.divider()
    st.subheader("⚡ Quick Phrases")
    
    quick_phrases = {
        "Hello": "👋",
        "Thank you": "🙏",
        "Good morning": "🌅",
        "Goodbye": "👋",
        "Yes": "✓",
        "No": "✗",
        "Please": "🙏",
        "How are you?": "💬"
    }
    
    cols = st.columns(4)
    
    for i, (phrase, emoji) in enumerate(quick_phrases.items()):
        with cols[i % 4]:
            if st.button(f"{emoji} {phrase}", key=f"quick_{i}"):
                st.session_state.input_text = phrase
                st.rerun()


def render_batch_translation():
    """Render batch translation interface."""
    st.divider()
    st.subheader("📋 Batch Translation")
    
    batch_text = st.text_area(
        "Enter multiple lines to translate (one per line)",
        height=200,
        placeholder="Line 1\nLine 2\nLine 3...",
        key="batch_input"
    )
    
    if st.button("🔄 Translate All"):
        lines = [line.strip() for line in batch_text.split('\n') if line.strip()]
        
        if not lines:
            st.error("Please enter at least one line to translate")
            return
        
        with st.spinner(f"Translating {len(lines)} lines..."):
            results = services['translator'].translate_batch(
                texts=lines,
                source_lang=st.session_state.source_lang,
                target_lang=st.session_state.target_lang
            )
        
        # Display results
        st.success(f"Translated {len(results)} lines!")
        
        for i, (line, result) in enumerate(zip(lines, results)):
            with st.expander(f"Translation {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Original:**\n{line}")
                with col2:
                    if result.success:
                        st.markdown(f"**Translated:**\n{result.translated_text}")
                    else:
                        st.error(f"Error: {result.error}")


def render_footer():
    """Render footer."""
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            """
            <div style="text-align: center;">
                <p>Built with ❤️ using Python, Streamlit, and AI</p>
                <p style="font-size: 0.8em; color: gray;">
                    Part of CodeAlpha AI Internship Program
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# Main application
def main():
    """Main application entry point."""
    # Initialize session state FIRST
    init_session_state()
    
    # Apply dark mode if enabled
    if st.session_state.dark_mode:
        st.markdown(get_dark_mode_css(), unsafe_allow_html=True)
    
    # Render UI
    render_header()
    render_sidebar()
    
    # Main content
    render_language_selectors()
    st.divider()
    render_translation_area()
    render_translation_result()
    render_translation_history()
    render_quick_phrases()
    render_batch_translation()
    render_footer()


# Run application
if __name__ == "__main__":
    main()