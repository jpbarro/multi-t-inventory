import uuid

import pytest
from app import crud
from app.schemas.user import UserCreate, UserUpdate, UserSignUp, UserInviteRequest
from app.schemas.tenant import TenantCreate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="User Test Tenant")
    return await crud.tenant.create(db_session, obj_in=tenant_in)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email,
        full_name="Test User",
        password="password123",
        tenant_id=tenant.id,
    )

    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.email == email
    assert user.full_name == "Test User"
    assert user.tenant_id == tenant.id
    assert user.is_superuser is False
    assert user.hashed_password != "password123"
    assert hasattr(user, "id")


@pytest.mark.asyncio
async def test_create_superuser(db_session: AsyncSession):
    email = _unique_email()
    user_in = UserCreate(
        email=email,
        full_name="Super Admin",
        password="password123",
        is_superuser=True,
    )

    user = await crud.user.create(db_session, obj_in=user_in)

    assert user.is_superuser is True
    assert user.tenant_id is None


# ---------------------------------------------------------------------------
# get_by_email
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_by_email(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="Find Me", password="password123", tenant_id=tenant.id
    )
    await crud.user.create(db_session, obj_in=user_in)

    found = await crud.user.get_by_email(db_session, email=email)

    assert found is not None
    assert found.email == email


@pytest.mark.asyncio
async def test_get_by_email_not_found(db_session: AsyncSession):
    found = await crud.user.get_by_email(db_session, email="nonexistent@example.com")
    assert found is None


# ---------------------------------------------------------------------------
# create_tenant_and_user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_tenant_and_user(db_session: AsyncSession):
    email = _unique_email()
    signup = UserSignUp(
        email=email,
        full_name="New Signup",
        password="password123",
        tenant_name="Signup Tenant",
    )

    user = await crud.user.create_tenant_and_user(db_session, obj_in=signup)

    assert user.email == email
    assert user.full_name == "New Signup"
    assert user.tenant_id is not None

    # verify the tenant was actually created
    tenant = await crud.tenant.get(db_session, id=user.tenant_id)
    assert tenant is not None
    assert tenant.name == "Signup Tenant"


# ---------------------------------------------------------------------------
# invite_user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invite_user(db_session: AsyncSession, tenant):
    email = _unique_email()
    invite_in = UserInviteRequest(email=email, full_name="Invited User")

    user, temp_password = await crud.user.invite_user(
        db_session, obj_in=invite_in, tenant_id=tenant.id
    )

    assert user.email == email
    assert user.full_name == "Invited User"
    assert user.tenant_id == tenant.id
    assert isinstance(temp_password, str)
    assert len(temp_password) == 12

    # the temporary password should actually authenticate
    authed = await crud.user.authenticate(
        db_session, email=email, password=temp_password
    )
    assert authed is not None
    assert authed.id == user.id


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_user_name(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="Old Name", password="password123", tenant_id=tenant.id
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    updated = await crud.user.update(
        db_session, db_obj=user, obj_in=UserUpdate(full_name="New Name")
    )

    assert updated.full_name == "New Name"
    assert updated.id == user.id


@pytest.mark.asyncio
async def test_update_user_password(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="Password Change", password="old_password", tenant_id=tenant.id
    )
    user = await crud.user.create(db_session, obj_in=user_in)
    old_hash = user.hashed_password

    updated = await crud.user.update(
        db_session, db_obj=user, obj_in=UserUpdate(password="new_password")
    )

    assert updated.hashed_password != old_hash
    # new password should authenticate
    authed = await crud.user.authenticate(
        db_session, email=email, password="new_password"
    )
    assert authed is not None


@pytest.mark.asyncio
async def test_update_user_with_dict(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="Dict Update", password="password123", tenant_id=tenant.id
    )
    user = await crud.user.create(db_session, obj_in=user_in)

    updated = await crud.user.update(
        db_session, db_obj=user, obj_in={"full_name": "Updated Via Dict"}
    )

    assert updated.full_name == "Updated Via Dict"


@pytest.mark.asyncio
async def test_update_user_without_password(db_session: AsyncSession, tenant):
    """Updating with password=None should not change the hash."""
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="No PW Change", password="password123", tenant_id=tenant.id
    )
    user = await crud.user.create(db_session, obj_in=user_in)
    old_hash = user.hashed_password

    updated = await crud.user.update(
        db_session, db_obj=user, obj_in=UserUpdate(full_name="Still Same PW")
    )

    assert updated.hashed_password == old_hash


# ---------------------------------------------------------------------------
# authenticate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_authenticate_success(db_session: AsyncSession, tenant):
    email = _unique_email()
    password = "correct_password"
    user_in = UserCreate(
        email=email, full_name="Auth User", password=password, tenant_id=tenant.id
    )
    created = await crud.user.create(db_session, obj_in=user_in)

    authed = await crud.user.authenticate(db_session, email=email, password=password)

    assert authed is not None
    assert authed.id == created.id


@pytest.mark.asyncio
async def test_authenticate_wrong_password(db_session: AsyncSession, tenant):
    email = _unique_email()
    user_in = UserCreate(
        email=email, full_name="Wrong PW", password="real_password", tenant_id=tenant.id
    )
    await crud.user.create(db_session, obj_in=user_in)

    authed = await crud.user.authenticate(db_session, email=email, password="wrong")

    assert authed is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_email(db_session: AsyncSession):
    authed = await crud.user.authenticate(
        db_session, email="nobody@example.com", password="whatever"
    )
    assert authed is None
