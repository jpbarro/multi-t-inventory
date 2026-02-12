from fastapi import APIRouter
from app.api.v1.endpoints import products
from app.api.v1.endpoints import inventory
from app.api.v1.endpoints import login
from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])