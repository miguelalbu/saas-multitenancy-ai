"""AI chat endpoint (Pillar 2)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_ai.exceptions import UnexpectedModelBehavior, UsageLimitExceeded

from app.agent.agent import task_agent
from app.agent.tools import AgentDeps
from app.api.deps import CurrentUser
from app.core import scopes
from app.core.permissions import require_scope
from app.schemas.chat import ChatRequest, ChatResponse, ToolCall

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current: CurrentUser = Depends(require_scope(scopes.CHAT_USE)),
) -> ChatResponse:
    """Send a natural-language message to the AI agent.

    The agent may invoke tools (e.g. create a task) and returns a text reply
    along with a structured list of every tool it called.
    """
    deps = AgentDeps(
        organization_id=current.organization_id,
        user_id=current.user.id,
    )

    try:
        result = await task_agent.run(payload.message, deps=deps)
    except UsageLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI usage limit exceeded. Please try again later.",
        ) from exc
    except UnexpectedModelBehavior as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unexpected response from the AI model: {exc}",
        ) from exc
    except Exception as exc:
        # Catch-all for LLM API errors (network, auth, rate-limit variants).
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {exc}",
        ) from exc

    actions: list[ToolCall] = []
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            # ToolReturnPart carries the serialised tool result.
            part_type = type(part).__name__
            if part_type == "ToolReturnPart":
                actions.append(
                    ToolCall(tool=part.tool_name, result=part.content if isinstance(part.content, dict) else {"result": str(part.content)})
                )

    return ChatResponse(response=result.output, actions_taken=actions)
