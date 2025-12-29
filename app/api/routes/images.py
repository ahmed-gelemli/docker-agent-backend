from fastapi import APIRouter, Depends, Request

from app.api.deps import get_current_user
from app.services import docker_service
from app.core.limiter import read_limit
from app.schemas.auth import TokenData
from app.schemas.images import ImageListResponse

router = APIRouter()


@router.get("/", response_model=ImageListResponse)
@read_limit()
async def list_images(
    request: Request,
    current_user: TokenData = Depends(get_current_user),
):
    """List all Docker images."""
    images = docker_service.list_images()
    return ImageListResponse(images=images, total=len(images))
