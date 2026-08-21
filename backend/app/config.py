"""Application configuration settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server and application settings loaded from environment or defaults."""
    
    # Server Settings
    APP_NAME: str = "ESP32 Motor Monitoring System Backend"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./motor_monitoring.db"
    
    # Motor Status Timeout (seconds)
    # If no data is received within this duration, motor is marked offline
    MOTOR_ONLINE_TIMEOUT_SECONDS: float = 10.0
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
