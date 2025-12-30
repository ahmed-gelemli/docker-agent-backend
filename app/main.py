from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from docker.errors import NotFound, APIError, DockerException
from jose import JWTError

from app.api.routes import containers, auth, images, system, stats, realtime
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import (
    DockerAgentException,
    docker_agent_exception_handler,
    docker_not_found_handler,
    docker_api_error_handler,
    docker_exception_handler,
    jwt_error_handler,
    generic_exception_handler,
)
from app.services import docker_service

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        debug=settings.debug,
        rate_limiting=settings.rate_limit_enabled,
    )

    # Verify Docker connection on startup
    try:
        docker_service.get_client()
        logger.info("docker_connection_verified")
    except Exception as e:
        logger.error("docker_connection_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutting_down")
    docker_service.close_client()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Docker management API with JWT authentication",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Add request ID middleware (first, so it wraps everything)
app.add_middleware(RequestIDMiddleware)

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

# API version prefix
API_V1_PREFIX = "/api/v1"

# Include routers with versioned prefix
app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Auth"])
app.include_router(containers.router, prefix=f"{API_V1_PREFIX}/containers", tags=["Containers"])
app.include_router(images.router, prefix=f"{API_V1_PREFIX}/images", tags=["Images"])
app.include_router(system.router, prefix=API_V1_PREFIX, tags=["System"])
app.include_router(stats.router, prefix=f"{API_V1_PREFIX}/stats", tags=["Stats"])
app.include_router(realtime.router, prefix=API_V1_PREFIX, tags=["Realtime"])
