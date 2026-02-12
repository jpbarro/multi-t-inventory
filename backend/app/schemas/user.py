from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.core.config import settings

class UserBase(BaseModel):
    email: str
    full_name: str
    tenant_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str = Field(..., max_length=settings.PASSWORD_MAX_LENGTH)
    is_superuser: bool = False

class UserCreateAndTenant(UserCreate):
    tenant_name: str

class SignUp(BaseModel):
    email: str
    full_name: str
    password: str = Field(..., max_length=settings.PASSWORD_MAX_LENGTH)
    tenant_name: str

class UserUpdate(UserBase):
    email: Optional[str] = None
    full_name: Optional[str] = None
    tenant_id: Optional[UUID] = None
    password: Optional[str] = Field(None, max_length=settings.PASSWORD_MAX_LENGTH)

class UserInDBBase(UserBase):
    id: UUID
    is_superuser: bool = False
    model_config = ConfigDict(from_attributes=True)

class UserPublic(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)