"""
Cache management utilities for the CountryCompare application.
"""

import json
import time
import hashlib
import threading
from typing import Dict, Any, Optional, Union, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheItem:
    """Represents a cached item with metadata."""
    
    def __init__(self, value: Any, ttl: int = 3600, created_at: Optional[datetime] = None):
        self.value = value
        self.ttl = ttl  # Time to live in seconds
        self.created_at = created_at or datetime.utcnow()
        self.access_count = 0
        self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache item has expired."""
        if self.ttl <= 0:  # Never expires
            return False
        
        expiry_time = self.created_at + timedelta(seconds=self.ttl)
        return datetime.utcnow() > expiry_time
    
    def touch(self):
        """Update access information."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cache item to dictionary."""
        return {
            'value': self.value,
            'ttl': self.ttl,
            'created_at': self.created_at.isoformat(),
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'is_expired': self.is_expired
        }


class MemoryCache:
    """In-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, CacheItem] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.lock = threading.RLock()
        self._cleanup_thread = None
        self._cleanup_interval = 300  # 5 minutes
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_expired():
            while True:
                time.sleep(self._cleanup_interval)
                self.cleanup_expired()
        
        self._cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        self._cleanup_thread.start()
    
    def _generate_key(self, key: Union[str, Dict, tuple]) -> str:
        """Generate cache key from various input types."""
        if isinstance(key, str):
            return key
        elif isinstance(key, dict):
            # Sort dict items to ensure consistent key generation
            sorted_items = sorted(key.items())
            key_str = json.dumps(sorted_items, sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
        elif isinstance(key, (list, tuple)):
            key_str = json.dumps(list(key), sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
        else:
            return str(key)
    
    def get(self, key: Union[str, Dict, tuple], default: Any = None) -> Any:
        """Get value from cache."""
        cache_key = self._generate_key(key)
        
        with self.lock:
            if cache_key in self.cache:
                item = self.cache[cache_key]
                
                if item.is_expired:
                    del self.cache[cache_key]
                    return default
                
                item.touch()
                return item.value
            
            return default
    
    def set(self, key: Union[str, Dict, tuple], value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl
        
        with self.lock:
            # Check if we need to evict items due to size limit
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                self._evict_lru()
            
            self.cache[cache_key] = CacheItem(value, ttl)
    
    def delete(self, key: Union[str, Dict, tuple]) -> bool:
        """Delete key from cache."""
        cache_key = self._generate_key(key)
        
        with self.lock:
            if cache_key in self.cache:
                del self.cache[cache_key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
    
    def exists(self, key: Union[str, Dict, tuple]) -> bool:
        """Check if key exists and is not expired."""
        cache_key = self._generate_key(key)
        
        with self.lock:
            if cache_key in self.cache:
                item = self.cache[cache_key]
                if item.is_expired:
                    del self.cache[cache_key]
                    return False
                return True
            return False
    
    def ttl(self, key: Union[str, Dict, tuple]) -> int:
        """Get TTL for a key in seconds."""
        cache_key = self._generate_key(key)
        
        with self.lock:
            if cache_key in self.cache:
                item = self.cache[cache_key]
                if item.is_expired:
                    del self.cache[cache_key]
                    return -1
                
                remaining = item.ttl - (datetime.utcnow() - item.created_at).total_seconds()
                return max(0, int(remaining))
            
            return -1
    
    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        with self.lock:
            expired_keys = [key for key, item in self.cache.items() if item.is_expired]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_items = len(self.cache)
            expired_items = sum(1 for item in self.cache.values() if item.is_expired)
            total_access = sum(item.access_count for item in self.cache.values())
            
            if total_items > 0:
                avg_access = total_access / total_items
            else:
                avg_access = 0
            
            return {
                'total_items': total_items,
                'expired_items': expired_items,
                'active_items': total_items - expired_items,
                'total_access_count': total_access,
                'average_access_count': avg_access,
                'max_size': self.max_size,
                'usage_percentage': (total_items / self.max_size) * 100 if self.max_size > 0 else 0
            }
    
    def keys(self) -> list:
        """Get all non-expired cache keys."""
        with self.lock:
            return [key for key, item in self.cache.items() if not item.is_expired]


class CacheDecorator:
    """Decorator for caching function results."""
    
    def __init__(self, cache: MemoryCache, ttl: int = 3600, key_prefix: str = ""):
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix
    
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = {
                'function': func.__name__,
                'prefix': self.key_prefix,
                'args': args,
                'kwargs': kwargs
            }
            
            # Try to get from cache
            result = self.cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            self.cache.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper


class CacheManager:
    """Main cache manager for the application."""
    
    def __init__(self):
        self.caches: Dict[str, MemoryCache] = {}
        self.default_cache = MemoryCache()
    
    def get_cache(self, name: str = "default") -> MemoryCache:
        """Get cache by name, create if doesn't exist."""
        if name not in self.caches:
            self.caches[name] = MemoryCache()
        return self.caches[name]
    
    def create_cache(self, name: str, default_ttl: int = 3600, max_size: int = 1000) -> MemoryCache:
        """Create a new named cache."""
        cache = MemoryCache(default_ttl=default_ttl, max_size=max_size)
        self.caches[name] = cache
        return cache
    
    def delete_cache(self, name: str) -> bool:
        """Delete a named cache."""
        if name in self.caches:
            self.caches[name].clear()
            del self.caches[name]
            return True
        return False
    
    def clear_all(self) -> None:
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()
        self.default_cache.clear()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches."""
        stats = {}
        
        # Default cache stats
        stats['default'] = self.default_cache.stats()
        
        # Named caches stats
        for name, cache in self.caches.items():
            stats[name] = cache.stats()
        
        return stats
    
    def cleanup_all(self) -> Dict[str, int]:
        """Cleanup expired items in all caches."""
        results = {}
        
        # Cleanup default cache
        results['default'] = self.default_cache.cleanup_expired()
        
        # Cleanup named caches
        for name, cache in self.caches.items():
            results[name] = cache.cleanup_expired()
        
        return results


# Global cache manager instance
cache_manager = CacheManager()

# Convenience functions
def get_cache(name: str = "default") -> MemoryCache:
    """Get cache instance."""
    return cache_manager.get_cache(name)


def cache_result(ttl: int = 3600, cache_name: str = "default", key_prefix: str = ""):
    """Decorator to cache function results."""
    cache = get_cache(cache_name)
    decorator = CacheDecorator(cache, ttl, key_prefix)
    return decorator


def invalidate_cache(pattern: str = None, cache_name: str = "default") -> int:
    """Invalidate cache entries matching pattern."""
    cache = get_cache(cache_name)
    
    if pattern is None:
        cache.clear()
        return cache.size()
    
    # Simple pattern matching - could be enhanced with regex
    keys_to_delete = []
    for key in cache.keys():
        if pattern in str(key):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete(key)
    
    return len(keys_to_delete)
