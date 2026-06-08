"""
Test Configuration & Fixtures
==============================
This file provides shared pytest fixtures for all tests.

You should implement here:
- async_client: An httpx.AsyncClient configured with the FastAPI app
  for making test HTTP requests
- test_db: An async session connected to a test database
  (use a separate test DB or transactions that rollback)
- seed_data: Fixture that inserts test organizations, users, and tasks
- auth_headers: Fixture that returns Authorization headers with a valid JWT
  for a test user (for authenticated endpoints)

Example:
    @pytest.fixture
    async def async_client():
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
"""
