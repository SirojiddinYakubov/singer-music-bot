import pathlib
from typing import Any
from pydantic import field_validator
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

    ADMIN_ID: str | int

    class Config:
        env_file = ".env"


settings = Settings()