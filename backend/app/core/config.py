from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vardast AI Builder"
    api_v1_str: str = "/api/v1"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "vardast"
    postgres_password: str = "vardast"
    postgres_db: str = "vardast"
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_fallback_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    allowed_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
