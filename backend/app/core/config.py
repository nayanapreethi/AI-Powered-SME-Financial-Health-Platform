"""
SME-Pulse AI - Core Configuration
Centralized configuration management using Pydantic Settings
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    APP_NAME: str = "SME-Pulse AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://sme_pulse_user:secure_password_123@localhost:5432/sme_pulse_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Security Configuration
    SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production-min-32-chars"
    ENCRYPTION_KEY: str = "your-32-byte-aes-encryption-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Integration (Optional)
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "claude-3-sonnet-20240229"
    AI_MAX_TOKENS: int = 2000
    
    # Banking APIs (Optional)
    ICICI_API_KEY: Optional[str] = None
    HDFC_API_KEY: Optional[str] = None
    
    # GST Integration (Optional)
    GST_API_KEY: Optional[str] = None
    
    # File Upload Configuration
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: tuple = (".pdf", ".csv", ".xlsx", ".xls")
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

