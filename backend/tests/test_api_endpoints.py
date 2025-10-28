"""
Tests for API endpoints
"""
import pytest
from unittest.mock import patch, MagicMock

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data

def test_cache_stats_endpoint(client):
    """Test cache statistics endpoint"""
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "cache" in data
    assert "size" in data["cache"]
    assert "hits" in data["cache"]
    assert "misses" in data["cache"]

def test_cache_clear_endpoint(client):
    """Test cache clear endpoint"""
    response = client.post("/api/cache/clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_cache_cleanup_endpoint(client):
    """Test cache cleanup endpoint"""
    response = client.post("/api/cache/cleanup")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

@patch('app.services.bvg_client.bvg_client.search_stations')
def test_search_stations_success(mock_search, client, mock_bvg_stations_response):
    """Test station search with successful response"""
    mock_search.return_value = mock_bvg_stations_response
    
    response = client.get("/api/stations/search?q=Alexander&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "stations" in data
    assert len(data["stations"]) > 0

@patch('app.services.bvg_client.bvg_client.search_stations')
def test_search_stations_invalid_query(mock_search, client):
    """Test station search with invalid query (too short)"""
    response = client.get("/api/stations/search?q=A&limit=10")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

@patch('app.services.bvg_client.bvg_client.search_stations')
def test_search_stations_api_unavailable(mock_search, client):
    """Test station search when BVG API is unavailable"""
    mock_search.return_value = None
    
    response = client.get("/api/stations/search?q=Berlin&limit=10")
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data

def test_get_all_stations(client):
    """Test get all stations endpoint"""
    response = client.get("/api/stations/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_featured_stations(client):
    """Test get featured stations endpoint"""
    response = client.get("/api/stations/featured")
    assert response.status_code == 200
    data = response.json()
    assert "stations" in data
    assert len(data["stations"]) > 0

@patch('app.services.bvg_client.bvg_client.get_departures')
def test_get_departures_success(mock_departures, client, mock_bvg_departures_response):
    """Test get departures with successful response"""
    mock_departures.return_value = mock_bvg_departures_response
    
    response = client.get("/api/departures/900000100003?duration=60")
    assert response.status_code == 200
    data = response.json()
    assert "station" in data
    assert "departures" in data
    assert len(data["departures"]) > 0

@patch('app.services.bvg_client.bvg_client.get_departures')
def test_get_departures_api_unavailable(mock_departures, client):
    """Test get departures when BVG API is unavailable"""
    mock_departures.return_value = None
    
    response = client.get("/api/departures/900000100003")
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data

def test_get_station_info(client):
    """Test get station info endpoint"""
    response = client.get("/api/stations/900000100003")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
