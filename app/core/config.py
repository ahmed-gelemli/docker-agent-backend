try:
    from pydantic_settings import BaseSettings
except ImportError:  # Fall back to pydantic<2
    from pydantic import BaseSettings


class Settings(BaseSettings):
    api_token: str = "changeme"

    class Config:
        env_file = ".env"


settings = Settings()
