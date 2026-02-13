from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional

from app.core.config import settings

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    tenant_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str = Field(..., max_length=settings.PASSWORD_MAX_LENGTH)
    is_superuser: bool = False

class UserCreateAndTenant(UserCreate):
    tenant_name: str

class UserSignUp(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(..., max_length=settings.PASSWORD_MAX_LENGTH)
    tenant_name: str

class UserInviteRequest(BaseModel):
    email: EmailStr
    full_name: str
class UserInviteResponse(UserBase):
    temporary_password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    tenant_id: Optional[UUID] = None
    password: Optional[str] = Field(None, max_length=settings.PASSWORD_MAX_LENGTH)

class UserInDBBase(UserBase):
    id: UUID
    is_superuser: bool = False
    model_config = ConfigDict(from_attributes=True)

class UserPublic(UserBase):
    id: UUID
    email: str  # type: ignore[assignment]  # plain str to avoid EmailStr rejecting stored addresses
    is_superuser: bool = False
    model_config = ConfigDict(from_attributes=True)