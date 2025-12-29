from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.api.deps import get_current_user
from app.core.security import authenticate_user, create_access_token
from app.core.config import settings
from app.core.limiter import limiter, auth_limit
from app.schemas.auth import LoginRequest, Token, TokenData

router = APIRouter()


@router.post("/login", response_model=Token)
@auth_limit()
async def login(request: Request, form_data: LoginRequest):
    """
    Authenticate user and return JWT access token.
    
    Rate limited to 5 requests per minute to prevent brute force attacks.
    """
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/check")
async def check_auth(current_user: TokenData = Depends(get_current_user)):
    """Check if the current token is valid."""
    return {"authenticated": True, "username": current_user.sub}
