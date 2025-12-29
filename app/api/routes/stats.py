from fastapi import APIRouter, Depends, Request

from app.api.deps import get_current_user
from app.services import docker_service
from app.core.limiter import read_limit
from app.schemas.auth import TokenData
from app.schemas.stats import ContainerStats

router = APIRouter()


@router.get("/{container_id}", response_model=ContainerStats)
@read_limit()
async def container_stats(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Get container resource statistics (CPU, memory, network, I/O)."""
    return docker_service.get_container_stats(container_id)
