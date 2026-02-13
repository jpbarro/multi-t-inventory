from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.inventory import (
    InventoryPublic,
    InventoryCreate,
    InventoryUpdate,
    SupplyRequest,
    SupplyResponse,
)
from uuid import UUID
from app.services.supply_service import SupplyService

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
            detail="This product is already in your inventory. Use PATCH to update stock.",
        )

    return await crud.inventory.create_with_tenant(db, obj_in=inventory_in, tenant_id=tenant_id)


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


@router.post(
    "/{inventory_id}/resupply",
    response_model=SupplyResponse,
    status_code=status.HTTP_200_OK,
)
async def request_more_supply(
    *,
    db: AsyncSession = Depends(deps.get_db),
    inventory_id: UUID,
    supply_in: SupplyRequest,
    current_user: User = Depends(deps.get_current_user),
    supply_svc: SupplyService = Depends(deps.get_supply_service),
) -> Any:
    """
    Request more supply from an external vendor when stock is low.
    """
    inventory_item = await crud.inventory.get(db, id=inventory_id)
    if not inventory_item or inventory_item.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    product = await crud.product.get(db, id=inventory_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Associated product not found")

    tenant = await crud.tenant.get(db, id=current_user.tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    response = await supply_svc.request_restock(
        tenant_name=tenant.name,
        product_sku=product.sku,
        product_name=product.name,
        quantity=supply_in.quantity,
    )

    return response
