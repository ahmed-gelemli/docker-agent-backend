from fastapi import APIRouter, Depends, Request

from app.services import docker_service
from app.api.deps import get_current_user
from app.core.limiter import read_limit
from app.schemas.auth import TokenData
from app.schemas.system import HealthResponse, VersionResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint (no auth required)."""
    connected = docker_service.is_connected()
    return HealthResponse(
        status="ok" if connected else "degraded",
        docker_connected=connected,
    )


@router.get("/version", response_model=VersionResponse)
@read_limit()
async def version_info(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Get Docker version info (requires auth)."""
    return docker_service.get_version()
