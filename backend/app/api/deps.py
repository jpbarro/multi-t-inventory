from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app import crud
from fastapi import Depends, HTTPException
from uuid import UUID
from app.models.user import User
from app.core.config import settings
from app.services.supply_service import SupplyService
from app.core import security
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields a db session.
    Closes the session automatically after the request finishes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if not token_data.sub:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_tenant(
    current_user: User = Depends(get_current_user),
) -> UUID:
    if not current_user.tenant_id:
        # Superusers might not have a tenant, handle accordingly
        raise HTTPException(
            status_code=400, detail="User is not associated with a tenant"
        )
    return current_user.tenant_id


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user


def get_supply_service() -> SupplyService:
    """
    Dependency that instantiates the SupplyService with the correct settings.
    """
    return SupplyService(
        supplier_url=getattr(
            settings, "SUPPLIER_API_URL", "https://mock-supplier.com/api"
        ),
        api_key=getattr(settings, "SUPPLIER_API_KEY", "mock_key_123"),
    )
