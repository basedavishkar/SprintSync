from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./sprintsync.db"

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI
    gemini_api_key: Optional[str] = None
    use_real_ai: bool = True

    # App
    debug: bool = True
    app_name: str = "SprintSync"
    version: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
