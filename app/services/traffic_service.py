import httpx
from datetime import datetime
from app.config import settings
import asyncio

def map_jam_factor_to_density(jam_factor: float) -> int:
    if jam_factor <= 3.0:
        return 0
    elif jam_factor <= 7.0:
        return 1
    else:
        return 2


def get_traffic_density_from_time(hour: int, day_of_week: int) -> int:
    is_weekend = day_of_week >= 5
    
    if is_weekend:
        if 10 <= hour <= 20:
            return 1
        return 0
    
    if (7 <= hour <= 9) or (17 <= hour <= 19):
        return 2
    elif (10 <= hour <= 16) or (20 <= hour <= 22):
        return 1
    else:
        return 0


async def get_traffic(latitude: float, longitude: float) -> dict:
    if not settings.traffic_api_key:
        now = datetime.now()
        density = get_traffic_density_from_time(now.hour, now.weekday())
        return {
            "traffic_density": density,
            "jam_factor": density * 3.5,
            "current_speed": 50,
            "free_flow_speed": 60,
            "confidence": 0.3,
            "nearby_accidents": 0,
            "source": "time_based"
        }
    
    try:
        flow_task = _get_here_flow_v7(latitude, longitude)
        incidents_task = _get_here_incidents_v7(latitude, longitude)
        
        flow_data, incidents_data = await asyncio.gather(flow_task, incidents_task, return_exceptions=True)
        
        if isinstance(flow_data, Exception):
            now = datetime.now()
            density = get_traffic_density_from_time(now.hour, now.weekday())
            flow_data = {
                "traffic_density": density,
                "jam_factor": density * 3.5,
                "current_speed": 50,
                "free_flow_speed": 60,
                "confidence": 0.3,
                "source": "time_based_fallback"
            }
        
        if isinstance(incidents_data, Exception):
            incidents_data = {"accident_count": 0}
        
        flow_data["nearby_accidents"] = incidents_data.get("accident_count", 0)
        return flow_data
        
    except Exception as e:
        print(f"Error fetching HERE traffic, using time-based fallback: {e}")
        now = datetime.now()
        density = get_traffic_density_from_time(now.hour, now.weekday())
        return {
            "traffic_density": density,
            "jam_factor": density * 3.5,
            "current_speed": 50,
            "free_flow_speed": 60,
            "confidence": 0.3,
            "nearby_accidents": 0,
            "source": "time_based_fallback"
        }


async def _get_here_flow_v7(latitude: float, longitude: float) -> dict:
    url = "https://data.traffic.hereapi.com/v7/flow"
    params = {
        "apiKey": settings.traffic_api_key,
        "in": f"circle:{latitude},{longitude};r=500",
        "locationReferencing": "shape"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            flow = result.get("currentFlow", {})
            
            current_speed = flow.get("speed", 50)
            free_flow_speed = flow.get("freeFlowSpeed", 60)
            jam_factor = flow.get("jamFactor", 0)
            confidence = flow.get("confidence", 0.7)
            
            traffic_density = map_jam_factor_to_density(jam_factor)
            
            return {
                "traffic_density": traffic_density,
                "jam_factor": jam_factor,
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed,
                "confidence": confidence,
                "source": "here_api"
            }
        
        now = datetime.now()
        density = get_traffic_density_from_time(now.hour, now.weekday())
        return {
            "traffic_density": density,
            "jam_factor": density * 3.5,
            "current_speed": 50,
            "free_flow_speed": 60,
            "confidence": 0.3,
            "nearby_accidents": 0,
            "source": "time_based"
        }


async def _get_here_incidents_v7(latitude: float, longitude: float) -> dict:
    url = "https://data.traffic.hereapi.com/v7/incidents"
    params = {
        "apiKey": settings.traffic_api_key,
        "in": f"circle:{latitude},{longitude};r=2000",
        "locationReferencing": "shape"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        incidents = data.get("results", [])
        accident_count = sum(1 for i in incidents if i.get("incidentDetails", {}).get("type") == "ACCIDENT")
        
        return {
            "total_incidents": len(incidents),
            "accident_count": accident_count
        }


async def get_traffic_incidents(latitude: float, longitude: float, radius: int = 5000) -> list:
    """
    Fetch real-time traffic incidents from HERE Traffic API v7.
    Returns detailed incident information including location, type, severity, and description.
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius: Search radius in meters (default: 5000m = 5km)
    
    Returns:
        List of incident dictionaries with full details
    """
    if not settings.traffic_api_key:
        raise Exception("Traffic API key not configured")
    
    try:
        url = "https://data.traffic.hereapi.com/v7/incidents"
        params = {
            "apiKey": settings.traffic_api_key,
            "in": f"circle:{latitude},{longitude};r={radius}",
            "locationReferencing": "shape"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                error_text = response.text[:200]
                raise Exception(f"HERE API error (status {response.status_code}): {error_text}")
            
            data = response.json()
            return data.get("results", [])
    
    except httpx.TimeoutException:
        raise Exception("Timeout connecting to HERE Traffic API")
    except httpx.RequestError as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch incidents: {str(e)}")


async def get_traffic_flow(latitude: float, longitude: float, radius: int = 1000) -> list:
    """
    Fetch real-time traffic flow data from HERE Traffic API v7.
    Returns detailed flow information for road segments including speeds and congestion.
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius: Search radius in meters (default: 1000m = 1km)
    
    Returns:
        List of flow data dictionaries with segment details
    """
    if not settings.traffic_api_key:
        raise Exception("Traffic API key not configured")
    
    try:
        url = "https://data.traffic.hereapi.com/v7/flow"
        params = {
            "apiKey": settings.traffic_api_key,
            "in": f"circle:{latitude},{longitude};r={radius}",
            "locationReferencing": "shape"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                error_text = response.text[:200]
                raise Exception(f"HERE API error (status {response.status_code}): {error_text}")
            
            data = response.json()
            return data.get("results", [])
    
    except httpx.TimeoutException:
        raise Exception("Timeout connecting to HERE Traffic API")
    except httpx.RequestError as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch traffic flow: {str(e)}")