# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = "a_very_secret_key"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    # Database Settings
    # The default value is for a local postgres instance in docker.
    # e.g., "postgresql://user:password@host:port/dbname"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/bambudash")

    # MQTT Settings
    MQTT_BROKER_HOST: str = "192.168.1.100" # Replace with your printer's IP
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = "bblp"
    MQTT_PASSWORD: str = "your_printer_access_code" # Replace with your printer's access code

    class Config:
        case_sensitive = True

settings = Settings()
