"""
Webhook Event Processing Service (Pillar 3)
=============================================
This file processes incoming webhook events as background tasks.

You should implement here:
- process_event(event: WebhookEvent): Main dispatcher that routes events
  to the appropriate handler based on event_type
- handle_task_overdue(payload): Marks a task as overdue and creates an audit log
- handle_financial_alert(payload): Processes financial alerts

After processing, each handler must notify connected WebSocket clients
via the NotificationService. Use asyncio.create_task() or FastAPI
BackgroundTasks to run these asynchronously.

Example:
    async def process_event(event: WebhookEvent):
        if event.event_type == "task_overdue":
            await handle_task_overdue(event.payload)
            await notification_service.notify(event.organization_id, {...})
"""
