import uuid

import pytest
from app import crud
from app.schemas.tenant import TenantCreate
from app.schemas.product import ProductCreate
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def tenant(db_session: AsyncSession):
    tenant_in = TenantCreate(name="Inventory Test Tenant")
    return await crud.tenant.create(db_session, obj_in=tenant_in)


@pytest.fixture
async def product(db_session: AsyncSession):
    sku = f"INV-{uuid.uuid4().hex[:8]}"
    product_in = ProductCreate(name="Inventory Test Product", sku=sku)
    return await crud.product.create(db_session, obj_in=product_in)


@pytest.fixture
async def second_product(db_session: AsyncSession):
    sku = f"INV2-{uuid.uuid4().hex[:8]}"
    product_in = ProductCreate(name="Second Product", sku=sku)
    return await crud.product.create(db_session, obj_in=product_in)


# 1. Test Create with Tenant
@pytest.mark.asyncio
async def test_create_inventory_with_tenant(db_session, tenant, product):
    inv_in = InventoryCreate(
        product_id=product.id,
        min_stock=10,
        current_stock=100,
    )

    inventory = await crud.inventory.create_with_tenant(
        db_session, obj_in=inv_in, tenant_id=tenant.id
    )

    assert inventory.tenant_id == tenant.id
    assert inventory.product_id == product.id
    assert inventory.current_stock == 100
    assert hasattr(inventory, "id")


# 2. Test Get by ID
@pytest.mark.asyncio
async def test_get_inventory(db_session, tenant, product):
    inv_in = InventoryCreate(
        product_id=product.id, min_stock=5, current_stock=50
    )
    created = await crud.inventory.create_with_tenant(
        db_session, obj_in=inv_in, tenant_id=tenant.id
    )

    stored = await crud.inventory.get(db_session, id=created.id)

    assert stored
    assert stored.id == created.id
    assert stored.current_stock == 50


# 3. Test Get by Product and Tenant
@pytest.mark.asyncio
async def test_get_by_product_and_tenant(db_session, tenant, product):
    inv_in = InventoryCreate(
        product_id=product.id, min_stock=3, current_stock=30
    )
    await crud.inventory.create_with_tenant(
        db_session, obj_in=inv_in, tenant_id=tenant.id
    )

    stored = await crud.inventory.get_by_product_and_tenant(
        db_session, product_id=product.id, tenant_id=tenant.id
    )

    assert stored
    assert stored.product_id == product.id
    assert stored.tenant_id == tenant.id


# 4. Test Get Multi by Tenant
@pytest.mark.asyncio
async def test_get_multi_by_tenant(db_session, tenant, product, second_product):
    for p in [product, second_product]:
        inv_in = InventoryCreate(
            product_id=p.id, min_stock=1, current_stock=10
        )
        await crud.inventory.create_with_tenant(
            db_session, obj_in=inv_in, tenant_id=tenant.id
        )

    inventories = await crud.inventory.get_multi_by_tenant(
        db_session, tenant_id=tenant.id
    )

    assert len(inventories) >= 2
    assert all(inv.tenant_id == tenant.id for inv in inventories)


# 5. Test Update
@pytest.mark.asyncio
async def test_update_inventory(db_session, tenant, product):
    inv_in = InventoryCreate(
        product_id=product.id, min_stock=2, current_stock=20
    )
    inventory = await crud.inventory.create_with_tenant(
        db_session, obj_in=inv_in, tenant_id=tenant.id
    )

    update_data = InventoryUpdate(current_stock=99, min_stock=15)
    updated = await crud.inventory.update(
        db_session, db_obj=inventory, obj_in=update_data
    )

    assert updated.current_stock == 99
    assert updated.min_stock == 15
    assert updated.product_id == product.id


# 6. Test Delete
@pytest.mark.asyncio
async def test_delete_inventory(db_session, tenant, product):
    inv_in = InventoryCreate(
        product_id=product.id, min_stock=1, current_stock=5
    )
    inventory = await crud.inventory.create_with_tenant(
        db_session, obj_in=inv_in, tenant_id=tenant.id
    )

    await crud.inventory.remove(db_session, id=inventory.id)

    deleted = await crud.inventory.get(db_session, id=inventory.id)
    assert deleted is None
