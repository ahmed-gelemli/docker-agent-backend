import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from docker.errors import NotFound, APIError, DockerException
from jose import JWTError

from app.api.routes import containers, auth, images, system, stats, realtime
from app.core.config import settings
from app.core.limiter import limiter
from app.core.exceptions import (
    DockerAgentException,
    docker_agent_exception_handler,
    docker_not_found_handler,
    docker_api_error_handler,
    docker_exception_handler,
    jwt_error_handler,
    generic_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Docker management API with JWT authentication",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Register exception handlers
app.add_exception_handler(DockerAgentException, docker_agent_exception_handler)
app.add_exception_handler(NotFound, docker_not_found_handler)
app.add_exception_handler(APIError, docker_api_error_handler)
app.add_exception_handler(DockerException, docker_exception_handler)
app.add_exception_handler(JWTError, jwt_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(containers.router, prefix="/containers", tags=["Containers"])
app.include_router(images.router, prefix="/images", tags=["Images"])
app.include_router(system.router, tags=["System"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(realtime.router, tags=["Realtime"])


@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.app_name} starting up...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.app_name} shutting down...")
