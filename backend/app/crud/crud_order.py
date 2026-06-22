# backend/app/crud/crud_order.py
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.base_models import Order
from app.schemas.order import OrderCreate, OrderUpdate # Define OrderUpdate in schemas

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create_with_creator(self, db: Session, *, obj_in: OrderCreate, creator_id: int) -> Order:
        # This is a simplified create. A real implementation would also create
        # the OrderItem and OrderItemSplit entries from the schema.
        db_obj = Order(
            store_name=obj_in.store_name,
            creator_id=creator_id
        )
        # ... logic to create items and splits would go here ...
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


order = CRUDOrder(Order)

# Dummy OrderUpdate for CRUDBase generic
from pydantic import BaseModel
class OrderUpdate(BaseModel):
    pass
