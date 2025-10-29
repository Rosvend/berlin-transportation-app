"""
BVG API Client Service
Refactored from extract/departures.py for web application use
OPTIMIZED: Reduced timeout and retries for better performance
"""
import os
import requests
import logging
from datetime import datetime
import pytz
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
import time
from app.utils.cache import cached

logger = logging.getLogger(__name__)

class BVGClient:
    """Client for interacting with BVG Transport REST API"""
    
    def __init__(self):
        self.api_url = os.getenv("BVG_API_BASE_URL", "https://v6.bvg.transport.rest")
        self.session = requests.Session()
        # OPTIMIZED: Reduced timeout from 10s to 5s for faster failures
        self.timeout = 5
        # OPTIMIZED: Reduced retries from 3 to 1 (fail-fast approach)
        self.max_retries = 1
        self.retry_delay = 0.5  # seconds (reduced from 1s)
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making request (attempt {attempt + 1}/{self.max_retries}): {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"Request timeout (attempt {attempt + 1}): {e}")
            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error: {e}")
                    return None
                last_error = e
                logger.warning(f"HTTP error (attempt {attempt + 1}): {e}")
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                return None
            
            # Wait before retrying (except on last attempt)
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        logger.error(f"All retry attempts failed. Last error: {last_error}")
        return None
    
    async def search_locations(
        self, 
        query: str, 
        results: int = 10,
        stops: bool = True,
        addresses: bool = False,
        poi: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for stops, addresses, or POIs
        
        Args:
            query: Search term (e.g., "alexanderplatz")
            results: Maximum number of results
            stops: Include stops/stations
            addresses: Include addresses
            poi: Include points of interest
        """
        try:
            data = self._make_request(url)
            if data:
                processed_data = self.process_radar_data(data)
                return processed_data
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_radar: {e}")
            return None
    
    @cached(ttl=300)  # Cache for 5 minutes
    def search_stations(self, query: str, results: int = 10) -> Optional[List[Dict]]:
        """Search for stations by name - CACHED"""
        url = f"{self.api_url}/locations?query={query}&results={results}"
        
        Args:
            stop_id: Stop ID (e.g., "900100003" for Alexanderplatz)
            duration: Show departures for how many minutes
            results: Maximum number of results
        """
        try:
            logger.info(f"Searching stations: {query}")
            data = self._make_request(url)
            
            if data is None:
                return None
            
            # Filter only stations/stops
            if isinstance(data, list):
                stations = [item for item in data if item.get('type') == 'stop']
                return stations
            return []
            
        except Exception as e:
            logger.error(f"Unexpected error in search_stations: {e}")
            return None
    
    @cached(ttl=60)  # Cache for 1 minute (departures change frequently)
    def get_departures(self, station_id: str, duration: int = 60) -> Optional[Dict]:
        """Get departures for a specific station - CACHED"""
        url = f"{self.api_url}/stops/{station_id}/departures?duration={duration}"
        
        try:
            logger.info(f"Getting departures for station: {station_id}")
            data = self._make_request(url)
            
            if data is None:
                return None
            
            # Process departure times
            if isinstance(data, dict) and 'departures' in data:
                for departure in data['departures']:
                    if 'when' in departure:
                        # Convert ISO string to more readable format if needed
                        pass
                    if 'delay' in departure:
                        # Process delay information
                        pass
            
            return data
            
        except Exception as e:
            logger.error(f"Unexpected error in get_departures: {e}")
            return None


# Global singleton instance
_bvg_client: Optional[BVGClient] = None


def get_bvg_client() -> BVGClient:
    """
    Get the global BVG client instance.
    This function should be used as a FastAPI dependency.
    """
    global _bvg_client
    if _bvg_client is None:
        raise RuntimeError("BVG client not initialized. Call initialize_bvg_client() first.")
    return _bvg_client


def initialize_bvg_client(base_url: str = "https://v6.bvg.transport.rest") -> None:
    """Initialize the global BVG client instance"""
    global _bvg_client
    _bvg_client = BVGClient(base_url)


async def shutdown_bvg_client() -> None:
    """Shutdown the global BVG client instance"""
    global _bvg_client
    if _bvg_client is not None:
        await _bvg_client.close()
        _bvg_client = None