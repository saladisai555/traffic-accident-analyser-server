from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.predict_schema import LocationPredictInput, LocationPredictOutput
from app.schemas.dashboard_schema import (
    HotspotsOutput, 
    HotspotData, 
    IncidentLocation,
    TrafficFlowOutput,
    FlowSegment
)
from app.services.weather_service import get_weather
from app.services.traffic_service import get_traffic, get_traffic_incidents, get_traffic_flow
from app.services.model_service import predict
from app.utils.mapping import map_all_features
from app.utils.token import get_current_user
from app.database.mongo import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/predict-location", response_model=LocationPredictOutput)
async def predict_location(
    input_data: LocationPredictInput,
    current_user: str = Depends(get_current_user)
):
    try:
        weather = await get_weather(input_data.latitude, input_data.longitude)
        traffic = await get_traffic(input_data.latitude, input_data.longitude)
        features = map_all_features(weather, traffic, input_data.timestamp)
        prediction = predict(features)
        
        return LocationPredictOutput(
            **prediction,
            weather=weather,
            traffic=traffic,
            location={
                "latitude": input_data.latitude,
                "longitude": input_data.longitude,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Location prediction failed: {str(e)}",
        )


@router.get("/hotspots", response_model=HotspotsOutput)
async def get_hotspots(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    current_user: str = Depends(get_current_user)
):
    """
    Get real-time traffic incidents (accidents, closures, construction, etc.) from HERE Traffic API.
    
    Args:
        latitude: Center latitude for search
        longitude: Center longitude for search
        radius: Search radius in meters (default: 5000m = 5km, max: 50000m)
    
    Returns:
        Real-time incidents with location, type, severity, and description
    """
    try:
        if radius > 50000:
            radius = 50000
        elif radius < 100:
            radius = 100
        
        raw_incidents = await get_traffic_incidents(latitude, longitude, radius)
        print(f"Raw incidents: {raw_incidents}")
        
        incidents = []
        for incident in raw_incidents:
            location_data = incident.get("location", {})
            geometry = location_data.get("geometry", {})
            
            coords = geometry.get("coordinates", [])
            inc_lat, inc_lon = latitude, longitude
            
            if geometry.get("type") == "Point" and len(coords) >= 2:
                inc_lon, inc_lat = coords[0], coords[1]
            elif geometry.get("type") == "LineString" and len(coords) > 0:
                inc_lon, inc_lat = coords[0][0], coords[0][1]
            
            incident_details = incident.get("incidentDetails", {})
            validity = incident.get("validity", {})
            
            incidents.append(
                HotspotData(
                    id=incident.get("id", "unknown"),
                    type=incident_details.get("type", "UNKNOWN"),
                    severity=incident.get("severity"),
                    impact=incident.get("impact"),
                    description=incident.get("description", "No description available"),
                    location=IncidentLocation(
                        latitude=inc_lat,
                        longitude=inc_lon,
                        description=location_data.get("description")
                    ),
                    start_time=validity.get("startTime"),
                    end_time=validity.get("endTime"),
                    last_updated=incident.get("lastUpdatedTime"),
                    geometry=geometry if geometry else None
                )
            )
        
        return HotspotsOutput(
            incidents=incidents,
            total_incidents=len(incidents),
            search_radius=radius,
            center=IncidentLocation(
                latitude=latitude,
                longitude=longitude
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch hotspots: {str(e)}",
        )


@router.get("/traffic-flow", response_model=TrafficFlowOutput)
async def get_traffic_flow_data(
    latitude: float,
    longitude: float,
    radius: int = 1000,
    current_user: str = Depends(get_current_user)
):
    """
    Get real-time traffic flow data (speeds, congestion, jam factor) from HERE Traffic API.
    
    Args:
        latitude: Center latitude for search
        longitude: Center longitude for search
        radius: Search radius in meters (default: 2000m = 2km, max: 10000m)
    
    Returns:
        Real-time traffic flow for road segments with speeds and congestion levels
    """
    try:
        if radius > 10000:
            radius = 10000
        elif radius < 100:
            radius = 100
        
        raw_flow = await get_traffic_flow(latitude, longitude, radius)
        # print(f"Raw flow: {raw_flow}")
        
        flow_segments = []
        for segment in raw_flow:
            location_data = segment.get("location", {})
            current_flow = segment.get("currentFlow", {})
            
            shape_data = location_data.get("shape", {})
            shape_points = []
            seg_lat, seg_lon = latitude, longitude
            
            if isinstance(shape_data, dict) and "links" in shape_data:
                links = shape_data.get("links", [])
                for link in links:
                    points = link.get("points", [])
                    shape_points.extend(points)
                
                if shape_points:
                    seg_lat = shape_points[0].get("lat", latitude)
                    seg_lon = shape_points[0].get("lng", longitude)
            
            flow_segments.append(
                FlowSegment(
                    location_id=location_data.get("id"),
                    latitude=seg_lat,
                    longitude=seg_lon,
                    current_speed=current_flow.get("speed", 0),
                    free_flow_speed=current_flow.get("freeFlowSpeed", 0),
                    jam_factor=current_flow.get("jamFactor", 0),
                    confidence=current_flow.get("confidence"),
                    length=location_data.get("length"),
                    shape=shape_points if shape_points else None
                )
            )
        
        return TrafficFlowOutput(
            flow_segments=flow_segments,
            total_segments=len(flow_segments),
            search_radius=radius,
            center=IncidentLocation(
                latitude=latitude,
                longitude=longitude
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch traffic flow: {str(e)}",
        )
