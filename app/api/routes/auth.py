
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/check", dependencies=[Depends(get_current_user)])
def check_auth():
    return {"authenticated": True}
