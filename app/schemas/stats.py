from pydantic import BaseModel, Field


class ContainerStats(BaseModel):
    """Container resource statistics."""

    container_id: str = Field(..., description="Container ID")
    cpu_percent: float = Field(..., description="CPU usage percentage (0-100)")
    memory_usage: int = Field(..., description="Memory usage in bytes")
    memory_limit: int = Field(..., description="Memory limit in bytes")
    memory_percent: float = Field(..., description="Memory usage percentage (0-100)")
    network_rx: int = Field(0, description="Network bytes received")
    network_tx: int = Field(0, description="Network bytes transmitted")
    block_read: int = Field(0, description="Block I/O bytes read")
    block_write: int = Field(0, description="Block I/O bytes written")


class ContainerStatsStream(BaseModel):
    """Streaming stats for WebSocket."""

    cpu_percent: float
    memory_usage: int
    memory_percent: float
    timestamp: str

