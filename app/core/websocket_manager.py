"""Multi-tenant WebSocket connection manager (Pillar 3).

Connections are partitioned by ``organization_id`` so that broadcast never
crosses tenant boundaries. The manager is a module-level singleton shared
across all requests.
"""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict

from fastapi import WebSocket
from fastapi.websockets import WebSocketState


class ConnectionManager:
    def __init__(self) -> None:
        # org_id -> set of active WebSocket connections
        self._connections: dict[uuid.UUID, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, org_id: uuid.UUID) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[org_id].add(websocket)

    async def disconnect(self, websocket: WebSocket, org_id: uuid.UUID) -> None:
        async with self._lock:
            self._connections[org_id].discard(websocket)
            if not self._connections[org_id]:
                del self._connections[org_id]

    async def broadcast(self, org_id: uuid.UUID, message: dict) -> None:
        """Send ``message`` to every client connected under ``org_id``.

        Dead connections are silently removed so a single dropped client never
        blocks notifications to the rest of the organization.
        """
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(org_id, [])):
            if ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            else:
                dead.append(ws)

        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections[org_id].discard(ws)

    def connection_count(self, org_id: uuid.UUID) -> int:
        return len(self._connections.get(org_id, set()))


# Module-level singleton used by the WebSocket endpoint and notification service.
manager = ConnectionManager()
