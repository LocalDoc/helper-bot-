# NOT DONE
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:changeme@localhost:5432/helper_bot")
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_V1_PREFIX: str = "/api/v1"
    
    TRIAL_MESSAGE_LIMIT: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()