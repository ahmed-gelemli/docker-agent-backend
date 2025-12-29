from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("ok", description="Service status")
    docker_connected: bool = Field(True, description="Docker daemon connectivity")


class VersionResponse(BaseModel):
    """Docker version information."""

    api_version: str = Field(..., description="Docker API version")
    docker_version: str = Field(..., description="Docker engine version")
    os: str = Field("", description="Operating system")
    arch: str = Field("", description="Architecture")

