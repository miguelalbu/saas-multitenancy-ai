"""Canonical RBAC permission scopes used across the platform."""

# Task domain
TASK_READ = "task:read"
TASK_WRITE = "task:write"
TASK_DELETE = "task:delete"

# AI agent
CHAT_USE = "chat:use"

# Automation / webhooks
WEBHOOK_MANAGE = "webhook:manage"

ALL_SCOPES: list[str] = [
    TASK_READ,
    TASK_WRITE,
    TASK_DELETE,
    CHAT_USE,
    WEBHOOK_MANAGE,
]

# Default scope bundle for a read-only member role.
MEMBER_SCOPES: list[str] = [TASK_READ]
