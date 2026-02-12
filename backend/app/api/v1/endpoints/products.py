from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.schemas.product import ProductCreate, ProductUpdate, ProductPublic

router = APIRouter()

@router.get("/", response_model=List[ProductPublic])
async def read_products(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products.
    """
    return await crud.product.get_multi(db, skip=skip, limit=limit)

# 2. CREATE
@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_in: ProductCreate,
) -> Any:
    """
    Create new product.
    """
    # Custom Logic: Check if SKU already exists
    product = await crud.product.get_by_sku(db, sku=product_in.sku)
    if product:
        raise HTTPException(
            status_code=400,
            detail="The product with this SKU already exists in the system.",
        )
    
    # Generic Logic: Create the item
    return await crud.product.create(db, obj_in=product_in)

# 3. GET ONE (By ID)
@router.get("/{product_id}", response_model=ProductPublic)
async def read_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: UUID,
) -> Any:
    """
    Get product by ID.
    """
    product = await crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 4. UPDATE
@router.patch("/{product_id}", response_model=ProductPublic)
async def update_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: UUID,
    product_in: ProductUpdate,
) -> Any:
    """
    Update a product.
    """
    product = await crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = await crud.product.update(db, db_obj=product, obj_in=product_in)
    return product

# 5. DELETE
@router.delete("/{product_id}", response_model=ProductPublic)
async def delete_product(
    *,
    db: AsyncSession = Depends(deps.get_db),
    product_id: UUID,
) -> Any:
    """
    Delete a product.
    """
    product = await crud.product.get(db, id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = await crud.product.remove(db, id=product_id)
    return product