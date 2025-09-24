"""
BVG API Client Service
Refactored from extract/departures.py for web application use
"""
import os
import requests
import logging
from datetime import datetime
import pytz
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class BVGClient:
    """Client for interacting with BVG Transport API"""
    
    def __init__(self):
        self.api_url = os.getenv("BVG_API_BASE_URL", "https://v6.bvg.transport.rest")
        self.session = requests.Session()
        # Set a reasonable timeout
        self.session.timeout = 10
    
    def convert_to_utc(self, timestamp_ms: Optional[int]) -> Optional[str]:
        """Convert timestamp in milliseconds to UTC datetime string"""
        if timestamp_ms is None:
            return None
        try:
            timestamp_seconds = timestamp_ms / 1000
            utc_datetime = datetime.fromtimestamp(timestamp_seconds, tz=pytz.UTC)
            return utc_datetime.isoformat()
        except Exception as e:
            logger.warning(f"Failed to convert timestamp {timestamp_ms}: {e}")
            return None
    
    def process_radar_data(self, data: Union[Dict, List]) -> Union[Dict, List]:
        """Process radar data to convert timestamps to UTC"""
        if isinstance(data, dict):
            processed_data = {}
            for key, value in data.items():
                if key == "realtimeDataUpdatedAt":
                    processed_data[key] = self.convert_to_utc(value)
                elif isinstance(value, (dict, list)):
                    processed_data[key] = self.process_radar_data(value)
                else:
                    processed_data[key] = value
            return processed_data
        elif isinstance(data, list):
            return [self.process_radar_data(item) for item in data]
        else:
            return data
    
    def get_radar(self, north: float, south: float, west: float, east: float, 
                  duration: int = 60, frames: int = 10, results: int = 50, 
                  polylines: bool = True) -> Optional[Dict]:
        """Get vehicle radar data for specified geographic area"""
        url = (f"{self.api_url}/radar?"
               f"north={north}&south={south}&west={west}&east={east}&"
               f"duration={duration}&frames={frames}&results={results}&"
               f"polylines={polylines}")
        
        try:
            logger.info(f"Making radar request to: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            processed_data = self.process_radar_data(data)
            return processed_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Radar API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_radar: {e}")
            return None
    
    def search_stations(self, query: str, results: int = 10) -> Optional[List[Dict]]:
        """Search for stations by name"""
        url = f"{self.api_url}/locations?query={query}&results={results}"
        
        try:
            logger.info(f"Searching stations: {query}")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter only stations/stops
            if isinstance(data, list):
                stations = [item for item in data if item.get('type') == 'stop']
                return stations
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Station search failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in search_stations: {e}")
            return None
    
    def get_departures(self, station_id: str, duration: int = 60) -> Optional[Dict]:
        """Get departures for a specific station"""
        url = f"{self.api_url}/stops/{station_id}/departures?duration={duration}"
        
        try:
            logger.info(f"Getting departures for station: {station_id}")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
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
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Departures API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in get_departures: {e}")
            return None

# Create a global instance
bvg_client = BVGClient()
