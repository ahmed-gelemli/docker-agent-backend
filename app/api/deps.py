
from fastapi import Header, HTTPException, status
from app.core.security import verify_token

def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    if not verify_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
