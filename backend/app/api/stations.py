"""
API endpoints for station search and information
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging

from app.services.bvg_client import get_bvg_client, BVGClient
from app.models.transport import Station, StationSearchResponse, Location

router = APIRouter()
logger = logging.getLogger(__name__)

# Featured stations from your config
FEATURED_STATIONS = [
    {"id": "900000100003", "name": "S+U Alexanderplatz", "type": "major_hub"},
    {"id": "900000003201", "name": "S+U Potsdamer Platz", "type": "major_hub"},
    {"id": "900000024101", "name": "S+U Friedrichstr.", "type": "major_hub"},
    {"id": "900000100001", "name": "S+U Zoologischer Garten", "type": "major_hub"},
    {"id": "900000100004", "name": "S Hackescher Markt", "type": "regional_hub"},
]

@router.get("/stations/all")
async def get_all_stations():
    """Get all available stations"""
    try:
        # Por ahora, devolvemos las estaciones destacadas
        return FEATURED_STATIONS
    except Exception as e:
        logger.error(f"Error getting all stations: {e}")
        raise HTTPException(status_code=500, detail="Error getting stations")

@router.get("/stations/search")
async def search_stations(
    q: str = Query(..., description="Search query for station name", min_length=2),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    bvg_client: BVGClient = Depends(get_bvg_client)
):
    """Search for stations by name"""
    try:
        # Call BVG API with correct method name
        results = bvg_client.search_stations(q, results=limit)
        
        if results is None:
            raise HTTPException(
                status_code=503, 
                detail="El servicio de BVG no está disponible en este momento. Por favor, intenta de nuevo en unos segundos."
            )
        
        # Convert to our Station model
        stations = []
        for result in results:
            station = Station(
                id=result.get('id', ''),
                name=result.get('name', ''),
                type=result.get('type', 'stop')
            )
            
            # Add location if available
            if 'location' in result and result['location']:
                station.location = Location(
                    latitude=result['location'].get('latitude', 0),
                    longitude=result['location'].get('longitude', 0)
                )
            
            stations.append(station)
        
        return StationSearchResponse(stations=stations, query=q)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Station search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stations/featured")
async def get_featured_stations():
    """Get list of featured major stations"""
    try:
        stations = []
        for station_data in FEATURED_STATIONS:
            station = Station(
                id=station_data["id"],
                name=station_data["name"],
                type=station_data["type"]
            )
            stations.append(station)
        
        return {"stations": stations}
        
    except Exception as e:
        logger.error(f"Failed to get featured stations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stations/{station_id}")
async def get_station_info(station_id: str):
    """Get information about a specific station"""
    try:
        # Return basic station structure
        # In a real app, this might query a database of stations
        station = Station(
            id=station_id,
            name=f"Station {station_id}",
            type="stop"
        )
        
        return station
        
    except Exception as e:
        logger.error(f"Failed to get station info for {station_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

