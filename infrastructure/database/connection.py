from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application configuration for the Dashboard BFF Service.
    Loads settings from environment variables.
    """
    # Database URLs for reading data from various services
    SCAN_DB_URL: str
    ASSET_DB_URL: str
    VULN_DB_URL: str
    RISK_DB_URL: str
    
    # JWT Settings (must match Auth Service)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Redis Cache Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_EXPIRATION_SECONDS: int = 300 # Default to 5 minutes

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create a single instance to be used throughout the application
settings = Settings()