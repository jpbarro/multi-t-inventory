from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "multi-t-inventory"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()