from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from app import crud
from app.api import deps
from app.schemas.inventory import InventoryPublic, InventoryCreate, InventoryUpdate
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[InventoryPublic])
async def read_inventories(
    db: AsyncSession = Depends(deps.get_db),
    tenant_id: UUID = Depends(deps.get_current_tenant),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve inventories.
    """
    return await crud.inventory.get_multi_by_tenant(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=InventoryPublic)
async def read_inventory_by_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    tenant_id: UUID = Depends(deps.get_current_tenant),
    product_id: UUID,
) -> Any:
    """
    Retrieve an inventory item by product ID.
    """
    inventory = await crud.inventory.get_by_product_and_tenant(db, product_id=product_id, tenant_id=tenant_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory

@router.post("/", response_model=InventoryPublic, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    *,
    db: AsyncSession = Depends(deps.get_db),
    tenant_id: UUID = Depends(deps.get_current_tenant),
    inventory_in: InventoryCreate,
) -> Any:
    """
    Create new inventory item.
    """
    existing_item = await crud.inventory.get_by_product_and_tenant(
        db, product_id=inventory_in.product_id, tenant_id=tenant_id
    )
    if existing_item:
        raise HTTPException(
            status_code=400,
            detail="This product is already in your inventory. Use PATCH to update quantity.",
        )

    return await crud.inventory.create_with_tenant(
        db, obj_in=inventory_in, tenant_id=tenant_id
    )

@router.patch("/{inventory_id}", response_model=InventoryPublic)
async def update_inventory(
    *,
    db: AsyncSession = Depends(deps.get_db),
    tenant_id: UUID = Depends(deps.get_current_tenant),
    inventory_id: UUID,
    inventory_in: InventoryUpdate,
) -> Any:
    """
    Update an inventory item (e.g., add stock).
    """
    item = await crud.inventory.get(db, id=inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if item.tenant_id != tenant_id:
         raise HTTPException(status_code=404, detail="Inventory item not found")

    return await crud.inventory.update(db, db_obj=item, obj_in=inventory_in)