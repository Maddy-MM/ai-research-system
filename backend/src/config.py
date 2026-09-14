import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Research Agent API"
    DEBUG: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60

    OPENAI_MODEL: str = "gpt-5-nano"
    OPENAI_REASONING_EFFORT: str | None = None

    TAVILY_API_KEY: str
    OPENAI_API_KEY: str = ""

    MCP_SERVER_URL: str = "http://localhost:8001/mcp"
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8001

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "researchmind"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    DATABASE_URL: str = "sqlite:///./research.db"

    DEMO_USERNAME: str = "admin"
    DEMO_PASSWORD: str = "secret"
    DEFAULT_USER: str | None = None
    DEFAULT_PASS: str | None = None
    JWT_SECRET: str | None = None

    @property
    def effective_username(self) -> str:
        return self.DEFAULT_USER or self.DEMO_USERNAME

    @property
    def effective_password(self) -> str:
        return self.DEFAULT_PASS or self.DEMO_PASSWORD

    @property
    def effective_jwt_secret(self) -> str:
        return self.JWT_SECRET or self.JWT_SECRET_KEY

    model_config = ConfigDict(
        env_file=[
            str(Path(__file__).resolve().parent.parent / ".env"),
            str(Path(__file__).resolve().parent.parent.parent / ".env"),
            ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )


def _configure_langsmith(settings: "Settings") -> None:
    if settings.LANGCHAIN_TRACING_V2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    _configure_langsmith(settings)
    return settings
