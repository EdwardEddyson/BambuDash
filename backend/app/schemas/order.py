# backend/app/schemas/order.py
from typing import Optional, List
from sqlmodel import SQLModel
from app.models.base_models import OrderStatus

# --- Order Item Split ---
class OrderItemSplitBase(SQLModel):
    user_id: int
    ownership_percentage: float

class OrderItemSplitCreate(OrderItemSplitBase):
    pass

class OrderItemSplitRead(OrderItemSplitBase):
    pass

# --- Order Item ---
class OrderItemBase(SQLModel):
    product_name: str
    quantity: int
    price_per_unit: float

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

class OrderRead(OrderBase):
    id: int
    order_date: str
    status: OrderStatus
    creator_id: int
    items: List[OrderItemRead] = []
