"""
Redis caching service for BVG API responses
Implements caching layer to reduce API calls and improve performance
"""
import json
import logging
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheService:
    """Async Redis cache service with TTL support"""
    
    def __init__(self, redis_url: str, default_ttl: int = 300):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            await self.client.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            # Don't raise - allow app to run without cache
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Redis cache disconnected")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not self.is_connected:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache HIT for key: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS for key: {key}")
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET for key: {key} (TTL: {ttl}s)")
            return True
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Cache SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        try:
            await self.client.delete(key)
            logger.debug(f"Cache DELETE for key: {key}")
            return True
        except RedisError as e:
            logger.error(f"Cache DELETE error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern
        
        Args:
            pattern: Redis key pattern (e.g., "departures:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_connected:
            return 0
        
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except RedisError as e:
            logger.error(f"Cache CLEAR error for pattern {pattern}: {e}")
            return 0
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from prefix and arguments
        
        Args:
            prefix: Key prefix (e.g., "departures", "stations")
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            Generated cache key
        """
        parts = [prefix]
        parts.extend(str(arg) for arg in args)
        parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return ":".join(parts)


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache async function results
    
    Args:
        prefix: Cache key prefix
        ttl: Cache TTL in seconds
        key_builder: Optional function to build custom cache key
        
    Example:
        @cached("departures", ttl=300)
        async def get_departures(stop_id: str):
            # ... fetch from API
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get cache service if available
            cache = getattr(self, '_cache', None)
            if not cache or not cache.is_connected:
                return await func(self, *args, **kwargs)
            
            # Build cache key
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = cache.cache_key(prefix, *args, **kwargs)
            
            # Try cache first
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - call function
            result = await func(self, *args, **kwargs)
            
            # Store in cache
            if result is not None:
                await cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_service: Optional[CacheService] = None


async def get_cache_service() -> CacheService:
    """
    Get cache service instance
    This function should be used as a FastAPI dependency
    """
    global _cache_service
    if _cache_service is None:
        raise RuntimeError("Cache service not initialized")
    return _cache_service


async def initialize_cache_service(redis_url: str, default_ttl: int = 300) -> CacheService:
    """Initialize and connect cache service"""
    global _cache_service
    _cache_service = CacheService(redis_url, default_ttl)
    await _cache_service.connect()
    return _cache_service


async def shutdown_cache_service() -> None:
    """Shutdown cache service"""
    global _cache_service
    if _cache_service is not None:
        await _cache_service.close()
        _cache_service = None
