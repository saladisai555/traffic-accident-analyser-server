from datetime import datetime, timezone


def map_weather_to_condition(weather_main: str) -> str:
    weather_lower = weather_main.lower()
    if weather_lower in ["clear", "clouds"]:
        return "Clear"
    elif weather_lower in ["rain", "drizzle", "thunderstorm"]:
        return "Rainy"
    elif weather_lower == "fog" or weather_lower == "mist":
        return "Foggy"
    elif weather_lower == "snow":
        return "Snowy"
    else:
        return "Clear"


def map_road_condition(weather_main: str, rain_mm: float, temp: float) -> str:
    weather_lower = weather_main.lower()
    
    if temp < 0:
        return "Icy"
    elif weather_lower in ["rain", "drizzle", "thunderstorm"] or rain_mm > 0:
        return "Wet"
    else:
        return "Dry"


def get_time_of_day(hour: int) -> str:
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def get_light_condition(hour: int) -> str:
    if 6 <= hour < 18:
        return "Daylight"
    elif 18 <= hour < 22:
        return "Artificial Light"
    else:
        return "No Light"


def build_model_features(
    weather_data: dict,
    traffic_data: dict,
    user_input: dict,
    timestamp: datetime = None
) -> dict:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    hour = timestamp.hour
    weather_main = weather_data.get("weather_main", "Clear")
    rain_mm = weather_data.get("rain_mm", 0)
    temp = weather_data.get("temp", 20)
    
    return {
        "Weather": map_weather_to_condition(weather_main),
        "Road_Type": user_input.get("road_type", "City Road"),
        "Time_of_Day": get_time_of_day(hour),
        "Traffic_Density": traffic_data.get("traffic_density", 0),
        "Speed_Limit": user_input.get("speed_limit", 50),
        "Number_of_Vehicles": user_input.get("number_of_vehicles", 2),
        "Driver_Alcohol": user_input.get("driver_alcohol", 0),
        "Road_Condition": map_road_condition(weather_main, rain_mm, temp),
        "Vehicle_Type": user_input.get("vehicle_type", "Car"),
        "Driver_Age": user_input.get("driver_age", 35),
        "Driver_Experience": user_input.get("driver_experience", 10),
        "Road_Light_Condition": get_light_condition(hour),
        "Accident": traffic_data.get("nearby_accidents", 0)
    }


def map_all_features(
    weather_data: dict,
    traffic_data: dict,
    location_timestamp: str | None = None,
) -> dict:
    if location_timestamp:
        dt = datetime.fromisoformat(location_timestamp)
    else:
        dt = datetime.now(timezone.utc)
    
    hour = dt.hour
    weather_main = weather_data.get("weather_main", "Clear")
    rain_mm = weather_data.get("rain_mm", 0)
    temp = weather_data.get("temp", 20)
    
    return {
        "Weather": map_weather_to_condition(weather_main),
        "Road_Type": "City Road",
        "Time_of_Day": get_time_of_day(hour),
        "Traffic_Density": traffic_data.get("traffic_density", 0),
        "Speed_Limit": 50,
        "Number_of_Vehicles": 2,
        "Driver_Alcohol": 0,
        "Road_Condition": map_road_condition(weather_main, rain_mm, temp),
        "Vehicle_Type": "Car",
        "Driver_Age": 35,
        "Driver_Experience": 10,
        "Road_Light_Condition": get_light_condition(hour)
    }
