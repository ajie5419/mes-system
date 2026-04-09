"""WebSocket 通知端点"""
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from services import auth_service
from services.ws_service import manager, heartbeat_monitor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])

# Track background tasks
_heartbeat_task = None


async def _ensure_heartbeat_monitor():
    global _heartbeat_task
    if _heartbeat_task is None or _heartbeat_task.done():
        _heartbeat_task = asyncio.create_task(heartbeat_monitor())


@router.websocket("/api/v1/ws/notifications")
async def ws_notifications(ws: WebSocket, token: str = Query(...)):
    # Verify token from query param
    try:
        payload = auth_service._decode_token(token)
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            await ws.close(code=4003, reason="invalid token payload")
            return
        user_id = int(user_id)
        role = payload.get("role", "user")
    except Exception as e:
        logger.warning("WS auth failed: %s", e)
        await ws.close(code=4001, reason="authentication failed")
        return

    await manager.connect(user_id, role, ws)
    await _ensure_heartbeat_monitor()

    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                manager.register_heartbeat(user_id)
                await ws.send_text("pong")
            else:
                manager.register_heartbeat(user_id)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        manager.disconnect(user_id, ws)
