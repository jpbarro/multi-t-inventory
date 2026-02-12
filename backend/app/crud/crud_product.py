from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def get_by_sku(self, db: AsyncSession, *, sku: str) -> Optional[Product]:
        """
        Find a product by its SKU.
        """
        query = select(Product).where(Product.sku == sku)
        result = await db.execute(query)
        return result.scalars().first()

product = CRUDProduct(Product)