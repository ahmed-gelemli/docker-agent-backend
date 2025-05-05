
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.services import docker_service

router = APIRouter()

@router.get("/{container_id}", dependencies=[Depends(get_current_user)])
def container_stats(container_id: str):
    return docker_service.get_container_stats(container_id)
