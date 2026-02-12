from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongo_url: Optional[str] = None
    mongo_db: str = "traffic_db"
    jwt_secret: str
    
    openweather_api_key: Optional[str] = None
    traffic_api_key: Optional[str] = None
    base_url: str 

    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    ml_model_path: str = "./model/model.pkl"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() # type: ignore