from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    mongo_url: Optional[str] = None
    mongo_db: str = "traffic_db"
    jwt_secret: str
    
    openweather_api_key: Optional[str] = None
    traffic_api_key: Optional[str] = None
    base_url: str

    # Comma-separated list, e.g. "http://localhost:3000,https://your-app.vercel.app"
    cors_origins: str = ""

    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    ml_model_path: str = "./model/model.pkl"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins(self) -> List[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if self.base_url and self.base_url not in origins:
            origins.append(self.base_url)
        return origins


settings = Settings() # type: ignore