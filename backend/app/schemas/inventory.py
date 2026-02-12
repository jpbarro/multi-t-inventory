from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional

class InventoryBase(BaseModel):
    quantity: int
    min_stock: int
    current_stock: int
    product_id: UUID

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_stock: Optional[int] = None
    current_stock: Optional[int] = None

class InventoryInDBBase(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class InventoryPublic(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)