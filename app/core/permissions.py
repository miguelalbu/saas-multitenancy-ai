"""RBAC permission dependencies (Pillar 1)."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.deps import CurrentUser, get_current_user


def require_scope(*required: str) -> Callable[..., CurrentUser]:
    """Build a dependency enforcing that the user holds all ``required`` scopes.

    Returns the authenticated :class:`CurrentUser` so endpoints can both gate
    access and reuse the resolved context.

    Usage::

        @router.get("/tasks")
        async def list_tasks(user = Depends(require_scope("task:read"))):
            ...
    """

    async def checker(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        missing = [scope for scope in required if scope not in current_user.scopes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope(s): {', '.join(missing)}",
            )
        return current_user

    return checker
