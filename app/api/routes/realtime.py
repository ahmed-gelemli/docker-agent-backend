from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import logging

from app.services import docker_service
from app.api.deps import verify_websocket_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/logs/ws/{container_id}")
async def websocket_logs(
    websocket: WebSocket,
    container_id: str,
    token: str = Query(...),
):
    """Stream container logs via WebSocket."""
    token_data = verify_websocket_token(token)
    if not token_data:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    await websocket.accept()
    logger.info(f"WebSocket logs connected: container={container_id}, user={token_data.sub}")

    try:
        async for line in docker_service.stream_logs(container_id):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        logger.info(f"WebSocket logs disconnected: container={container_id}")
    except Exception as e:
        logger.error(f"WebSocket logs error: {e}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
            await websocket.close(code=1011)
        except Exception:
            pass


@router.websocket("/events/ws")
async def websocket_events(
    websocket: WebSocket,
    token: str = Query(...),
):
    """Stream Docker events via WebSocket."""
    token_data = verify_websocket_token(token)
    if not token_data:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    await websocket.accept()
    logger.info(f"WebSocket events connected: user={token_data.sub}")

    try:
        async for event in docker_service.stream_events():
            await websocket.send_text(event)
    except WebSocketDisconnect:
        logger.info("WebSocket events disconnected")
    except Exception as e:
        logger.error(f"WebSocket events error: {e}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
            await websocket.close(code=1011)
        except Exception:
            pass


@router.websocket("/stats/ws/{container_id}")
async def websocket_stats(
    websocket: WebSocket,
    container_id: str,
    token: str = Query(...),
):
    """Stream container stats via WebSocket."""
    token_data = verify_websocket_token(token)
    if not token_data:
        await websocket.close(code=1008, reason="Invalid or expired token")
        return

    await websocket.accept()
    logger.info(f"WebSocket stats connected: container={container_id}, user={token_data.sub}")

    try:
        async for stat in docker_service.stream_stats(container_id):
            await websocket.send_text(stat)
    except WebSocketDisconnect:
        logger.info(f"WebSocket stats disconnected: container={container_id}")
    except Exception as e:
        logger.error(f"WebSocket stats error: {e}")
        try:
            await websocket.send_text(f"Error: {str(e)}")
            await websocket.close(code=1011)
        except Exception:
            pass
