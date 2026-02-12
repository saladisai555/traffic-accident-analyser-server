from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.schemas.predict_schema import PredictInput, PredictOutput
from app.services.model_service import predict
from app.services.weather_service import get_weather
from app.services.traffic_service import get_traffic
from app.utils.mapping import build_model_features
from app.utils.token import get_current_user

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictOutput)
async def predict_risk(
    input_data: PredictInput,
    current_user: str = Depends(get_current_user)
):
    try:
        weather = await get_weather(input_data.latitude, input_data.longitude)
        traffic = await get_traffic(input_data.latitude, input_data.longitude)
        
        timestamp = datetime.now(timezone.utc)
        
        user_input = {
            "road_type": input_data.road_type,
            "speed_limit": input_data.speed_limit,
            "number_of_vehicles": input_data.number_of_vehicles,
            "driver_alcohol": input_data.driver_alcohol,
            "vehicle_type": input_data.vehicle_type,
            "driver_age": input_data.driver_age,
            "driver_experience": input_data.driver_experience
        }
        
        features = build_model_features(weather, traffic, user_input, timestamp)
        result = predict(features)
        
        return PredictOutput(
            severity=result["severity"],
            probabilities=result["probabilities"],
            confidence=result["confidence"],
            weather=weather,
            traffic=traffic,
            location={
                "latitude": input_data.latitude,
                "longitude": input_data.longitude
            },
            timestamp=timestamp.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )
