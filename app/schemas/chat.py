"""Chat schemas (Pillar 2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4096)


class ToolCall(BaseModel):
    tool: str
    result: dict


class ChatResponse(BaseModel):
    response: str
    actions_taken: list[ToolCall] = Field(default_factory=list)
