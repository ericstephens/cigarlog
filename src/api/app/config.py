from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:cigarlog_pass_local@127.0.0.1:5433/cigarlog_db"
    )
    OIDC_ISSUER: str = "http://localhost:8081/realms/cigarlog"
    JWT_AUDIENCE: str = "cigarlog"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Keycloak admin — used by the registration endpoint to create new users.
    # Set KEYCLOAK_ADMIN_URL="" to disable (e.g. when using mock OIDC).
    KEYCLOAK_ADMIN_URL: str = "http://localhost:8081"
    KEYCLOAK_REALM: str = "cigarlog"
    KEYCLOAK_ADMIN_USER: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
