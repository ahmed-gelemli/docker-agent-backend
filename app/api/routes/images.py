
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.services import docker_service

router = APIRouter()

@router.get("/", dependencies=[Depends(get_current_user)])
def list_images():
    return docker_service.list_images()
