"""
RBAC Permission System (Pillar 1)
==================================
This file implements the Role-Based Access Control middleware/decorator.

You should implement here:
- A dependency or decorator that checks if the current user has the required
  scope/permission to access a route
- If the user lacks the permission, raise HTTPException 403 Forbidden

Example:
    from functools import wraps
    from fastapi import HTTPException, Depends

    def require_permission(scope: str):
        async def permission_checker(current_user = Depends(get_current_user)):
            if scope not in current_user.scopes:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return current_user
        return permission_checker

Usage in endpoints:
    @router.get("/tasks", dependencies=[Depends(require_permission("task:read"))])
    async def list_tasks(...):
"""
