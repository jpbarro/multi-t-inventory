from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import UserSignUp, UserPublic, UserInviteRequest, UserInviteResponse
from app.models.user import User
from uuid import UUID

router = APIRouter()

@router.get("/me", response_model=UserPublic)
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user info.
    """
    return current_user

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_tenant_and_user(
    user_in: UserSignUp,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Register a new Tenant and its first User.
    """
    existing = await crud.user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )

    user = await crud.user.create_tenant_and_user(db, obj_in=user_in)
    return user

@router.post("/invite", response_model=UserInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_user(
    user_in: UserInviteRequest,
    tenant_id: UUID = Depends(deps.get_current_tenant),
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Invite a new User to the Tenant.
    """
    existing = await crud.user.get_by_email(db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )

    user, password = await crud.user.invite_user(db, obj_in=user_in, tenant_id=tenant_id)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "temporary_password": password,
    }