import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    payload = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "strongpassword123",
        "tenant_name": "New Tenant",
    }
    response = await client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data
    assert data["tenant_id"] is not None
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "First User",
        "password": "password123",
        "tenant_name": "Dup Tenant",
    }
    # Create the first user
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201

    # Attempt to create a second user with the same email
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_missing_fields(client: AsyncClient):
    # Missing email, password, and tenant_name
    payload = {"full_name": "Incomplete User"}
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422
