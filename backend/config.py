from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_URL: Optional[str] = None
    KAPSO_API_KEY: Optional[str] = None
    KAPSO_PHONE_NUMBER_ID: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar campos extra en lugar de rechazarlos

settings = Settings()
