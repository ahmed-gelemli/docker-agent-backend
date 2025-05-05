
from fastapi import APIRouter
from app.services import docker_service

router = APIRouter()

@router.get("/healthz")
def health_check():
    return {"status": "ok"}

@router.get("/version")
def version_info():
    return docker_service.get_version()
