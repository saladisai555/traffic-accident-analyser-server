from fastapi import APIRouter, HTTPException
from app.services.weather_service import get_weather

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/test")
async def test_weather():
    return {
        "message": "Weather API integration working",
        "status": "ready",
    }


@router.get("/current")
async def get_current_weather(lat: float, lon: float):
    try:
        weather = await get_weather(lat, lon)
        return weather
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather: {str(e)}")
