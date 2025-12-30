from fastapi import APIRouter, Depends, Request, Query

from app.services import docker_service
from app.api.deps import get_current_user
from app.core.limiter import read_limit, action_limit
from app.schemas.auth import TokenData
from app.schemas.containers import (
    ContainerListResponse,
    ContainerLogsResponse,
    ContainerActionResponse,
    ContainerDetail,
)

router = APIRouter()


@router.get("/", response_model=ContainerListResponse)
@read_limit()
async def get_containers(
    request: Request,
    all: bool = Query(True, description="Include stopped containers"),
    current_user: TokenData = Depends(get_current_user),
):
    """List all containers."""
    containers = docker_service.list_containers(all=all)
    return ContainerListResponse(containers=containers, total=len(containers))


@router.get("/{container_id}", response_model=ContainerDetail)
@read_limit()
async def get_container_details(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Get detailed information about a specific container."""
    return docker_service.get_container_details(container_id)


@router.get("/{container_id}/logs", response_model=ContainerLogsResponse)
@read_limit()
async def logs(
    request: Request,
    container_id: str,
    tail: int = Query(100, ge=1, le=10000, description="Number of lines to return"),
    current_user: TokenData = Depends(get_current_user),
):
    """Get container logs."""
    log_content = docker_service.get_logs(container_id, tail)
    return ContainerLogsResponse(
        container_id=container_id,
        logs=log_content,
        tail=tail,
    )


@router.post("/{container_id}/start", response_model=ContainerActionResponse)
@action_limit()
async def start(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Start a container."""
    docker_service.start_container(container_id)
    return ContainerActionResponse(
        container_id=container_id,
        status="started",
        message=f"Container {container_id} started successfully",
    )


@router.post("/{container_id}/stop", response_model=ContainerActionResponse)
@action_limit()
async def stop(
    request: Request,
    container_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Stop a container."""
    docker_service.stop_container(container_id)
    return ContainerActionResponse(
        container_id=container_id,
        status="stopped",
        message=f"Container {container_id} stopped successfully",
    )


@router.post("/{container_id}/restart", response_model=ContainerActionResponse)
@action_limit()
async def restart(
    request: Request,
    container_id: str,
    timeout: int = Query(10, ge=0, le=300, description="Timeout in seconds before killing the container"),
    current_user: TokenData = Depends(get_current_user),
):
    """Restart a container."""
    docker_service.restart_container(container_id, timeout=timeout)
    return ContainerActionResponse(
        container_id=container_id,
        status="restarted",
        message=f"Container {container_id} restarted successfully",
    )
