import pytest
from app import crud
from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.ext.asyncio import AsyncSession


# 1. Test Creation
@pytest.mark.asyncio
async def test_create_product(db_session: AsyncSession):
    sku = "TEST-CREATE-001"
    product_in = ProductCreate(name="Test Product", sku=sku, description="A test desc")

    product = await crud.product.create(db_session, obj_in=product_in)

    assert product.name == "Test Product"
    assert product.sku == sku
    assert hasattr(product, "id")


# 2. Test Get by ID
@pytest.mark.asyncio
async def test_get_product(db_session: AsyncSession):
    sku = "TEST-GET-001"
    product_in = ProductCreate(name="Get Me", sku=sku)
    created_product = await crud.product.create(db_session, obj_in=product_in)

    stored_product = await crud.product.get(db_session, id=created_product.id)

    assert stored_product
    assert stored_product.id == created_product.id
    assert stored_product.name == "Get Me"


# 3. Test Custom Logic (Get by SKU)
@pytest.mark.asyncio
async def test_get_product_by_sku(db_session: AsyncSession):
    sku = "UNIQUE-SKU-123"
    product_in = ProductCreate(name="Unique Item", sku=sku)
    await crud.product.create(db_session, obj_in=product_in)

    stored_product = await crud.product.get_by_sku(db_session, sku=sku)

    assert stored_product
    assert stored_product.sku == sku


# 4. Test Update
@pytest.mark.asyncio
async def test_update_product(db_session: AsyncSession):
    sku = "TEST-UPDATE-001"
    product_in = ProductCreate(name="Original Name", sku=sku)
    product = await crud.product.create(db_session, obj_in=product_in)

    update_data = ProductUpdate(name="Updated Name")
    updated_product = await crud.product.update(
        db_session, db_obj=product, obj_in=update_data
    )

    assert updated_product.name == "Updated Name"
    assert updated_product.sku == sku


# 5. Test Delete
@pytest.mark.asyncio
async def test_delete_product(db_session: AsyncSession):
    sku = "TEST-DELETE-001"
    product_in = ProductCreate(name="To Delete", sku=sku)
    product = await crud.product.create(db_session, obj_in=product_in)

    await crud.product.remove(db_session, id=product.id)

    deleted_product = await crud.product.get(db_session, id=product.id)
    assert deleted_product is None
