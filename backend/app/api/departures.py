"""
API endpoints for departure information
"""
from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
import logging

from app.services.bvg_client import bvg_client
from app.models.transport import DeparturesResponse, Departure, TransportLine, Station

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/departures/{station_id}")
async def get_departures(
    station_id: str = Path(..., description="Station ID"),
    duration: int = Query(60, ge=10, le=240, description="Duration in minutes to fetch departures")
):
    """Get live departures for a station"""
    try:
        # Call BVG API
        results = bvg_client.get_departures(station_id, duration)
        
        if results is None:
            raise HTTPException(
                status_code=503, 
                detail="El servicio de BVG no está disponible en este momento. Por favor, intenta de nuevo en unos segundos."
            )
        
        if not results:
            raise HTTPException(status_code=404, detail="Estación no encontrada")
        
        # Convert to our models
        departures = []
        
        # Handle different response structures from BVG API
        departures_data = results.get('departures', [])
        if isinstance(departures_data, list):
            for dep in departures_data:
                try:
                    # Skip if dep is not a dict
                    if not isinstance(dep, dict):
                        logger.warning(f"Skipping non-dict departure: {type(dep)}")
                        continue
                    
                    # Extract line information safely
                    line_data = dep.get('line', {})
                    if not isinstance(line_data, dict):
                        line_data = {}
                    
                    product_data = line_data.get('product', {})
                    if not isinstance(product_data, dict):
                        product_data = {}
                    
                    line = TransportLine(
                        name=line_data.get('name', 'Unknown'),
                        type=product_data.get('short', 'unknown')
                    )
                    
                    # Create departure
                    departure = Departure(
                        line=line,
                        direction=dep.get('direction', 'Unknown'),
                        when=dep.get('when', ''),
                        delay=dep.get('delay'),
                        platform=dep.get('platform')
                    )
                    
                    departures.append(departure)
                    
                except Exception as e:
                    logger.warning(f"Failed to process departure: {e} - {type(dep)}")
                    continue
        
        # Create station info
        station_data = results.get('stop', {})
        if not isinstance(station_data, dict):
            station_data = {}
            
        station = Station(
            id=station_id,
            name=station_data.get('name', f'Station {station_id}'),
            type='stop'
        )
        
        response = DeparturesResponse(
            station=station,
            departures=departures,
            realtimeDataUpdatedAt=results.get('realtimeDataUpdatedAt')
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get departures for {station_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
