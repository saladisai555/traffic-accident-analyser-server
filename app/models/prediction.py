from datetime import datetime, timezone
from typing import Optional


class Prediction:
    def __init__(
        self,
        user_email: str,
        risk_level: str,
        risk_probability: float,
        latitude: float,
        longitude: float,
        features: dict,
        created_at: Optional[datetime] = None,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.user_email = user_email
        self.risk_level = risk_level
        self.risk_probability = risk_probability
        self.latitude = latitude
        self.longitude = longitude
        self.features = features
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def to_dict(self):
        return {
            "user_email": self.user_email,
            "risk_level": self.risk_level,
            "risk_probability": self.risk_probability,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "features": self.features,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            user_email=data.get("user_email"),
            risk_level=data.get("risk_level"),
            risk_probability=data.get("risk_probability"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            features=data.get("features"),
            created_at=data.get("created_at"),
            _id=data.get("_id"),
        )
