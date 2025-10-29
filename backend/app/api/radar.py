"""
API endpoints for vehicle radar (real-time vehicle positions)
"""
from fastapi import APIRouter, HTTPException, Query, Depends
import logging

from app.services.bvg_client import get_bvg_client, BVGClient

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/radar/vehicles")
async def get_vehicles_radar(
    north: float = Query(..., description="North latitude boundary"),
    south: float = Query(..., description="South latitude boundary"),
    west: float = Query(..., description="West longitude boundary"),
    east: float = Query(..., description="East longitude boundary"),
    duration: int = Query(30, ge=10, le=120, description="Duration in seconds"),
    results: int = Query(50, ge=1, le=256, description="Maximum number of vehicles"),
    client: BVGClient = Depends(get_bvg_client)
):
    """
    Get real-time vehicle positions (buses, trams, trains) within a geographic area.
    
    Example: Berlin city center
    - north: 52.55
    - south: 52.48
    - west: 13.35
    - east: 13.45
    """
    try:
        logger.info(f"Getting radar data for bounds: N={north}, S={south}, W={west}, E={east}")
        
        # Call BVG API radar
        data = client.get_radar(
            north=north,
            south=south,
            west=west,
            east=east,
            duration=duration,
            frames=1,  # Solo necesitamos 1 frame para posición actual
            results=results,
            polylines=False  # No necesitamos polylines para el mapa
        )
        
        if data is None:
            raise HTTPException(
                status_code=503,
                detail="El servicio de radar BVG no está disponible en este momento."
            )
        
        # Procesar y estructurar los datos para el frontend
        vehicles = []
        if isinstance(data, dict) and 'movements' in data:
            for movement in data['movements']:
                if 'location' in movement and movement['location']:
                    vehicle = {
                        'line': movement.get('line', {}),
                        'direction': movement.get('direction'),
                        'location': movement['location'],
                        'tripId': movement.get('tripId'),
                        'nextStopovers': movement.get('nextStopovers', [])[:3]  # Solo próximas 3 paradas
                    }
                    vehicles.append(vehicle)
        
        return {
            'vehicles': vehicles,
            'count': len(vehicles),
            'bounds': {
                'north': north,
                'south': south,
                'west': west,
                'east': east
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting radar data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
