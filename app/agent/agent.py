"""
PydanticAI Agent Definition (Pillar 2)
=======================================
This file defines and configures the PydanticAI conversational agent.

You should implement here:
- Create a PydanticAI Agent instance connected to an LLM
  (OpenAI API, Gemini API, or local Ollama)
- Configure the agent with a system prompt (from app/agent/prompts.py)
- Register tools (from app/agent/tools.py) that the agent can call
- Define the agent's response model using Pydantic schemas

Example:
    from pydantic_ai import Agent
    from app.agent.prompts import SYSTEM_PROMPT
    from app.agent.tools import create_task_tool

    agent = Agent(
        model="openai:gpt-4o",
        system_prompt=SYSTEM_PROMPT,
        tools=[create_task_tool],
    )

The agent is invoked by the POST /v1/chat endpoint.
"""
