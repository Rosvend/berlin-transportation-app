"""
Pydantic models for transport data validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Location(BaseModel):
    """Geographic location"""
    latitude: float
    longitude: float

class TransportLine(BaseModel):
    """Transport line information"""
    name: str
    type: str  # "bus", "tram", "subway", "train", etc.
    color: Optional[str] = None

class Station(BaseModel):
    """Transport station/stop"""
    id: str
    name: str
    location: Optional[Location] = None
    type: str = "stop"

class Departure(BaseModel):
    """Departure information"""
    line: TransportLine
    direction: str
    when: str  # ISO datetime string
    delay: Optional[int] = None  # delay in seconds
    platform: Optional[str] = None
    remarks: Optional[List[str]] = []

class DeparturesResponse(BaseModel):
    """API response for station departures"""
    station: Station
    departures: List[Departure]
    realtimeDataUpdatedAt: Optional[str] = None

class StationSearchResponse(BaseModel):
    """API response for station search"""
    stations: List[Station]
    query: str

class VehicleMovement(BaseModel):
    """Vehicle movement from radar data"""
    line: TransportLine
    trip_id: Optional[str] = None
    location: Location
    direction: Optional[str] = None
    realtime_data_updated_at: Optional[str] = None

class RadarResponse(BaseModel):
    """API response for radar data"""
    movements: List[VehicleMovement]
