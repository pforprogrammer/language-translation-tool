#!/usr/bin/env python3
"""Interactive service testing script."""

from src.services.translator import get_translation_service
from src.services.language_detector import get_language_detector
from src.services.tts_service import get_tts_service

print("=" * 60)
print("Core Services Test")
print("=" * 60)

# Test 1: Translation Service
print("\n1. Translation Service Test:")
translator = get_translation_service()
print(f"   Service initialized: ✓")
print(f"   Available providers: {translator.get_available_providers()}")

result = translator.translate(
    text="Hello, how are you?",
    source_lang="en",
    target_lang="es"
)

if result.success:
    print(f"   ✓ Translation successful")
    print(f"   Original: Hello, how are you?")
    print(f"   Translated: {result.translated_text}")
    print(f"   Provider: {result.provider}")
    print(f"   Cached: {result.cached}")
else:
    print(f"   ✗ Translation failed: {result.error}")

# Test 2: Language Detection
print("\n2. Language Detection Test:")
detector = get_language_detector()

if detector.is_available():
    print(f"   Service initialized: ✓")
    
    detection = detector.detect("Bonjour le monde")
    
    if detection.success:
        print(f"   ✓ Detection successful")
        print(f"   Text: Bonjour le monde")
        print(f"   Detected: {detection.detected_lang}")
        print(f"   Confidence: {detection.confidence:.2f}")
    else:
        print(f"   ✗ Detection failed: {detection.error}")
else:
    print(f"   ⚠ Language detection not available")

# Test 3: Text-to-Speech Service
print("\n3. Text-to-Speech Service Test:")
tts = get_tts_service()

if tts.is_available():
    print(f"   Service initialized: ✓")
    print(f"   Available providers: {tts.get_available_providers()}")
    
    audio = tts.generate_speech(
        text="Hello world",
        lang="en"
    )
    
    if audio.success:
        print(f"   ✓ TTS generation successful")
        print(f"   Provider: {audio.provider}")
        print(f"   Audio size: {len(audio.audio_data)} bytes")
    else:
        print(f"   ✗ TTS failed: {audio.error}")
else:
    print(f"   ⚠ TTS service not available")

# Test 4: Cache Statistics
print("\n4. Cache Statistics:")
from src.utils.cache import get_cache

cache = get_cache()
stats = cache.get_stats()

print(f"   Size: {stats['size']}/{stats['max_size']}")
print(f"   Hits: {stats['hits']}")
print(f"   Misses: {stats['misses']}")
print(f"   Hit Rate: {stats['hit_rate']}%")

print("\n" + "=" * 60)
print("✅ Service testing complete!")
print("=" * 60)