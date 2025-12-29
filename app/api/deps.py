from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.schemas.auth import TokenData

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Dependency that validates JWT token from Authorization header.
    Returns decoded token data if valid.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenError()
        return TokenData(sub=username, exp=payload.get("exp"))
    except (InvalidTokenError, TokenExpiredError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_websocket_token(token: str) -> TokenData:
    """
    Verify JWT token for WebSocket connections.
    WebSockets can't use Authorization header, so token is passed as query param.
    """
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenError()
        return TokenData(sub=username, exp=payload.get("exp"))
    except (InvalidTokenError, TokenExpiredError):
        return None
