from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic import Field


class InventoryBase(BaseModel):
    min_stock: int = Field(ge=0)
    current_stock: int = Field(ge=0)
    product_id: UUID


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    min_stock: Optional[int] = Field(None, ge=0)
    current_stock: Optional[int] = Field(None, ge=0)


class InventoryInDBBase(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class InventoryPublic(InventoryBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class SupplyRequest(BaseModel):
    quantity: int = Field(ge=0)


class SupplyResponse(BaseModel):
    status: str
    message: str
    external_reference_id: str
