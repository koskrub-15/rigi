from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True, extra="ignore", env_file=".env"
    )
    PROJECT_NAME: str = "rigi"
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    API_BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://site.project.local.net:5173",
    ]
    # Auth Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    STRIPE_SECRET_KEY: str = ""
    WEB_URL: str = "http://localhost:5173"


settings = Settings()  # pyright: ignore[reportCallIssue]
