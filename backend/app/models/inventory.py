import enum
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, Numeric, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    product_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00")
    )
    unit: Mapped[str] = mapped_column(String(50), default="pcs", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, product_id={self.product_id}, location={self.location})>"


class TransactionReason(str, enum.Enum):
    """Reason for inventory transaction"""
    ADD = "add"
    REMOVE = "remove"
    ADJUST = "adjust"


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    inventory_item_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inventory_items.id"),
        nullable=False,
        index=True
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[TransactionReason] = mapped_column(
        SQLEnum(TransactionReason),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<InventoryTransaction(id={self.id}, item_id={self.inventory_item_id}, delta={self.delta})>"
