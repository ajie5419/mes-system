"""WebSocket 连接管理服务"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # user_id -> set of WebSocket connections (multi-device support)
        self._connections: Dict[int, Set[WebSocket]] = {}
        # role -> set of user_ids
        self._role_map: Dict[str, Set[int]] = {}
        # user_id -> last heartbeat timestamp
        self._heartbeat: Dict[int, float] = {}
        self._heartbeat_timeout = 60  # seconds

    async def connect(self, user_id: int, role: str, ws: WebSocket):
        await ws.accept()
        if user_id not in self._connections:
            self._connections[user_id] = set()
        self._connections[user_id].add(ws)
        if role not in self._role_map:
            self._role_map[role] = set()
        self._role_map[role].add(user_id)
        self._heartbeat[user_id] = datetime.now().timestamp()
        logger.info("WebSocket connected: user=%d role=%s", user_id, role)

    def disconnect(self, user_id: int, ws: WebSocket):
        conns = self._connections.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                del self._connections[user_id]
                self._heartbeat.pop(user_id, None)
        logger.info("WebSocket disconnected: user=%d", user_id)

    def register_heartbeat(self, user_id: int):
        self._heartbeat[user_id] = datetime.now().timestamp()

    def get_stale_users(self) -> List[int]:
        """Return user_ids with no heartbeat for > timeout seconds."""
        now = datetime.now().timestamp()
        return [uid for uid, ts in self._heartbeat.items() if now - ts > self._heartbeat_timeout]

    async def broadcast_to_user(self, user_id: int, message: dict):
        payload = {"type": message.get("type", "notification"), "data": message.get("data", message), "timestamp": datetime.now().isoformat()}
        dead = []
        for ws in self._connections.get(user_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def broadcast_to_all(self, message: dict):
        for uid in list(self._connections.keys()):
            await self.broadcast_to_user(uid, message)

    async def broadcast_to_role(self, role: str, message: dict):
        for uid in self._role_map.get(role, set()):
            await self.broadcast_to_user(uid, message)


# Singleton
manager = ConnectionManager()


async def heartbeat_monitor():
    """Periodically check and close stale connections."""
    while True:
        await asyncio.sleep(10)
        stale = manager.get_stale_users()
        for uid in stale:
            for ws in list(manager._connections.get(uid, [])):
                try:
                    await ws.close(code=4001, reason="heartbeat timeout")
                except Exception:
                    pass
            manager._connections.pop(uid, None)
            manager._heartbeat.pop(uid, None)
            logger.info("WebSocket heartbeat timeout: user=%d", uid)
