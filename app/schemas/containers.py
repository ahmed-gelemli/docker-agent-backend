from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContainerState(BaseModel):
    """Container state information."""

    status: str
    running: bool
    paused: bool
    restarting: bool
    pid: int
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class ContainerPort(BaseModel):
    """Container port mapping."""

    container_port: int = Field(..., alias="PrivatePort")
    host_port: Optional[int] = Field(None, alias="PublicPort")
    protocol: str = Field("tcp", alias="Type")
    host_ip: Optional[str] = Field(None, alias="IP")

    class Config:
        populate_by_name = True


class ContainerSummary(BaseModel):
    """Summary of a container for list endpoints."""

    id: str = Field(..., description="Container ID")
    name: str = Field(..., description="Container name")
    image: str = Field(..., description="Image name")
    status: str = Field(..., description="Container status")
    state: str = Field(..., description="Container state (running, exited, etc.)")
    created: int = Field(..., description="Creation timestamp")
    ports: list[ContainerPort] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class ContainerListResponse(BaseModel):
    """Response for container list endpoint."""

    containers: list[ContainerSummary]
    total: int


class ContainerLogsResponse(BaseModel):
    """Response for container logs endpoint."""

    container_id: str
    logs: str
    tail: int


class ContainerActionResponse(BaseModel):
    """Response for container start/stop actions."""

    container_id: str
    status: str
    message: str

