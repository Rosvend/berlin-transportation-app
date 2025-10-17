"""
API endpoints for departure information
"""
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional
import logging

from app.services.bvg_client import get_bvg_client, BVGClient
from app.models.transport import DeparturesResponse, Departure, TransportLine, Station

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/departures/{station_id}", response_model=DeparturesResponse)
async def get_departures(
    station_id: str = Path(..., description="Station ID"),
    duration: int = Query(60, ge=10, le=240, description="Duration in minutes to fetch departures"),
    bvg_client: BVGClient = Depends(get_bvg_client)
):
    """Get live departures for a station"""
    try:
        # Call BVG API with correct method name
        results = await bvg_client.get_stop_departures(station_id, duration=duration)
        
        if results is None:
            raise HTTPException(status_code=503, detail="BVG API unavailable")
        
        if not results:
            raise HTTPException(status_code=404, detail="Station not found")
        
        # Convert to our models
        departures = []
        
        # Handle different response structures from BVG API
        departures_data = results.get('departures', [])
        if isinstance(departures_data, list):
            for dep in departures_data:
                try:
                    # Extract line information
                    line_data = dep.get('line', {})
                    line = TransportLine(
                        name=line_data.get('name', 'Unknown'),
                        type=line_data.get('product', {}).get('short', 'unknown') if isinstance(line_data.get('product'), dict) else line_data.get('product', 'unknown')
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
                    logger.warning(f"Failed to process departure: {e}")
                    continue
        
        # Create station info
        station = Station(
            id=station_id,
            name=results.get('stop', {}).get('name', f'Station {station_id}'),
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
        logger.error(f"Failed to get departures for {station_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
