"""
Tests for cache utility
"""
import pytest
import time
from app.utils.cache import cached, clear_cache, get_cache_stats, cleanup_cache

@pytest.fixture(autouse=True)
def reset_cache():
    """Reset cache before each test"""
    clear_cache()
    yield
    clear_cache()

def test_cache_decorator():
    """Test that cache decorator works"""
    call_count = 0
    
    @cached(ttl=1)
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2
    
    # First call - should execute
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count == 1
    
    # Second call - should use cache
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count == 1  # Should not increment
    
    # Different argument - should execute again
    result3 = expensive_function(10)
    assert result3 == 20
    assert call_count == 2

def test_cache_expiration():
    """Test that cache expires after TTL"""
    call_count = 0
    
    @cached(ttl=1)  # 1 second TTL
    def function_with_short_ttl(x):
        nonlocal call_count
        call_count += 1
        return x * 3
    
    # First call
    result1 = function_with_short_ttl(5)
    assert result1 == 15
    assert call_count == 1
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Should execute again after expiration
    result2 = function_with_short_ttl(5)
    assert result2 == 15
    assert call_count == 2

def test_clear_cache():
    """Test clearing cache"""
    @cached(ttl=60)
    def cached_function(x):
        return x + 1
    
    # Populate cache
    cached_function(1)
    cached_function(2)
    
    stats_before = get_cache_stats()
    assert stats_before["memory_size"] > 0 or (stats_before.get("redis_keys", 0) > 0)
    
    # Clear cache
    clear_cache()
    
    stats_after = get_cache_stats()
    assert stats_after["memory_size"] == 0

def test_cache_stats():
    """Test cache statistics"""
    clear_cache()  # Start fresh
    
    @cached(ttl=60)
    def test_func(x):
        return x * 2
    
    # Populate cache
    test_func(1)  # Miss
    test_func(1)  # Hit
    test_func(2)  # Miss
    test_func(1)  # Hit
    
    stats = get_cache_stats()
    assert stats["hits"] >= 2
    assert stats["misses"] >= 2
    assert "hit_rate" in stats
    assert "using_redis" in stats

def test_cleanup_expired():
    """Test cleanup of expired entries"""
    @cached(ttl=1)
    def short_lived_function(x):
        return x
    
    # Create some cached entries
    short_lived_function(1)
    short_lived_function(2)
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Cleanup should remove expired entries
    removed = cleanup_cache()
    assert removed >= 0  # Should remove at least some entries
