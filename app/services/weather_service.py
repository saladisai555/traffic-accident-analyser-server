import httpx
from app.config import settings


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather(latitude: float, longitude: float) -> dict:
    if not settings.openweather_api_key:
        return {
            "temp": 20,
            "weather_main": "Clear",
            "rain_mm": 0,
            "humidity": 50,
            "wind_speed": 5,
            "feels_like": 20,
            "visibility": 10000,
            "pressure": 1013,
            "clouds": 0,
        }
    
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": settings.openweather_api_key,
        "units": "metric",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "temp": data["main"]["temp"],
                "weather_main": data["weather"][0]["main"],
                "rain_mm": data.get("rain", {}).get("1h", 0),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"],
                "visibility": data["visibility"],
                "pressure": data["main"]["pressure"],
                "clouds": data["clouds"]["all"],
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return {
                "temp": 20,
                "weather_main": "Clear",
                "rain_mm": 0,
                "humidity": 50,
                "wind_speed": 5,
                "feels_like": 20,
                "visibility": 10000,
                "pressure": 1013,
                "clouds": 0,
            }


async def get_hourly_forecast(latitude: float, longitude: float) -> list:
    # Hourly forecast not available in free 2.5 API
    return []


async def get_daily_forecast(latitude: float, longitude: float) -> list:
    # Daily forecast not available in free 2.5 API
    return []