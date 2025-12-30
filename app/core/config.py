from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import List, Self
import secrets


class Settings(BaseSettings):
    # JWT Configuration
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API Authentication (for initial login or API key mode)
    api_username: str = "admin"
    api_password: str = "changeme"  # Override in .env for production

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Application
    app_name: str = "Docker Agent"
    debug: bool = False

    # MCP Configuration
    mcp_enabled: bool = True
    mcp_debug: bool = False  # Enable verbose MCP library logs
    mcp_api_key: str = ""  # API key for MCP authentication (required if mcp_enabled)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("secret_key", mode="after")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "changeme" or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                "Generate one with: openssl rand -base64 32"
            )
        return v

    @model_validator(mode="after")
    def validate_mcp_api_key(self) -> Self:
        if self.mcp_enabled and not self.mcp_api_key:
            raise ValueError(
                "MCP_API_KEY is required when MCP_ENABLED=true. "
                "Generate one with: openssl rand -base64 32"
            )
        if self.mcp_api_key and len(self.mcp_api_key) < 16:
            raise ValueError(
                "MCP_API_KEY must be at least 16 characters for security."
            )
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
