"""
Notification Service (Pillar 3 - Real-Time Push)
==================================================
This file bridges background tasks with WebSocket notifications.

You should implement here:
- notify(organization_id, message): Sends a notification to all connected
  WebSocket clients within the given organization
- Uses the ConnectionManager from app/core/websocket_manager.py

This service is called after any background task completes successfully,
ensuring reactive real-time updates for connected clients.

Example:
    from app.core.websocket_manager import manager

    async def notify(org_id: str, message: dict):
        await manager.broadcast(org_id, message)
"""
