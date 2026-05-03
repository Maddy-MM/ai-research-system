from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Research Agent API"
    DEBUG: bool = False

    # --- JWT ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    # --- API Keys ---
    TAVILY_API_KEY: str
    GROQ_API_KEY: str

    # --- Demo user (no DB yet, one hardcoded user is fine for now) ---
    DEMO_USERNAME: str = "admin"
    DEMO_PASSWORD: str = "secret"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


# lru_cache means Settings() is only created once and reused everywhere.
# Without this, every file that calls get_settings() would re-read .env from disk.
@lru_cache
def get_settings() -> Settings:
    return Settings()