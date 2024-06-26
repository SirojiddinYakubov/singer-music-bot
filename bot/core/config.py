import os
import pathlib
from typing import Any
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

BASE_DIR = pathlib.Path(__file__).parents[1]


class Settings(BaseSettings):
    BOT_API: str
    BOT_HASH: str

    # WEBHOOK_HOST: Optional[AnyHttpUrl] = "https://topskill.uz"

    TOKEN_API: str | None = None

    @field_validator("TOKEN_API", check_fields=False)
    def assemble_bot_token(cls, v: str, values: dict[str, Any]) -> str:
        return f"{values.data.get('BOT_API')}:{values.data.get('BOT_HASH')}"

    REDIS_HOST: str
    REDIS_PORT: str | int

    ADMIN_IDS: list[int] = [1470735667, 360176754, 183551051]

    DATABASE_PORT: int
    DATABASE_PASSWORD: str
    DATABASE_USER: str
    DATABASE_NAME: str
    DATABASE_HOST: str

    ASYNC_DATABASE_URI: str | None = None

    @field_validator("ASYNC_DATABASE_URI", check_fields=False)
    def assemble_async_database_uri(cls, v: str, values: dict[str, Any]) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("DATABASE_USER"),
            password=values.data.get("DATABASE_PASSWORD"),
            host=values.data.get("DATABASE_HOST"),
            port=int(values.data.get("DATABASE_PORT")),
            path=f"{values.data.get('DATABASE_NAME') or ''}?prepared_statement_cache_size=0",
        )

    PAGE_SIZE: int = 5

    WEB_SERVER_HOST: str = "0.0.0.0"
    WEB_SERVER_PORT: int = 8000
    WEBHOOK_PATH: str = ""
    WEBHOOK_SECRET: str
    BASE_WEBHOOK_URL: str = "https://bahtiyorrahmanov.uz/"
    PAYMENTS_PROVIDER_TOKEN: str

    MEDIA_ROOT: str = os.path.join(BASE_DIR, 'media')

    class Config:
        env_file = ".env"


settings = Settings()
