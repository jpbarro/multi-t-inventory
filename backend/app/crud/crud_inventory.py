from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate

class CRUDInventory(CRUDBase[Inventory, InventoryCreate, InventoryUpdate]):
    
    async def get_multi_by_tenant(
        self, db: AsyncSession, *, tenant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Inventory]:
        query = (
            select(Inventory)
            .where(Inventory.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def create_with_tenant(
        self, db: AsyncSession, *, obj_in: InventoryCreate, tenant_id: UUID
    ) -> Inventory:
        db_obj = Inventory(
            **obj_in.model_dump(),
            tenant_id=tenant_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_product_and_tenant(
        self, db: AsyncSession, *, product_id: UUID, tenant_id: UUID
    ) -> Optional[Inventory]:
        query = select(Inventory).where(
            Inventory.product_id == product_id,
            Inventory.tenant_id == tenant_id
        )
        result = await db.execute(query)
        return result.scalars().first()

inventory = CRUDInventory(Inventory)