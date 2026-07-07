# backend/app/core/config.py
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production"))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database Settings
    DATABASE_URL: str = Field(default="")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if v and v.strip():
            return v

        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        db = os.getenv("POSTGRES_DB", "bambudash")
        host = os.getenv("POSTGRES_HOST", "db")
        port = os.getenv("POSTGRES_PORT", "5432")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    # MQTT Settings
    MQTT_BROKER_HOST: str = Field(default_factory=lambda: os.getenv("MQTT_BROKER_HOST", ""))
    MQTT_BROKER_PORT: int = Field(default_factory=lambda: int(os.getenv("MQTT_BROKER_PORT", "1883")))
    MQTT_USERNAME: str = Field(default_factory=lambda: os.getenv("MQTT_USERNAME", ""))
    MQTT_PASSWORD: str = Field(default_factory=lambda: os.getenv("MQTT_PASSWORD", ""))

    # Bambu Cloud Settings (MQTT over TLS)
    BAMBU_CLOUD_HOST: str = Field(default_factory=lambda: os.getenv("BAMBU_CLOUD_HOST", "us.mqtt.bambulab.com"))
    BAMBU_CLOUD_PORT: int = Field(default_factory=lambda: int(os.getenv("BAMBU_CLOUD_PORT", "8883")))
    BAMBU_CLOUD_USERNAME: str = Field(default_factory=lambda: os.getenv("BAMBU_CLOUD_USERNAME", ""))
    BAMBU_CLOUD_PASSWORD: str = Field(default_factory=lambda: os.getenv("BAMBU_CLOUD_PASSWORD", ""))

    class Config:
        case_sensitive = True


settings = Settings()
