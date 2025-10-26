"""Translation caching utilities."""

import hashlib
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from collections import OrderedDict
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached translation entry."""
    
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: float = field(default_factory=time.time)
    hit_count: int = 1
    provider: str = "unknown"
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry has expired."""
        return (time.time() - self.timestamp) > ttl_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_text": self.source_text,
            "translated_text": self.translated_text,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "timestamp": self.timestamp,
            "hit_count": self.hit_count,
            "provider": self.provider,
        }


class TranslationCache:
    """In-memory LRU cache for translations."""
    
    def __init__(
        self,
        max_size: Optional[int] = None,
        ttl_hours: Optional[int] = None
    ):
        """
        Initialize translation cache.
        
        Args:
            max_size: Maximum number of entries (default from settings)
            ttl_hours: Time-to-live in hours (default from settings)
        """
        self.max_size = max_size or settings.cache_max_size
        self.ttl_hours = ttl_hours or settings.cache_ttl_hours
        self.ttl_seconds = self.ttl_hours * 3600
        
        # Use OrderedDict for LRU functionality
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        self._hits = 0
        self._misses = 0
        
        logger.info(
            f"Translation cache initialized: "
            f"max_size={self.max_size}, ttl={self.ttl_hours}h"
        )
    
    def _generate_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Generate cache key from translation parameters.
        
        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Cache key (hash)
        """
        # Create unique identifier
        identifier = f"{source_lang}:{target_lang}:{text}"
        
        # Generate hash
        return hashlib.sha256(identifier.encode()).hexdigest()
    
    def get(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Get cached translation.
        
        Args:
            text: Source text
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Cached translation or None if not found/expired
        """
        if not settings.cache_enabled:
            return None
        
        key = self._generate_key(text, source_lang, target_lang)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired(self.ttl_seconds):
                logger.debug(f"Cache entry expired: {key[:16]}...")
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            # Increment hit count
            entry.hit_count += 1
            
            self._hits += 1
            logger.debug(
                f"Cache hit: {key[:16]}... (hits: {entry.hit_count})"
            )
            
            return entry.translated_text
        
        self._misses += 1
        logger.debug(f"Cache miss: {key[:16]}...")
        return None
    
    def set(
        self,
        text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        provider: str = "unknown"
    ) -> None:
        """
        Store translation in cache.
        
        Args:
            text: Source text
            translated_text: Translated text
            source_lang: Source language code
            target_lang: Target language code
            provider: Translation provider name
        """
        if not settings.cache_enabled:
            return
        
        key = self._generate_key(text, source_lang, target_lang)
        
        # Create cache entry
        entry = CacheEntry(
            source_text=text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            provider=provider
        )
        
        # Add to cache
        self._cache[key] = entry
        self._cache.move_to_end(key)
        
        # Enforce size limit (LRU eviction)
        if len(self._cache) > self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"Cache eviction (LRU): {oldest_key[:16]}...")
        
        logger.debug(f"Cache set: {key[:16]}... (size: {len(self._cache)})")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_hours": self.ttl_hours,
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        if not settings.cache_enabled:
            return 0
        
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired(self.ttl_seconds)
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_all_entries(self) -> list[Dict[str, Any]]:
        """
        Get all cache entries (for debugging).
        
        Returns:
            List of cache entry dictionaries
        """
        return [entry.to_dict() for entry in self._cache.values()]


# Global cache instance
_cache_instance: Optional[TranslationCache] = None


def get_cache() -> TranslationCache:
    """
    Get or create global cache instance.
    
    Returns:
        TranslationCache instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = TranslationCache()
    
    return _cache_instance


def clear_cache() -> None:
    """Clear global cache instance."""
    cache = get_cache()
    cache.clear()