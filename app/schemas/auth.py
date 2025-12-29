from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request body for login endpoint."""

    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)


class Token(BaseModel):
    """Response body for successful authentication."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    sub: str | None = None
    exp: int | None = None

