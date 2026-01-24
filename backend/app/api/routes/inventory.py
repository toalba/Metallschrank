from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.product import Product
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryAdjustRequest,
    InventoryTransactionResponse,
)

router = APIRouter()


@router.get("", response_model=List[InventoryItemResponse])
async def list_inventory(
    skip: int = 0,
    limit: int = 100,
    location: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List inventory items with optional location filter"""
    stmt = select(InventoryItem)
    
    if location:
        search = f"%{location}%"
        stmt = stmt.where(InventoryItem.location.ilike(search))
    
    stmt = stmt.offset(skip).limit(limit).order_by(InventoryItem.created_at.desc())
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return [InventoryItemResponse.model_validate(item) for item in items]


@router.post("", response_model=InventoryItemResponse, status_code=201)
async def create_inventory_item(
    item: InventoryItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new inventory item"""
    # Verify product exists
    result = await db.execute(
        select(Product).where(Product.id == item.product_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_item = InventoryItem(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    
    # Create initial transaction if quantity > 0
    if db_item.quantity > 0:
        transaction = InventoryTransaction(
            inventory_item_id=db_item.id,
            delta=int(db_item.quantity),
            reason="add"
        )
        db.add(transaction)
        await db.commit()
    
    return InventoryItemResponse.model_validate(db_item)


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a single inventory item by ID"""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    return InventoryItemResponse.model_validate(item)


@router.post("/{item_id}/adjust")
async def adjust_inventory(
    item_id: str,
    adjustment: InventoryAdjustRequest,
    db: AsyncSession = Depends(get_db)
):
    """Adjust inventory quantity (±delta). Deletes item if quantity reaches 0 or below."""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    new_quantity = item.quantity + Decimal(adjustment.delta)
    
    # Create transaction record before potential deletion
    transaction = InventoryTransaction(
        inventory_item_id=item.id,
        delta=adjustment.delta,
        reason=adjustment.reason
    )
    db.add(transaction)
    await db.flush()  # Flush to save transaction
    
    # Delete item if quantity reaches 0 or below
    if new_quantity <= 0:
        # Delete all transactions first (foreign key constraint)
        from sqlalchemy import delete
        await db.execute(
            delete(InventoryTransaction).where(
                InventoryTransaction.inventory_item_id == item_id
            )
        )
        
        # Now delete the item
        await db.delete(item)
        await db.commit()
        return {"status": "deleted", "id": item_id}
    
    # Otherwise update quantity
    item.quantity = new_quantity
    await db.commit()
    await db.refresh(item)
    
    return InventoryItemResponse.model_validate(item)
