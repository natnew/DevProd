from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_base_url: str = Field(default="http://localhost:3000", alias="APP_BASE_URL")
    api_base_url: str = Field(default="http://localhost:8000", alias="API_BASE_URL")
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    devprod_api_key: str | None = Field(default=None, alias="DEVPROD_API_KEY")
    devprod_enable_auth: bool = Field(default=False, alias="DEVPROD_ENABLE_AUTH")
    devprod_rate_limit_per_minute: int = Field(default=60, alias="DEVPROD_RATE_LIMIT_PER_MINUTE")
    devprod_allowed_origins: list[str] = Field(
        default=["http://localhost:3000"], alias="DEVPROD_ALLOWED_ORIGINS"
    )
    gradient_api_base_url: str | None = Field(default=None, alias="GRADIENT_API_BASE_URL")
    gradient_agent_id: str | None = Field(default=None, alias="GRADIENT_AGENT_ID")
    gradient_model_access_key: str | None = Field(default=None, alias="GRADIENT_MODEL_ACCESS_KEY")
    devprod_run_history_db_path: str = Field(
        default="apps/api/devprod_history.sqlite3",
        alias="DEVPROD_RUN_HISTORY_DB_PATH",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("devprod_allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("devprod_api_key")
    @classmethod
    def require_key_when_auth_enabled(cls, value: str | None, info: object) -> str | None:
        data = getattr(info, "data", {})
        if data.get("devprod_enable_auth") and not value:
            raise ValueError("DEVPROD_API_KEY is required when auth is enabled.")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
