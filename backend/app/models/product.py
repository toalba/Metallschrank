import enum
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class ProductSource(str, enum.Enum):
    """Source of product data"""
    MANUAL = "manual"
    OPENFOODFACTS = "openfoodfacts"
    OPENGTINDB = "opengtindb"
    UPCITEMDB = "upcitemdb"
    BARCODELOOKUP = "barcodelookup"
    UNKNOWN = "unknown"


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    gtin: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[ProductSource] = mapped_column(
        SQLEnum(ProductSource),
        default=ProductSource.MANUAL,
        nullable=False
    )
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
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
        return f"<Product(id={self.id}, gtin={self.gtin}, name={self.name})>"
