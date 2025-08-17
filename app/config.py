# app/config.py
import os
from functools import lru_cache
from typing import Any

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    bot_token: SecretStr
    admin_ids: list[int]
    verify_chat_id: int | str
    invite_url: str
    rate_limit_broadcast_per_sec: int = 18

    # Database
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    # Deployment
    use_webhook: bool = False
    base_webhook_url: str = ""
    web_server_host: str = "0.0.0.0"
    web_server_port: int = 8080

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> list[int]:
        if isinstance(v, int): return [v]
        if isinstance(v, str):
            if not v: return []
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        return v

    @property
    def postgres_dsn(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            path=self.db_name,
        ))
    
    # --- NEW PROPERTIES FOR WEBHOOKS ---
    @property
    def webhook_path(self) -> str:
        """Constructs the path for the webhook."""
        # A secret path is used to ensure that only Telegram can call our bot
        return f"/webhook/{self.bot_token.get_secret_value()}"

    @property
    def webhook_url(self) -> str:
        """Constructs the full webhook URL."""
        return f"{self.base_webhook_url.rstrip('/')}{self.webhook_path}"

    @property
    def is_dev(self) -> bool:
        return os.getenv("ENV") == "dev"


@lru_cache
def load_config() -> Settings:
    """Load configuration from environment variables."""
    return Settings()