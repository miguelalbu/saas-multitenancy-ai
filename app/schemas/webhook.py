"""
Webhook Event Schemas (Pillar 3)
=================================
Pydantic models for incoming webhook/trigger event payloads.

You should implement here:
- WebhookEvent: event_type (str, e.g., "task_overdue", "financial_alert"),
  payload (dict) - the event-specific data,
  organization_id (UUID) - which tenant this event belongs to
- WebhookResponse: status (str), message (str)

These schemas validate external events before they trigger background actions.
"""
