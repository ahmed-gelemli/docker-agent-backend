import secrets
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, status, Query, Header

from mcp.server.sse import SseServerTransport

from app.mcp.server import mcp_server
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Create SSE transport for MCP
sse_transport = SseServerTransport("/mcp/messages/")


def _verify_mcp_api_key(api_key: Optional[str]) -> bool:
    """Verify the MCP API key using constant-time comparison."""
    if not settings.mcp_api_key:
        logger.warning("mcp_no_api_key_configured")
        return False
    if not api_key:
        return False
    return secrets.compare_digest(api_key, settings.mcp_api_key)


def _extract_api_key(
    authorization: Optional[str] = None,
    api_key_query: Optional[str] = None,
) -> Optional[str]:
    """Extract API key from Authorization header or query parameter."""
    # Try Authorization header first (Bearer token)
    if authorization:
        if authorization.startswith("Bearer "):
            return authorization[7:]
        return authorization
    # Fall back to query parameter
    return api_key_query


@router.get("/sse")
async def mcp_sse_endpoint(
    request: Request,
    api_key: Optional[str] = Query(None, alias="api_key"),
    authorization: Optional[str] = Header(None),
):
    """SSE endpoint for MCP communication."""
    # Verify API key
    key = _extract_api_key(authorization, api_key)
    if not _verify_mcp_api_key(key):
        logger.warning(
            "mcp_auth_failed",
            client=request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing MCP API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(
        "mcp_client_connected",
        client=request.client.host if request.client else "unknown",
    )

    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options(),
        )


@router.post("/messages/")
async def mcp_messages_endpoint(
    request: Request,
    api_key: Optional[str] = Query(None, alias="api_key"),
    authorization: Optional[str] = Header(None),
):
    """Handle MCP messages via POST."""
    # Verify API key
    key = _extract_api_key(authorization, api_key)
    if not _verify_mcp_api_key(key):
        logger.warning(
            "mcp_auth_failed",
            client=request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing MCP API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug("mcp_message_received")
    return await sse_transport.handle_post_message(
        request.scope,
        request.receive,
        request._send,
    )
