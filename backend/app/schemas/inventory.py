from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional
from app.models.inventory import TransactionReason


class InventoryItemBase(BaseModel):
    product_id: UUID
    location: str = Field(..., description="e.g. 'Schrank A / Fach 3 / Box 2'")
    quantity: Decimal = Field(default=Decimal("0.00"), ge=0)
    unit: str = "pcs"
    notes: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemResponse(InventoryItemBase):
    id: UUID
    
    class Config:
        from_attributes = True


class InventoryAdjustRequest(BaseModel):
    delta: int = Field(..., description="Amount to adjust (positive or negative)")
    reason: TransactionReason = TransactionReason.ADJUST


class InventoryTransactionResponse(BaseModel):
    id: UUID
    inventory_item_id: UUID
    delta: int
    reason: TransactionReason
    
    class Config:
        from_attributes = True
