"""
Simple cache for API responses with Redis fallback
Reduces latency for repeated queries
"""
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
from functools import wraps
import hashlib
import json
import logging
import os

logger = logging.getLogger(__name__)

# Try to import Redis, fall back to in-memory if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")

class SimpleCache:
    """Cache with Redis support and in-memory fallback"""
    
    def __init__(self):
        self._cache = {}
        self._hits = 0
        self._misses = 0
        self._redis_client = None
        self._use_redis = False
        
        # Try to connect to Redis
        if REDIS_AVAILABLE:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", "6379"))
                redis_db = int(os.getenv("REDIS_DB", "0"))
                
                self._redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self._redis_client.ping()
                self._use_redis = True
                logger.info(f"Redis cache connected at {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                self._redis_client = None
                self._use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        # Try Redis first if available
        if self._use_redis and self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    self._hits += 1
                    logger.debug(f"Redis cache HIT for key: {key[:50]}...")
                    return json.loads(value)
                else:
                    self._misses += 1
                    logger.debug(f"Redis cache MISS for key: {key[:50]}...")
                    return None
            except Exception as e:
                logger.warning(f"Redis error on GET, falling back to memory: {e}")
                # Fall through to in-memory cache
        
        # In-memory cache
        if key in self._cache:
            data, expiry = self._cache[key]
            if datetime.now() < expiry:
                self._hits += 1
                logger.debug(f"Memory cache HIT for key: {key[:50]}...")
                return data
            else:
                # Expired, remove it
                del self._cache[key]
                logger.debug(f"Memory cache EXPIRED for key: {key[:50]}...")
        
        self._misses += 1
        logger.debug(f"Memory cache MISS for key: {key[:50]}...")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL"""
        # Try Redis first if available
        if self._use_redis and self._redis_client:
            try:
                serialized = json.dumps(value, default=str)
                self._redis_client.setex(key, ttl_seconds, serialized)
                logger.debug(f"Redis cache SET for key: {key[:50]}... (TTL: {ttl_seconds}s)")
                return
            except Exception as e:
                logger.warning(f"Redis error on SET, falling back to memory: {e}")
                # Fall through to in-memory cache
        
        # In-memory cache
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)
        logger.debug(f"Memory cache SET for key: {key[:50]}... (TTL: {ttl_seconds}s)")
    
    def clear(self):
        """Clear all cache"""
        # Clear Redis if available
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.flushdb()
                logger.info("Redis cache cleared")
            except Exception as e:
                logger.warning(f"Failed to clear Redis cache: {e}")
        
        # Clear in-memory cache
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Memory cache cleared ({count} items removed)")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        stats = {
            "memory_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "using_redis": self._use_redis
        }
        
        # Add Redis info if available
        if self._use_redis and self._redis_client:
            try:
                info = self._redis_client.info("stats")
                stats["redis_keys"] = self._redis_client.dbsize()
                stats["redis_hits"] = info.get("keyspace_hits", 0)
                stats["redis_misses"] = info.get("keyspace_misses", 0)
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
        
        return stats
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired_keys = [k for k, (_, exp) in self._cache.items() if now >= exp]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)

# Global cache instance
_cache = SimpleCache()

def make_cache_key(*args, **kwargs) -> str:
    """Create a cache key from function arguments"""
    # Skip first arg if it looks like 'self' (for instance methods)
    # by checking if args exist and making hashable copies
    args_to_hash = args
    if args and hasattr(args[0], '__dict__'):
        # Likely a 'self' parameter, skip it
        args_to_hash = args[1:]
    
    # Convert args to strings for JSON serialization
    try:
        key_data = json.dumps({
            "args": [str(arg) for arg in args_to_hash],
            "kwargs": sorted([(k, str(v)) for k, v in kwargs.items()])
        }, sort_keys=True)
    except (TypeError, ValueError):
        # Fallback to string representation
        key_data = f"args:{args_to_hash}:kwargs:{sorted(kwargs.items())}"
    
    # Hash it to create a fixed-length key
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
    
    Usage:
        @cached(ttl=600)
        def my_expensive_function(param1, param2):
            # ... expensive operation
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Not in cache, call function
            result = func(*args, **kwargs)
            
            # Store in cache
            _cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Export functions to interact with cache
def clear_cache():
    """Clear all cached data"""
    _cache.clear()

def get_cache_stats() -> dict:
    """Get cache statistics"""
    return _cache.get_stats()

def cleanup_cache():
    """Remove expired entries"""
    return _cache.cleanup_expired()
