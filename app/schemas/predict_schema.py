from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PredictInput(BaseModel):
    latitude: float
    longitude: float
    road_type: str = Field(..., description="Highway, City Road, Rural Road, Mountain Road")
    speed_limit: int = Field(..., ge=0, le=200, description="Speed limit in km/h")
    number_of_vehicles: int = Field(..., ge=1, le=5)
    driver_alcohol: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    vehicle_type: str = Field(..., description="Car, Truck, Bus, Motorcycle")
    driver_age: int = Field(..., ge=18, le=70)
    driver_experience: int = Field(..., ge=0, le=50, description="Years of experience")


class PredictOutput(BaseModel):
    severity: str
    probabilities: dict
    confidence: float
    weather: dict
    traffic: dict
    location: dict
    timestamp: str


class LocationPredictInput(BaseModel):
    latitude: float
    longitude: float


class LocationPredictOutput(BaseModel):
    risk_level: str
    risk_probability: float
    recommendation: str
    weather: dict
    traffic: dict
    location: dict