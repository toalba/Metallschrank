from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from app.models.product import ProductSource


class ProductBase(BaseModel):
    gtin: Optional[str] = None
    name: str
    brand: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    source: ProductSource = ProductSource.MANUAL
    raw_payload: Optional[dict] = None


class ProductResponse(ProductBase):
    id: UUID
    source: ProductSource
    raw_payload: Optional[dict] = None
    
    class Config:
        from_attributes = True


class LookupRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Barcode/GTIN to lookup")


class LookupResponse(BaseModel):
    status: str = Field(..., description="'found', 'created', or 'not_found'")
    product: Optional[ProductResponse] = None
