from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


def get_limiter_key(request: Request) -> str:
    """Get rate limit key from request. Uses IP address."""
    return get_remote_address(request)


limiter = Limiter(
    key_func=get_limiter_key,
    enabled=settings.rate_limit_enabled,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window}seconds"],
)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down.",
            "retry_after": exc.detail,
        },
    )


# Rate limit decorators for different endpoint types
def auth_limit():
    """Stricter limit for auth endpoints: 5 per minute."""
    return limiter.limit("5/minute")


def action_limit():
    """Limit for action endpoints (start/stop): 10 per minute."""
    return limiter.limit("10/minute")


def read_limit():
    """Standard limit for read endpoints: 60 per minute."""
    return limiter.limit("60/minute")

