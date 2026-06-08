"""WebSocket notifications endpoint (Pillar 3).

Clients connect to ``/v1/ws/notifications?token=<jwt>`` and receive push
notifications when background tasks complete. Authentication is done via the
``token`` query parameter because the browser WebSocket API does not support
custom headers.
"""

from __future__ import annotations

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.core.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    """Maintain a persistent connection for real-time push notifications.

    The client authenticates via JWT query param. On connect, the socket is
    registered under the caller's ``organization_id`` so that ``broadcast``
    never leaks messages across tenants. The loop keeps the connection alive
    and handles client pings.
    """
    # Validate token before accepting the connection.
    try:
        payload = decode_access_token(token)
    except Exception:
        await websocket.close(code=1008)  # Policy Violation
        return

    org_id = payload.organization_id
    await manager.connect(websocket, org_id)

    try:
        while True:
            # Keep connection alive; echo any text frame back as a pong.
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, org_id)
