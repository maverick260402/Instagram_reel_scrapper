from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://scraper_user:password@localhost:5432/instagram_scraper"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 60

    # User Limits
    MAX_GROUPS_PER_USER: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
