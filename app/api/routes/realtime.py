
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services import docker_service
from app.core.security import verify_token

router = APIRouter()

@router.websocket("/logs/ws/{container_id}")
async def websocket_logs(websocket: WebSocket, container_id: str, token: str = Query(...)):
    if not verify_token(token):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        async for line in docker_service.stream_logs(container_id):
            await websocket.send_text(line)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()

@router.websocket("/events/ws")
async def websocket_events(websocket: WebSocket, token: str = Query(...)):
    if not verify_token(token):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        async for event in docker_service.stream_events():
            await websocket.send_text(event)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()

@router.websocket("/stats/ws/{container_id}")
async def websocket_stats(websocket: WebSocket, container_id: str, token: str = Query(...)):
    if not verify_token(token):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        async for stat in docker_service.stream_stats(container_id):
            await websocket.send_text(stat)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()
