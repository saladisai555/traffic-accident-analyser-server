from datetime import datetime, timezone
from typing import Optional


class User:
    def __init__(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        created_at: Optional[datetime] = None,
        is_verified: bool = False,
        _id: Optional[str] = None,
    ):
        self._id = _id
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.latitude = latitude
        self.longitude = longitude
        self.created_at = created_at or datetime.now(timezone.utc)
        self.is_active = True
        self.is_verified = is_verified
    
    def to_dict(self):
        return {
            "email": self.email,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            email=data.get("email"),
            full_name=data.get("full_name"),
            hashed_password=data.get("hashed_password"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            created_at=data.get("created_at"),
            is_verified=data.get("is_verified", False),
            _id=data.get("_id"),
        )
