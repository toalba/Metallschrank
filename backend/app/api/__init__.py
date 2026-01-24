from fastapi import APIRouter, Depends
from app.api.routes import lookup, products, inventory
from app.core.auth import verify_credentials

api_router = APIRouter()

# Include route modules - all protected by Basic Auth
api_router.include_router(
    lookup.router, 
    tags=["lookup"],
    dependencies=[Depends(verify_credentials)]
)
api_router.include_router(
    products.router, 
    prefix="/products", 
    tags=["products"],
    dependencies=[Depends(verify_credentials)]
)
api_router.include_router(
    inventory.router, 
    prefix="/inventory", 
    tags=["inventory"],
    dependencies=[Depends(verify_credentials)]
)

@api_router.get("/ping")
async def ping():
    """Public health check endpoint"""
    return {"message": "pong"}

@api_router.get("/auth/check")
async def check_auth(username: str = Depends(verify_credentials)):
    """Verify credentials are valid - used by frontend login"""
    return {"authenticated": True, "username": username}
