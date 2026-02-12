from pydantic import BaseModel
from typing import List, Optional, Any, Dict


class IncidentLocation(BaseModel):
    latitude: float
    longitude: float
    description: Optional[str] = None


class HotspotData(BaseModel):
    id: str
    type: str  # ACCIDENT, CONSTRUCTION, ROAD_CLOSED, etc.
    severity: Optional[int] = None  # 0-10 or provider specific
    impact: Optional[str] = None  # LOW, MEDIUM, HIGH
    description: str
    location: IncidentLocation
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    last_updated: Optional[str] = None
    geometry: Optional[Dict[str, Any]] = None  # GeoJSON geometry


class FlowSegment(BaseModel):
    location_id: Optional[str] = None
    latitude: float
    longitude: float
    current_speed: float  # m/s
    free_flow_speed: float  # m/s
    jam_factor: float  # 0-10
    confidence: Optional[float] = None
    length: Optional[float] = None  # meters
    shape: Optional[List[Dict[str, float]]] = None  # [{lat, lng}, ...]


class HotspotsOutput(BaseModel):
    incidents: List[HotspotData]
    total_incidents: int
    search_radius: int  # in meters
    center: IncidentLocation


class TrafficFlowOutput(BaseModel):
    flow_segments: List[FlowSegment]
    total_segments: int
    search_radius: int
    center: IncidentLocation
