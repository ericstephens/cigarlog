from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_db"
    )
    OIDC_ISSUER: str = "http://localhost:8080/local"
    JWT_AUDIENCE: str = "cigarlog"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
