#!/usr/bin/env python3
"""
Quick cache performance test - verifies Redis integration
"""
import sys
import os
import time

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.cache import _cache, cached

def test_cache_performance():
    """Test cache performance with and without Redis"""
    
    print("Cache Performance Test")
    print("=" * 60)
    
    # Get cache info
    stats = _cache.get_stats()
    print(f"\nCache backend: {'Redis' if stats['using_redis'] else 'In-Memory'}")
    print(f"Initial state: {stats}")
    
    # Create a test function
    call_count = 0
    
    @cached(ttl=60)
    def expensive_operation(x):
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # Simulate slow operation
        return x * 2
    
    # Test 1: First call (cache miss)
    print("\nTest 1: First call (cache miss)")
    start = time.time()
    result = expensive_operation(42)
    first_call_time = (time.time() - start) * 1000
    print(f"  Result: {result}")
    print(f"  Time: {first_call_time:.2f}ms")
    print(f"  Function called: {call_count} times")
    
    # Test 2: Second call (cache hit)
    print("\nTest 2: Second call (cache hit)")
    start = time.time()
    result = expensive_operation(42)
    second_call_time = (time.time() - start) * 1000
    print(f"  Result: {result}")
    print(f"  Time: {second_call_time:.2f}ms")
    print(f"  Function called: {call_count} times (should still be 1)")
    
    # Calculate speedup
    speedup = first_call_time / second_call_time if second_call_time > 0 else 0
    print(f"\nSpeedup: {speedup:.1f}x faster")
    
    # Check cache stats
    final_stats = _cache.get_stats()
    print(f"\nFinal cache stats:")
    print(f"  Hits: {final_stats['hits']}")
    print(f"  Misses: {final_stats['misses']}")
    print(f"  Hit rate: {final_stats['hit_rate']}")
    
    # Verify performance
    print("\n" + "=" * 60)
    if second_call_time < 10:  # Should be < 10ms if cached
        print("PASSED: Cache is working efficiently")
        print(f"Cached response time: {second_call_time:.2f}ms (< 10ms)")
        return True
    else:
        print("WARNING: Cache may not be working optimally")
        print(f"Cached response time: {second_call_time:.2f}ms (>= 10ms)")
        return False

if __name__ == "__main__":
    success = test_cache_performance()
    sys.exit(0 if success else 1)
