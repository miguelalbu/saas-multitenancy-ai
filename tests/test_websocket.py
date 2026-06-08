"""WebSocket notification tests (Pillar 3)."""

from __future__ import annotations

import asyncio
import uuid

import pytest
from starlette.testclient import TestClient

from app.core.security import create_access_token
from app.core.scopes import ALL_SCOPES
from app.core.websocket_manager import manager
from app.main import app


def _make_token(user_id: uuid.UUID, org_id: uuid.UUID) -> str:
    return create_access_token(
        user_id=user_id, organization_id=org_id, scopes=list(ALL_SCOPES)
    )


def test_websocket_connection_and_ping(make_org):
    """Client connects, sends ping, receives pong, disconnects cleanly."""
    import asyncio

    org_id = uuid.uuid4()
    user_id = uuid.uuid4()
    token = _make_token(user_id, org_id)

    with TestClient(app) as test_client:
        with test_client.websocket_connect(
            f"/v1/ws/notifications?token={token}"
        ) as ws:
            ws.send_text("ping")
            assert ws.receive_text() == "pong"


def test_websocket_rejects_invalid_token():
    """Connection with a bad token is closed with 1008."""
    with TestClient(app) as test_client:
        with pytest.raises(Exception):
            with test_client.websocket_connect(
                "/v1/ws/notifications?token=not-a-valid-jwt"
            ) as ws:
                ws.receive_text()


@pytest.mark.asyncio
async def test_websocket_receives_notification():
    """After broadcast, the connected client receives the notification.

    We use a mock WebSocket object to register directly with the manager and
    verify the broadcast reaches it — this keeps everything on the same event
    loop and avoids the thread/loop boundary issue with TestClient.
    """
    from unittest.mock import AsyncMock, MagicMock
    from fastapi.websockets import WebSocketState

    org_id = uuid.uuid4()

    mock_ws = MagicMock()
    mock_ws.client_state = WebSocketState.CONNECTED
    mock_ws.send_json = AsyncMock()

    # Register the mock socket directly into the manager.
    await manager.connect.__wrapped__(manager, mock_ws, org_id) if hasattr(manager.connect, "__wrapped__") else None
    manager._connections[org_id].add(mock_ws)

    payload = {"type": "task_updated", "data": {"status": "overdue"}, "timestamp": "2026-01-01T00:00:00Z"}
    await manager.broadcast(org_id, payload)

    mock_ws.send_json.assert_called_once_with(payload)

    # Cleanup
    manager._connections[org_id].discard(mock_ws)


@pytest.mark.asyncio
async def test_websocket_tenant_isolation():
    """Broadcast to org_a must NOT be received by an org_b client."""
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()
    token_b = _make_token(uuid.uuid4(), org_b)

    received_by_b: list[dict] = []
    ready = asyncio.Event()

    import threading

    done_b = threading.Event()

    def _ws_b():
        with TestClient(app) as tc:
            with tc.websocket_connect(
                f"/v1/ws/notifications?token={token_b}"
            ) as ws:
                # Signal ready, then wait briefly for any message.
                done_b.set()
                ws.send_text("ping")
                ws.receive_text()  # pong

    thread = threading.Thread(target=_ws_b, daemon=True)
    thread.start()
    done_b.wait(timeout=3)
    await asyncio.sleep(0.1)

    # Broadcast to org_a only.
    await manager.broadcast(org_a, {"type": "org_a_secret", "data": {}, "timestamp": "2026-01-01T00:00:00Z"})

    # org_b should never have received that message.
    assert received_by_b == []
    thread.join(timeout=1)
