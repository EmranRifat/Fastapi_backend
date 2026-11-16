
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ecommerce API"
    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/ecommerce"
    )

    secret_key: SecretStr = SecretStr(
        "development-only-change-this-secret"
    )

    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
