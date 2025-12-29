from fastapi import APIRouter, Depends, Request

from app.api.deps import get_current_user
from app.services import docker_service
from app.core.limiter import read_limit
from app.schemas.auth import TokenData

router = APIRouter()


@router.get("/")
@read_limit()
async def list_images(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """List all Docker images."""
    return docker_service.list_images()
