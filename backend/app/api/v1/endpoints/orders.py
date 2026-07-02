# backend/app/api/v1/endpoints/orders.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import OrderRead, OrderCreate
from app.crud import crud_order
from app.api.deps import get_current_user
from app.models.base_models import User

router = APIRouter()

@router.get("/", response_model=List[OrderRead])
def get_all_orders(db: Session = Depends(get_db)):
    """
    Retrieve all orders.
    """
    return crud_order.get_multi(db)

@router.post("/", response_model=OrderRead)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new order (starts in 'PLANNING' status).
    """
    return crud_order.create_with_creator(db=db, obj_in=order, creator_id=current_user.id)
