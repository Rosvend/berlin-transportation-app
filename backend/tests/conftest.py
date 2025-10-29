"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.bvg_client import initialize_bvg_client

@pytest.fixture(scope="session", autouse=True)
def setup_bvg_client():
    """Initialize BVG client for all tests"""
    initialize_bvg_client()
    yield

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def mock_bvg_stations_response():
    """Mock response for BVG stations search"""
    return [
        {
            "type": "stop",
            "id": "900000100003",
            "name": "S+U Alexanderplatz",
            "location": {
                "latitude": 52.521508,
                "longitude": 13.413267
            }
        },
        {
            "type": "stop",
            "id": "900000003201",
            "name": "S+U Potsdamer Platz",
            "location": {
                "latitude": 52.509458,
                "longitude": 13.376461
            }
        }
    ]

@pytest.fixture
def mock_bvg_departures_response():
    """Mock response for BVG departures"""
    return {
        "stop": {
            "type": "stop",
            "id": "900000100003",
            "name": "S+U Alexanderplatz"
        },
        "departures": [
            {
                "when": "2025-10-28T15:30:00+02:00",
                "direction": "Pankow",
                "line": {
                    "name": "U2",
                    "product": {
                        "short": "subway"
                    }
                },
                "delay": 120,
                "platform": "1"
            },
            {
                "when": "2025-10-28T15:35:00+02:00",
                "direction": "Ruhleben",
                "line": {
                    "name": "U2",
                    "product": {
                        "short": "subway"
                    }
                },
                "delay": None,
                "platform": "2"
            }
        ]
    }
