# backend/app/services/store_service.py
import httpx
from typing import Optional, List
from pydantic import BaseModel

class ProductVariant(BaseModel):
    id: int
    title: str
    price: float  # Price in standard units (e.g., Euros/Dollars)
    available: bool
    sku: Optional[str] = None

class StoreProductInfo(BaseModel):
    title: str
    handle: str
    price_min: float
    price_max: float
    available: bool
    variants: List[ProductVariant]

def fetch_bambu_store_product(product_slug: str) -> Optional[StoreProductInfo]:
    """
    Fetches product information (price, availability, variants) from the Bambu Lab Store.
    Uses the public Shopify JSON payload (.js endpoint) for robust structured data.
    """
    url = f"https://store.bambulab.com/products/{product_slug}.js"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        if response.status_code != 200:
            return None

        data = response.json()

        variants = []
        for v in data.get("variants", []):
            # Shopify prices are in cents (e.g. 2499 representing 24.99)
            price_units = float(v.get("price", 0)) / 100.0
            variants.append(ProductVariant(
                id=v.get("id"),
                title=v.get("title", ""),
                price=price_units,
                available=v.get("available", False),
                sku=v.get("sku")
            ))

        return StoreProductInfo(
            title=data.get("title", ""),
            handle=data.get("handle", ""),
            price_min=float(data.get("price_min", 0)) / 100.0,
            price_max=float(data.get("price_max", 0)) / 100.0,
            available=data.get("available", False),
            variants=variants
        )
    except Exception as e:
        print(f"Error fetching Bambu Lab Store product details: {e}")
        return None
