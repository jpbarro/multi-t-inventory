from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: str 

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProductInDBBase(ProductBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

# user response
class ProductPublic(ProductBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)