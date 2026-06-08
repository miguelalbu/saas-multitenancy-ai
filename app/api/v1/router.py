"""API v1 router aggregator.

Sub-routers are mounted here under the ``/v1`` prefix. Chat (Pillar 2) and
webhook/websocket (Pillar 3) routers are added as those pillars are built.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, tasks

router = APIRouter(prefix="/v1")
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
