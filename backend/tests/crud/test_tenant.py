import pytest
from app import crud
from app.schemas.tenant import TenantCreate, TenantUpdate
from sqlalchemy.ext.asyncio import AsyncSession


# 1. Test Creation
@pytest.mark.asyncio
async def test_create_tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="Acme Corp")

    tenant = await crud.tenant.create(db_session, obj_in=tenant_in)

    assert tenant.name == "Acme Corp"
    assert hasattr(tenant, "id")


# 2. Test Get by ID
@pytest.mark.asyncio
async def test_get_tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="Get Tenant")
    created_tenant = await crud.tenant.create(db_session, obj_in=tenant_in)

    stored_tenant = await crud.tenant.get(db_session, id=created_tenant.id)

    assert stored_tenant
    assert stored_tenant.id == created_tenant.id
    assert stored_tenant.name == "Get Tenant"


# 3. Test Get Multiple
@pytest.mark.asyncio
async def test_get_multi_tenants(db_session: AsyncSession):
    await crud.tenant.create(db_session, obj_in=TenantCreate(name="Tenant A"))
    await crud.tenant.create(db_session, obj_in=TenantCreate(name="Tenant B"))

    tenants = await crud.tenant.get_multi(db_session)

    assert len(tenants) >= 2


# 4. Test Update
@pytest.mark.asyncio
async def test_update_tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="Old Name")
    tenant = await crud.tenant.create(db_session, obj_in=tenant_in)

    update_data = TenantUpdate(name="New Name")
    updated_tenant = await crud.tenant.update(db_session, db_obj=tenant, obj_in=update_data)

    assert updated_tenant.name == "New Name"
    assert updated_tenant.id == tenant.id


# 5. Test Delete
@pytest.mark.asyncio
async def test_delete_tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="To Delete")
    tenant = await crud.tenant.create(db_session, obj_in=tenant_in)

    await crud.tenant.remove(db_session, id=tenant.id)

    deleted_tenant = await crud.tenant.get(db_session, id=tenant.id)
    assert deleted_tenant is None
