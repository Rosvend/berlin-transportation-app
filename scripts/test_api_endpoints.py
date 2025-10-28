"""
Script para probar todos los endpoints de la API
Mide latencia y valida respuestas
"""
import requests
import time
from typing import Dict, Any
import json

API_BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def test_endpoint(method: str, endpoint: str, params: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return metrics"""
    url = f"{API_BASE_URL}{endpoint}"
    
    print(f"\n{Colors.BLUE}Testing:{Colors.RESET} {method} {endpoint}")
    if params:
        print(f"  Params: {params}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=15)
        elif method == "POST":
            response = requests.post(url, json=params, timeout=15)
        else:
            return {"error": "Method not supported"}
        
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "latency_ms": round(latency, 2),
            "success": response.status_code == expected_status
        }
        
        # Validate response
        if response.status_code == expected_status:
            print_success(f"Status: {response.status_code} - Latency: {result['latency_ms']}ms")
            
            # Try to parse JSON
            try:
                data = response.json()
                result["response_size"] = len(json.dumps(data))
                result["response_type"] = type(data).__name__
                
                # Endpoint-specific validation
                if "search" in endpoint and isinstance(data, dict):
                    stations = data.get("stations", [])
                    print(f"  Found {len(stations)} stations")
                    result["items_count"] = len(stations)
                elif "departures" in endpoint and isinstance(data, dict):
                    departures = data.get("departures", [])
                    print(f"  Found {len(departures)} departures")
                    result["items_count"] = len(departures)
                elif isinstance(data, list):
                    print(f"  Returned {len(data)} items")
                    result["items_count"] = len(data)
                    
            except Exception as e:
                print_warning(f"Could not parse JSON: {e}")
        else:
            print_error(f"Status: {response.status_code} (Expected: {expected_status})")
            print(f"  Response: {response.text[:200]}")
        
        # Latency warnings
        if latency > 5000:
            print_error(f"⚠️  Very slow response: {latency}ms")
        elif latency > 2000:
            print_warning(f"Slow response: {latency}ms")
        
        return result
        
    except requests.exceptions.Timeout:
        print_error("Request timed out (>15s)")
        return {
            "endpoint": endpoint,
            "method": method,
            "error": "Timeout",
            "success": False
        }
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server. Is it running?")
        return {
            "endpoint": endpoint,
            "method": method,
            "error": "Connection Error",
            "success": False
        }
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return {
            "endpoint": endpoint,
            "method": method,
            "error": str(e),
            "success": False
        }

def main():
    print_header("🚀 BERLIN TRANSPORT API - ENDPOINT TESTING")
    
    results = []
    
    # Test 1: Health check
    print_header("1️⃣  Health Check")
    results.append(test_endpoint("GET", "/health"))
    
    # Test 2: Search stations
    print_header("2️⃣  Station Search Endpoint")
    results.append(test_endpoint("GET", "/api/stations/search", {"q": "Alexanderplatz", "limit": 10}))
    results.append(test_endpoint("GET", "/api/stations/search", {"q": "Haupt", "limit": 5}))
    results.append(test_endpoint("GET", "/api/stations/search", {"q": "Zoo", "limit": 15}))
    
    # Test 3: Search with invalid params
    print_header("3️⃣  Invalid Search (should fail)")
    results.append(test_endpoint("GET", "/api/stations/search", {"q": "A", "limit": 10}, expected_status=400))
    
    # Test 4: Get all stations
    print_header("4️⃣  Get All Stations")
    results.append(test_endpoint("GET", "/api/stations/all"))
    
    # Test 5: Get featured stations
    print_header("5️⃣  Get Featured Stations")
    results.append(test_endpoint("GET", "/api/stations/featured"))
    
    # Test 6: Get departures for specific station
    print_header("6️⃣  Get Departures")
    results.append(test_endpoint("GET", "/api/departures/900000100003", {"duration": 60}))  # Alexanderplatz
    
    # Test 7: Get station info
    print_header("7️⃣  Get Station Info")
    results.append(test_endpoint("GET", "/api/stations/900000100003"))
    
    # Print summary
    print_header("📊 SUMMARY")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\nTotal tests: {len(results)}")
    print_success(f"Successful: {len(successful)}")
    if failed:
        print_error(f"Failed: {len(failed)}")
    
    # Latency stats
    latencies = [r.get("latency_ms", 0) for r in results if "latency_ms" in r]
    if latencies:
        print(f"\n{Colors.BLUE}Latency Statistics:{Colors.RESET}")
        print(f"  Average: {sum(latencies)/len(latencies):.2f}ms")
        print(f"  Min: {min(latencies):.2f}ms")
        print(f"  Max: {max(latencies):.2f}ms")
    
    # Failed tests detail
    if failed:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for r in failed:
            error = r.get("error", "Unknown error")
            print(f"  ✗ {r['method']} {r['endpoint']} - {error}")
    
    # Performance warnings
    slow_endpoints = [r for r in results if r.get("latency_ms", 0) > 2000]
    if slow_endpoints:
        print(f"\n{Colors.YELLOW}Slow Endpoints (>2s):{Colors.RESET}")
        for r in slow_endpoints:
            print(f"  ⚠ {r['endpoint']} - {r.get('latency_ms')}ms")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    return len(failed) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
