# backend/app/api/v1/endpoints/store.py
from fastapi import APIRouter, HTTPException, status
from app.services.store_service import fetch_bambu_store_product, StoreProductInfo

router = APIRouter()

@router.get("/lookup/{product_slug}", response_model=StoreProductInfo)
def lookup_store_product(product_slug: str):
    """
    Look up pricing and availability for a product in the Bambu Lab Store by its product slug.
    Example slug: 'bambu-pla-basic'
    """
    product_info = fetch_bambu_store_product(product_slug)
    if not product_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with slug '{product_slug}' not found on Bambu Lab Store or service unavailable."
        )
    return product_info
