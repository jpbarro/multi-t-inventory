from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "multi-t-inventory"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    API_V1_STR: str = "/api/v1"
    # Bcrypt limit (72 bytes); used for validation and hashing
    PASSWORD_MAX_LENGTH: int = 72

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()