from fastapi import APIRouter, Depends, Request

from app.services import docker_service
from app.api.deps import get_current_user
from app.core.limiter import limiter, read_limit, action_limit
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/")
@read_limit()
async def get_containers(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """List all containers."""
    return [c.attrs for c in docker_service.list_containers()]


@router.get("/{container_id}/logs")
@read_limit()
async def logs(
    request: Request,
    container_id: str,
    tail: int = 100,
    current_user: TokenData = Depends(get_current_user),
):
    """Get container logs."""
    return {"logs": docker_service.get_logs(container_id, tail)}


@router.post("/{container_id}/start")
@action_limit()
async def start(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Start a container."""
    docker_service.start_container(container_id)
    return {"status": "started", "container_id": container_id}


@router.post("/{container_id}/stop")
@action_limit()
async def stop(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Stop a container."""
    docker_service.stop_container(container_id)
    return {"status": "stopped", "container_id": container_id}
