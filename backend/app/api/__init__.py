from fastapi import APIRouter
from app.api.routes import lookup, products, inventory

api_router = APIRouter()

# Include route modules
api_router.include_router(lookup.router, tags=["lookup"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

@api_router.get("/ping")
async def ping():
    return {"message": "pong"}
