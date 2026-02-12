from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.user import SignUp, UserPublic
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup(
    *,
    db: AsyncSession = Depends(deps.get_db),
    signup_in: SignUp,
):
    """
    Public signup: creates a new tenant and its first user atomically.
    """
    existing = await crud.user.get_by_email(db, email=signup_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Create tenant + user in a single transaction
    tenant = Tenant(name=signup_in.tenant_name)
    db.add(tenant)
    await db.flush()  # assigns tenant.id without committing

    user = User(
        email=signup_in.email,
        full_name=signup_in.full_name,
        hashed_password=get_password_hash(signup_in.password),
        is_superuser=False,
        tenant_id=tenant.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
