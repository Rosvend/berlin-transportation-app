#!/usr/bin/env python3
"""
Latency test for Berlin Transport App
Tests response times for various endpoints
"""
import time
import requests
import sys
from statistics import mean, median

API_BASE = "http://localhost:8000"

def measure_latency(url, label, iterations=5):
    """Measure latency for a given endpoint"""
    times = []
    
    print(f"\nTesting: {label}")
    print(f"URL: {url}")
    
    for i in range(iterations):
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            end = time.time()
            
            latency = (end - start) * 1000  # Convert to milliseconds
            times.append(latency)
            
            status_icon = "✓" if response.status_code == 200 else "✗"
            print(f"  Request {i+1}: {latency:.2f}ms {status_icon}")
            
            # Small delay between requests
            if i < iterations - 1:
                time.sleep(0.5)
                
        except requests.exceptions.RequestException as e:
            print(f"  Request {i+1}: FAILED - {e}")
            continue
    
    if times:
        print(f"\nResults for {label}:")
        print(f"  Average: {mean(times):.2f}ms")
        print(f"  Median:  {median(times):.2f}ms")
        print(f"  Min:     {min(times):.2f}ms")
        print(f"  Max:     {max(times):.2f}ms")
        
        # Check if under 1 second
        if mean(times) < 1000:
            print(f"  Status: PASSED (< 1000ms)")
        else:
            print(f"  Status: WARNING (>= 1000ms)")
        
        return mean(times)
    else:
        print(f"  Status: FAILED - No successful requests")
        return None

def main():
    print("=" * 60)
    print("Berlin Transport App - Latency Test")
    print("=" * 60)
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                print("Server is ready!")
                break
        except:
            if i == max_retries - 1:
                print("ERROR: Server did not start in time")
                sys.exit(1)
            time.sleep(1)
    
    # Test endpoints
    results = {}
    
    # Health check
    results['health'] = measure_latency(
        f"{API_BASE}/health",
        "Health Check",
        iterations=5
    )
    
    # Cache stats
    results['cache_stats'] = measure_latency(
        f"{API_BASE}/api/cache/stats",
        "Cache Statistics",
        iterations=5
    )
    
    # Station search (will be cached after first request)
    results['station_search'] = measure_latency(
        f"{API_BASE}/api/stations/search?q=Alexanderplatz&limit=10",
        "Station Search (with caching)",
        iterations=5
    )
    
    # Featured stations
    results['featured_stations'] = measure_latency(
        f"{API_BASE}/api/stations/featured",
        "Featured Stations",
        iterations=5
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_times = [t for t in results.values() if t is not None]
    if all_times:
        overall_avg = mean(all_times)
        print(f"\nOverall average latency: {overall_avg:.2f}ms")
        
        if overall_avg < 1000:
            print("✓ PASSED: Average latency is under 1 second")
        else:
            print("✗ FAILED: Average latency exceeds 1 second")
        
        # Check cache effectiveness
        print("\nCache effectiveness:")
        print("  Note: Subsequent requests to the same endpoint should be faster")
        print("  due to caching. Check the individual request times above.")
    else:
        print("✗ FAILED: No successful requests")
        sys.exit(1)

if __name__ == "__main__":
    main()
