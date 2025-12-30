from fastapi import APIRouter, Depends, Request

from app.services import docker_service
from app.api.deps import get_current_user
from app.core.limiter import read_limit
from app.schemas.auth import TokenData
from app.schemas.system import HealthResponse, EnhancedHealthResponse, VersionResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint (no auth required)."""
    connected = docker_service.is_connected()
    return HealthResponse(
        status="ok" if connected else "degraded",
        docker_connected=connected,
    )


@router.get("/health", response_model=EnhancedHealthResponse)
@read_limit()
async def enhanced_health_check(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Enhanced health check with system information (requires auth)."""
    info = docker_service.get_system_info()
    return EnhancedHealthResponse(
        status="ok" if info.get("docker_connected") else "degraded",
        **info,
    )


@router.get("/version", response_model=VersionResponse)
@read_limit()
async def version_info(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """Get Docker version info (requires auth)."""
    return docker_service.get_version()
