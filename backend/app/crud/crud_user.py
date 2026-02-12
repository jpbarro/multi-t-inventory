from typing import Any, Dict, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateAndTenant, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.crud.crud_tenant import tenant
from app.schemas.tenant import TenantCreate
# Pre-computed dummy hash so authenticate() takes constant time
_DUMMY_HASH = get_password_hash("dummy")


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            tenant_id=obj_in.tenant_id,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # async def create_user_and_tenant(self, db: AsyncSession, *, obj_in: UserCreateAndTenant) -> User:
    #     tenant = await tenant.create(db, obj_in=TenantCreate(name=obj_in.tenant_name))
    #     obj_in.tenant_id = tenant.id
    #     return await self.create(db, obj_in=obj_in)

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"] is not None:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        else:
            update_data.pop("password", None)

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            # Spend the same time as a real verification to prevent timing enumeration
            verify_password(password, _DUMMY_HASH)
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)