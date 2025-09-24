from dotenv import load_dotenv, find_dotenv
import requests
import os
import json
import logging 
import time
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logging.info("Starting the BVG Radar Data Extraction")

load_dotenv(find_dotenv())
API_URL = os.getenv("BVG_API_BASE_URL")


def convert_to_utc(timestamp_ms):
    """Convert timestamp in milliseconds to UTC datetime string"""
    if timestamp_ms is None:
        return None
    try:
        # Convert milliseconds to seconds
        timestamp_seconds = timestamp_ms / 1000
        # Create UTC datetime
        utc_datetime = datetime.fromtimestamp(timestamp_seconds, tz=pytz.UTC)
        return utc_datetime.isoformat()
    except Exception as e:
        logging.warning(f"Failed to convert timestamp {timestamp_ms}: {e}")
        return timestamp_ms


def process_radar_data(data):
    """Process radar data to convert timestamps to UTC"""
    if isinstance(data, dict):
        processed_data = {}
        for key, value in data.items():
            if key == "realtimeDataUpdatedAt":
                processed_data[key] = convert_to_utc(value)
            elif isinstance(value, (dict, list)):
                processed_data[key] = process_radar_data(value)
            else:
                processed_data[key] = value
        return processed_data
    elif isinstance(data, list):
        return [process_radar_data(item) for item in data]
    else:
        return data


def get_radar(north, south, west, east, duration, frames, results=1, polylines=True):
    url = f"{API_URL}/radar?north={north}&south={south}&west={west}&east={east}&duration={duration}&frames={frames}&results={results}&polylines={polylines}"
    logging.info(f"Making request to: {url}")
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Response type: {type(data)}")
        logging.info(f"Response structure: {json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)[:500]}")
        
        # Process data to convert timestamps to UTC
        processed_data = process_radar_data(data)
        return processed_data
    else:
        logging.error(f"API request failed with status {response.status_code}: {response.text}")
        response.raise_for_status()


def display_vehicle_info(radar_data):
    print("\n🔍 Radar Data Analysis:\n")
    
    print(f"Data type: {type(radar_data)}")
    
    if isinstance(radar_data, dict):
        print("Response is a dictionary with keys:", list(radar_data.keys()))
        
        if 'movements' in radar_data:
            movements = radar_data['movements']
        elif 'vehicles' in radar_data:
            movements = radar_data['vehicles']
        elif 'data' in radar_data:
            movements = radar_data['data']
        else:
            print("Available keys:", list(radar_data.keys()))
            movements = radar_data
            
    elif isinstance(radar_data, list):
        print(f"Response is a list with {len(radar_data)} items")
        movements = radar_data
    else:
        print(f"Unexpected data type: {type(radar_data)}")
        print(f"Data content: {str(radar_data)[:200]}")
        return
    
    # Process movements
    if isinstance(movements, list) and len(movements) > 0:
        print(f"\n🚍 Found {len(movements)} vehicle movements:\n")
        
        for i, movement in enumerate(movements[:5]):  # Show first 5 only
            print(f"🚍 Vehicle #{i+1}")
            
            if isinstance(movement, dict):
                # Safe access with error handling
                line_info = movement.get("line", {})
                line_name = line_info.get("name", "N/A") if isinstance(line_info, dict) else str(line_info)
                
                trip_id = movement.get("tripId", "N/A")
                location = movement.get("location", {})
                
                if isinstance(location, dict):
                    latitude = location.get("latitude", "N/A")
                    longitude = location.get("longitude", "N/A")
                else:
                    latitude = longitude = "N/A"
                
                direction = movement.get("direction", "N/A")
                
                print(f"  Line: {line_name}")
                print(f"  Trip ID: {trip_id}")
                print(f"  Lat/Lon: {latitude}, {longitude}")
                print(f"  Direction: {direction}")
                
            elif isinstance(movement, str):
                print(f"  String data: {movement}")
            else:
                print(f"  Unexpected movement type: {type(movement)}")
                print(f"  Content: {str(movement)[:100]}")
            
            print("-" * 40)
            
        if len(movements) > 5:
            print(f"... and {len(movements) - 5} more vehicles")
    else:
        print("No movements found or movements is not a list")
        if movements:
            print(f"Movements type: {type(movements)}")
            print(f"Movements content: {str(movements)[:200]}")

if __name__ == "__main__":
    try:
        # Test with Berlin coordinates
        radar_data = get_radar(
            north=52.55,   # North Berlin
            south=52.45,   # South Berlin  
            west=13.35,    # West Berlin
            east=13.45,    # East Berlin
            duration=60,
            frames=10,
            results=1
        )
        display_vehicle_info(radar_data)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()