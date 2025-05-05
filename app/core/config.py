
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_token: str = "changeme"

    class Config:
        env_file = ".env"

settings = Settings()
