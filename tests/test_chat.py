"""
AI Chat Endpoint Tests (Pillar 2)
==================================
Test the PydanticAI agent chat functionality.

You should implement here:
- test_chat_creates_task: Send a message like "Create urgent task..."
  and verify the agent calls the create_task tool and the task exists in DB
- test_chat_requires_auth: Unauthenticated request returns 401
- test_chat_respects_tenant: Agent only creates tasks in the user's org
- test_chat_handles_invalid_input: Graceful response for unclear messages

Tip: You may need to mock the LLM API in tests to avoid real API calls.
"""
