from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from app import crud
from app.api import deps
from app.models.user import User
from app.schemas.tenant import TenantPublic

router = APIRouter()

@router.get("/", response_model=List[TenantPublic])
async def read_tenants(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all tenants.
    """
    return await crud.tenant.get_multi(db)