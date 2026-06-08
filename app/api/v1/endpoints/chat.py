"""
AI Chat Endpoint (Pillar 2)
============================
This file implements the conversational AI agent endpoint.

You should implement here:
- POST /v1/chat: Receives a user message, passes it to the PydanticAI agent,
  and returns the agent's structured response

The endpoint must:
1. Authenticate the user and extract organization context
2. Pass the message to the PydanticAI agent (defined in app/agent/agent.py)
3. The agent may invoke tools (e.g., create a task in the database)
4. Return the agent's response to the user

Example request body:
    {"message": "Register an urgent task called 'Review financial report' for Commercial"}

The agent should extract entities, validate with Pydantic schemas,
and autonomously call the appropriate tool to insert data.
"""
