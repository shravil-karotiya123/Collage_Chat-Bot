"""
Backend Configuration Module.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "College Intelligent Assistant API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "*")


settings = Settings()
