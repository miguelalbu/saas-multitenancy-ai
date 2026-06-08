"""
WebSocket Connection Manager (Pillar 3)
========================================
This file manages active WebSocket connections with multi-tenant isolation.

You should implement here:
- A ConnectionManager class that:
  - Stores active connections grouped by organization_id
  - connect(websocket, organization_id): Accepts and registers a connection
  - disconnect(websocket, organization_id): Removes a connection
  - broadcast(organization_id, message): Sends a message to ALL connected
    clients within that specific organization (never cross-tenant)

Example:
    class ConnectionManager:
        def __init__(self):
            self.active_connections: dict[str, list[WebSocket]] = {}

        async def connect(self, websocket: WebSocket, org_id: str):
            await websocket.accept()
            self.active_connections.setdefault(org_id, []).append(websocket)

        async def broadcast(self, org_id: str, message: dict):
            for connection in self.active_connections.get(org_id, []):
                await connection.send_json(message)

    manager = ConnectionManager()  # Singleton instance
"""
