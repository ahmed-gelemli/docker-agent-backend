
from fastapi import APIRouter, Depends
from app.services import docker_service
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", dependencies=[Depends(get_current_user)])
def get_containers():
    return [c.attrs for c in docker_service.list_containers()]

@router.get("/{container_id}/logs", dependencies=[Depends(get_current_user)])
def logs(container_id: str, tail: int = 100):
    return {"logs": docker_service.get_logs(container_id, tail)}

@router.post("/{container_id}/start", dependencies=[Depends(get_current_user)])
def start(container_id: str):
    docker_service.start_container(container_id)
    return {"status": "started"}

@router.post("/{container_id}/stop", dependencies=[Depends(get_current_user)])
def stop(container_id: str):
    docker_service.stop_container(container_id)
    return {"status": "stopped"}
