from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

# Explicitly load the .env file
load_dotenv()

class Settings(BaseSettings):
    # Pydantic will now pick these up from the environment variables loaded by dotenv
    MONGODB_URL: str
    DATABASE_NAME: str = "event_photo_retrieval"

    # We can still use model_config to be safe, but load_dotenv() handles the OS environment
    model_config = SettingsConfigDict(extra="ignore")

settings = Settings()
