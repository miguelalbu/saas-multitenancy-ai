"""
API v1 Router Aggregator
========================
This file aggregates all endpoint routers under the /v1 prefix.

You should implement here:
- Import all endpoint routers (auth, chat, tasks, webhook, websocket)
- Create an APIRouter with prefix "/v1"
- Include each sub-router with appropriate prefixes and tags

Example:
    from fastapi import APIRouter
    from app.api.v1.endpoints import auth, chat, tasks, webhook, websocket

    router = APIRouter(prefix="/v1")
    router.include_router(auth.router, prefix="/auth", tags=["auth"])
    router.include_router(chat.router, prefix="/chat", tags=["chat"])
    router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
    router.include_router(websocket.router, tags=["websocket"])
"""
