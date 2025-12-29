from fastapi import Request, status
from fastapi.responses import JSONResponse
from docker.errors import NotFound, APIError, DockerException
from jose import JWTError
import logging

logger = logging.getLogger(__name__)


class DockerAgentException(Exception):
    """Base exception for Docker Agent."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ContainerNotFoundError(DockerAgentException):
    """Raised when a container is not found."""

    def __init__(self, container_id: str):
        super().__init__(
            message=f"Container '{container_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ImageNotFoundError(DockerAgentException):
    """Raised when an image is not found."""

    def __init__(self, image_id: str):
        super().__init__(
            message=f"Image '{image_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DockerServiceUnavailableError(DockerAgentException):
    """Raised when Docker daemon is unavailable."""

    def __init__(self):
        super().__init__(
            message="Docker service is unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class InvalidCredentialsError(DockerAgentException):
    """Raised when credentials are invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class TokenExpiredError(DockerAgentException):
    """Raised when JWT token has expired."""

    def __init__(self):
        super().__init__(
            message="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidTokenError(DockerAgentException):
    """Raised when JWT token is invalid."""

    def __init__(self):
        super().__init__(
            message="Invalid token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


# Exception Handlers


async def docker_agent_exception_handler(
    request: Request, exc: DockerAgentException
) -> JSONResponse:
    logger.warning(f"DockerAgentException: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def docker_not_found_handler(request: Request, exc: NotFound) -> JSONResponse:
    logger.warning(f"Docker NotFound: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found in Docker"},
    )


async def docker_api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    logger.error(f"Docker APIError: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "Docker daemon returned an error"},
    )


async def docker_exception_handler(
    request: Request, exc: DockerException
) -> JSONResponse:
    logger.error(f"DockerException: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Docker service is unavailable"},
    )


async def jwt_error_handler(request: Request, exc: JWTError) -> JSONResponse:
    logger.warning(f"JWTError: {exc} | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid or expired token"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception | Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

