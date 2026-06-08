"""
WebSocket Notification Schemas (Pillar 3)
==========================================
Pydantic models for WebSocket messages pushed to connected clients.

You should implement here:
- WSNotification: type (str, e.g., "task_updated", "new_audit_log"),
  data (dict) - the notification payload,
  timestamp (datetime)

These schemas structure the JSON messages sent via WebSocket
after background tasks complete.
"""
