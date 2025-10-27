# backend/services/bvg_client.py
import httpx
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BVGClient:
    """Client for interacting with BVG Transport REST API"""
    
    def __init__(self, base_url: str = "https://v6.bvg.transport.rest"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
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
            response = await self.client.get(
                f"{self.base_url}/locations",
                params={
                    "query": query,
                    "results": results,
                    "stops": str(stops).lower(),
                    "addresses": str(addresses).lower(),
                    "poi": str(poi).lower()
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error searching locations: {e}")
            raise
    
    async def get_stop_departures(
        self,
        stop_id: str,
        duration: int = 60,
        results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get departures for a specific stop
        
        Args:
            stop_id: Stop ID (e.g., "900100003" for Alexanderplatz)
            duration: Show departures for how many minutes
            results: Maximum number of results
        """
        try:
            params = {"duration": duration}
            if results:
                params["results"] = results
            
            response = await self.client.get(
                f"{self.base_url}/stops/{stop_id}/departures",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting departures for stop {stop_id}: {e}")
            raise
    
    async def get_stop_info(self, stop_id: str) -> Dict[str, Any]:
        """Get detailed information about a stop"""
        try:
            response = await self.client.get(
                f"{self.base_url}/stops/{stop_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting stop info for {stop_id}: {e}")
            raise
    
    async def find_nearby_stops(
        self,
        latitude: float,
        longitude: float,
        distance: int = 1000,
        results: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Find stops near a location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            distance: Maximum walking distance in meters
            results: Maximum number of results
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/locations/nearby",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "distance": distance,
                    "results": results
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error finding nearby stops: {e}")
            raise
    
    async def get_journeys(
        self,
        from_id: str,
        to_id: str,
        results: int = 3
    ) -> Dict[str, Any]:
        """
        Get journey suggestions from A to B
        
        Args:
            from_id: Origin stop ID
            to_id: Destination stop ID
            results: Maximum number of journey options
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/journeys",
                params={
                    "from": from_id,
                    "to": to_id,
                    "results": results
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting journeys: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


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