"""
Basic smoke tests for the Berlin Transport backend
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_api_info():
    """Test the API info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data


def test_homepage():
    """Test the homepage loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_featured_stations():
    """Test fetching featured stations"""
    response = client.get("/api/stations/featured")
    assert response.status_code == 200
    data = response.json()
    assert "stations" in data
    assert len(data["stations"]) > 0


def test_station_search_validation():
    """Test station search input validation"""
    # Query too short
    response = client.get("/api/stations/search?q=a")
    assert response.status_code == 422  # Validation error
    
    # Valid query
    response = client.get("/api/stations/search?q=alex")
    # Should succeed even if BVG API is unavailable
    assert response.status_code in [200, 503]


def test_departures_endpoint_exists():
    """Test that departures endpoint exists"""
    # Test with a known station ID (Alexanderplatz)
    response = client.get("/api/departures/900000100003")
    # Should either succeed or fail gracefully
    assert response.status_code in [200, 404, 503]


@pytest.mark.asyncio
async def test_config_loading():
    """Test that configuration loads correctly"""
    from app.config import get_settings
    
    settings = get_settings()
    assert settings.app_name is not None
    assert settings.bvg_api_base_url is not None
    assert settings.cache_ttl > 0


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/health")
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
