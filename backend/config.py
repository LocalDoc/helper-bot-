"""
PURPOSE:
This file defines all configuration settings for the Pomogator backend using
Pydantic Settings. It loads environment variables, sets defaults, and provides
type-safe configuration for the entire application.

HOW CONFIGURATION IS LOADED:
1. ENVIRONMENT VARIABLES: Highest priority (overrides everything)
2. .env FILE: To be loaded from project root   
3. CLASS DEFAULTS: Used if no env var or .env value is set

CONFIGURATION SOURCES:
Production/Deployment: Environment variables (DATABASE_URL, API keys, etc.)
Local Development: .env file in project root
Fallback Values: Defaults defined in this class

REQUIRED ENVIRONMENT VARIABLES FOR PRODUCTION:
DATABASE_URL: PostgreSQL connection string (asyncpg format)
OPENAI_API_KEY: OpenAI API authentication
GEMINI_API_KEY: Google Gemini API authentication  
DEEPSEEK_API_KEY: DeepSeek API authentication
TELEGRAM_PAYMENT_PROVIDER_TOKEN: Telegram payment provider token

DEFAULT VALUES (used when env vars not set):
APP_NAME: "pomogator-backend"
ENV: "development"
HOST: "0.0.0.0" 
PORT: 8000
TRIAL_DEFAULT_MESSAGES: 10
CREDIT_PER_PAYMENT_UNIT: 1
"""

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "pomogator-backend"
    ENV: str = "development"
    DEBUG: bool = False
    # Database (asyncpg) URL (set by Dev 3 / deployment)
    DATABASE_URL: Optional[str] = None

    # AI providers DO BE DONE
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[AnyHttpUrl] = None

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_URL: Optional[AnyHttpUrl] = None

    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: Optional[AnyHttpUrl] = None

    # Payment Dev 4 
    TELEGRAM_PAYMENT_PROVIDER_TOKEN: Optional[str] = None

    TRIAL_DEFAULT_MESSAGES: int = 10
    CREDIT_PER_PAYMENT_UNIT: int = 1  # 1 unit - 1 credit

    # HTTP / server TO BE DONE 
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()