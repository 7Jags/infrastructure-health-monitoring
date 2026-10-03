
"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: int = 5433
    database_username: str = ""
    database_password: str = ""
    database_name: str = ""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIRECTORY / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()