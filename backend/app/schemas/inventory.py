from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional

class InventoryBase(BaseModel):
    min_stock: int
    current_stock: int
    product_id: UUID

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    min_stock: Optional[int] = None
    current_stock: Optional[int] = None

class InventoryInDBBase(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class InventoryPublic(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

class SupplyRequest(BaseModel):
    quantity: int

class SupplyResponse(BaseModel):
    status: str
    message: str
    external_reference_id: str