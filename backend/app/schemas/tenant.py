from uuid import UUID
from pydantic import BaseModel, ConfigDict

class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
    pass

class TenantInDBBase(TenantBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class TenantPublic(TenantInDBBase):
    pass