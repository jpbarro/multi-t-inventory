import pytest
from httpx import AsyncClient

from app.core.rate_limit import limiter


@pytest.fixture(autouse=True)
def _reset_limiter():
    """Reset rate-limit counters before each test."""
    limiter.reset()
    yield


@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient):
    """The 6th login attempt within a minute should return 429."""
    payload = {"username": "a@b.com", "password": "wrong"}

    for i in range(5):
        resp = await client.post("/api/v1/auth/login", data=payload)
        assert resp.status_code != 429, f"Request {i + 1} was unexpectedly rate-limited"

    resp = await client.post("/api/v1/auth/login", data=payload)
    assert resp.status_code == 429
