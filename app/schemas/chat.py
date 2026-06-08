"""
Chat Schemas (Pillar 2)
========================
Pydantic models for the AI chat endpoint request/response.

You should implement here:
- ChatRequest: message (str) - the user's natural language input
- ChatResponse: response (str) - the agent's text reply,
  actions_taken (list[dict], optional) - tools the agent called,
  e.g., [{"tool": "create_task", "result": {"task_id": "..."}}]
"""
