# backend/app/schemas/order.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from app.models.base_models import OrderStatus

# --- Order Item Split ---
class OrderItemSplitBase(SQLModel):
    user_id: int
    ownership_percentage: float = Field(default=1.0, ge=0.0, le=1.0)

class OrderItemSplitCreate(OrderItemSplitBase):
    pass

class OrderItemSplitRead(OrderItemSplitBase):
    pass

# --- Order Item ---
class OrderItemBase(SQLModel):
    product_name: str
    quantity: int
    price_per_unit: float
    product_slug: Optional[str] = None
    sku: Optional[str] = None
    variant_title: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    splits: List[OrderItemSplitCreate] = []

class OrderItemRead(OrderItemBase):
    id: int
    user_links: List[OrderItemSplitRead] = []

# --- Order ---
class OrderBase(SQLModel):
    store_name: Optional[str] = "Bambu Lab Store"

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

# Properties to receive via API on order update
# All fields are optional for partial updates
class OrderUpdate(SQLModel):
    store_name: Optional[str] = None
    status: Optional[OrderStatus] = None

class CartItemUpdate(SQLModel):
    quantity: Optional[int] = None
    price_per_unit: Optional[float] = None
    splits: Optional[List[OrderItemSplitCreate]] = None
    product_slug: Optional[str] = None
    sku: Optional[str] = None
    variant_title: Optional[str] = None

class OrderRead(OrderBase):
    id: int
    order_date: datetime
    status: OrderStatus
    creator_id: int
    items: List[OrderItemRead] = []
