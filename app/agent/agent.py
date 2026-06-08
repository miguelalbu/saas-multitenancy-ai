"""PydanticAI agent definition (Pillar 2).

The agent is a module-level singleton. Tools are passed at construction time
so they are importable and patchable in tests.
"""

from __future__ import annotations

from pydantic_ai import Agent

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import AgentDeps, create_task, list_tasks

task_agent: Agent[AgentDeps, str] = Agent(
    model="openai-chat:gpt-4o-mini",
    deps_type=AgentDeps,
    output_type=str,
    system_prompt=SYSTEM_PROMPT,
    tools=[create_task, list_tasks],
)
