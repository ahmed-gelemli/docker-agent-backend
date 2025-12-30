from pydantic import BaseModel, Field
from typing import Optional


class HealthResponse(BaseModel):
    """Basic health check response."""

    status: str = Field("ok", description="Service status (ok, degraded)")
    docker_connected: bool = Field(True, description="Docker daemon connectivity")


class EnhancedHealthResponse(BaseModel):
    """Enhanced health check with system information."""

    status: str = Field("ok", description="Service status (ok, degraded)")
    docker_connected: bool = Field(..., description="Docker daemon connectivity")
    docker_version: Optional[str] = Field(None, description="Docker engine version")
    api_version: Optional[str] = Field(None, description="Docker API version")
    os: Optional[str] = Field(None, description="Operating system")
    arch: Optional[str] = Field(None, description="Architecture")
    containers_running: Optional[int] = Field(None, description="Number of running containers")
    containers_total: Optional[int] = Field(None, description="Total number of containers")
    images_total: Optional[int] = Field(None, description="Total number of images")
    memory_total: Optional[int] = Field(None, description="Total system memory in bytes")
    cpus: Optional[int] = Field(None, description="Number of CPUs")
    error: Optional[str] = Field(None, description="Error message if Docker is disconnected")


class VersionResponse(BaseModel):
    """Docker version information."""

    api_version: str = Field(..., description="Docker API version")
    docker_version: str = Field(..., description="Docker engine version")
    os: str = Field("", description="Operating system")
    arch: str = Field("", description="Architecture")

