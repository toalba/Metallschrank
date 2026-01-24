from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    query: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List products with optional search query"""
    stmt = select(Product)
    
    if query:
        search = f"%{query}%"
        stmt = stmt.where(
            (Product.name.ilike(search)) |
            (Product.brand.ilike(search)) |
            (Product.gtin.ilike(search))
        )
    
    stmt = stmt.offset(skip).limit(limit).order_by(Product.created_at.desc())
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    return [ProductResponse.model_validate(p) for p in products]


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Manually create a product"""
    # Check if GTIN already exists
    if product.gtin:
        result = await db.execute(
            select(Product).where(Product.gtin == product.gtin)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Product with GTIN {product.gtin} already exists"
            )
    
    db_product = Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    return ProductResponse.model_validate(db_product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single product by ID"""
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse.model_validate(product)
