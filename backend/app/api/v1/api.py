from fastapi import APIRouter
from app.api.v1.endpoints import products
from app.api.v1.endpoints import inventory
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import tenants

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
