"""
Tests for BVG Client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.bvg_client import BVGClient

@pytest.fixture
def bvg_client():
    """Create a BVG client instance"""
    return BVGClient()

def test_bvg_client_initialization(bvg_client):
    """Test BVG client is initialized correctly"""
    assert bvg_client.api_url == "https://v6.bvg.transport.rest"
    assert bvg_client.timeout == 5
    assert bvg_client.max_retries == 1
    assert bvg_client.retry_delay == 0.5

@patch('app.services.bvg_client.requests.Session.get')
def test_make_request_success(mock_get, bvg_client):
    """Test successful API request"""
    mock_response = Mock()
    mock_response.json.return_value = {"test": "data"}
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    result = bvg_client._make_request("https://test.com")
    assert result == {"test": "data"}
    mock_get.assert_called_once()

@patch('app.services.bvg_client.requests.Session.get')
def test_make_request_timeout(mock_get, bvg_client):
    """Test API request with timeout"""
    import requests
    mock_get.side_effect = requests.exceptions.Timeout()
    
    result = bvg_client._make_request("https://test.com")
    assert result is None

@patch('app.services.bvg_client.requests.Session.get')
def test_make_request_connection_error(mock_get, bvg_client):
    """Test API request with connection error"""
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    result = bvg_client._make_request("https://test.com")
    assert result is None

@patch('app.services.bvg_client.BVGClient._make_request')
def test_search_stations(mock_request, bvg_client):
    """Test search stations method"""
    mock_request.return_value = [
        {"type": "stop", "id": "123", "name": "Test Station"},
        {"type": "address", "id": "456", "name": "Test Address"}
    ]
    
    result = bvg_client.search_stations("test")
    assert len(result) == 1  # Only stops should be returned
    assert result[0]["type"] == "stop"

@patch('app.services.bvg_client.BVGClient._make_request')
def test_search_stations_none_response(mock_request, bvg_client):
    """Test search stations with None response"""
    mock_request.return_value = None
    
    result = bvg_client.search_stations("test")
    assert result is None

@patch('app.services.bvg_client.BVGClient._make_request')
def test_get_departures(mock_request, bvg_client):
    """Test get departures method"""
    mock_request.return_value = {
        "stop": {"name": "Test Station"},
        "departures": [
            {"when": "2025-10-28T15:30:00", "direction": "North"}
        ]
    }
    
    result = bvg_client.get_departures("123")
    assert result is not None
    assert "stop" in result
    assert "departures" in result

@patch('app.services.bvg_client.BVGClient._make_request')
def test_get_departures_none_response(mock_request, bvg_client):
    """Test get departures with None response"""
    mock_request.return_value = None
    
    result = bvg_client.get_departures("123")
    assert result is None

def test_convert_to_utc(bvg_client):
    """Test timestamp conversion to UTC"""
    timestamp_ms = 1698508800000  # Oct 28, 2023 12:00:00 UTC
    result = bvg_client.convert_to_utc(timestamp_ms)
    assert result is not None
    assert isinstance(result, str)
    assert "T" in result  # ISO format

def test_convert_to_utc_none(bvg_client):
    """Test timestamp conversion with None"""
    result = bvg_client.convert_to_utc(None)
    assert result is None
