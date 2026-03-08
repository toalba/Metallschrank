import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.product import Product, ProductSource
from app.schemas.product import LookupRequest, LookupResponse, ProductResponse
from app.providers import provider_registry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/lookup", response_model=LookupResponse)
async def lookup_barcode(
    request: LookupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Lookup a barcode:
    1. Check local database first
    2. If not found, query configured providers
    3. If provider finds it, save to database
    4. Return result
    """
    code = request.code.strip()

    # Step 1: Check local database
    result = await db.execute(
        select(Product).where(Product.gtin == code)
    )
    existing_product = result.scalar_one_or_none()

    if existing_product:
        return LookupResponse(
            status="found",
            product=ProductResponse.model_validate(existing_product)
        )

    # Step 2: Try providers
    provider_result = await provider_registry.lookup(code)

    if not provider_result:
        return LookupResponse(
            status="not_found",
            product=None
        )

    # Step 3: Save to database
    # Map provider name to ProductSource
    source_mapping = {
        "openfoodfacts": ProductSource.OPENFOODFACTS,
        "opengtindb": ProductSource.OPENGTINDB,
        "upcitemdb": ProductSource.UPCITEMDB,
    }

    product_source = source_mapping.get(
        provider_result.provider_name,
        ProductSource.UNKNOWN
    )

    new_product = Product(
        gtin=code,
        name=provider_result.name,
        brand=provider_result.brand,
        image_url=provider_result.image_url,
        source=product_source,
        raw_payload=provider_result.raw_data
    )

    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except IntegrityError:
        # Race condition: another request saved this GTIN first
        await db.rollback()
        result = await db.execute(
            select(Product).where(Product.gtin == code)
        )
        new_product = result.scalar_one_or_none()
        if not new_product:
            logger.error(f"IntegrityError but product not found for GTIN {code}")
            return LookupResponse(status="not_found", product=None)
        return LookupResponse(
            status="found",
            product=ProductResponse.model_validate(new_product)
        )

    return LookupResponse(
        status="created",
        product=ProductResponse.model_validate(new_product)
    )
