# backend/app/api/v1/endpoints/orders.py
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import OrderRead, OrderCreate, OrderItemCreate, OrderItemRead, CartItemUpdate
from app.crud import crud_order
from app.api.deps import get_current_user
from app.models.base_models import User, UserRole
from app.services.import_service import import_orders_from_csv

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
    Create a new order manually (starts in 'PLANNING' status).
    """
    try:
        return crud_order.create_with_creator(db=db, obj_in=order, creator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/cart", response_model=OrderRead)
def get_active_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the active shopping cart (planning order) for the current user.
    Creates an empty cart if one does not exist.
    """
    return crud_order.get_or_create_active_cart(db=db, creator_id=current_user.id)

@router.post("/cart/items", response_model=OrderItemRead)
def add_item_to_cart(
    item_in: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a line item to the user's active shopping cart.
    Increments quantity if item with the same product name already exists.
    """
    cart = crud_order.get_or_create_active_cart(db=db, creator_id=current_user.id)
    try:
        return crud_order.add_item_to_cart(db=db, cart=cart, item_in=item_in, creator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.patch("/cart/items/{item_id}", response_model=OrderItemRead)
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update quantity, unit price, or split ownership of a line item in the active cart.
    """
    try:
        return crud_order.update_cart_item(db=db, item_id=item_id, item_in=item_in, creator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a line item from the user's active shopping cart.
    """
    try:
        crud_order.remove_cart_item(db=db, item_id=item_id, creator_id=current_user.id)
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post("/cart/checkout", response_model=OrderRead)
def checkout_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Checkout the active shopping cart, changing its status to 'ORDERED'.
    """
    cart = crud_order.get_active_cart(db=db, creator_id=current_user.id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active shopping cart found.")
    try:
        return crud_order.checkout_cart(db=db, cart=cart)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{order_id}/deliver", response_model=OrderRead)
def deliver_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an order as 'DELIVERED'. This automatically converts all ordered items
    into draft physical FilamentSpools in the database for users to enrich.
    """
    order = crud_order.get(db=db, id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if not (current_user.role == UserRole.ADMIN or current_user.role == "admin" or current_user.id == order.creator_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deliver this order.")
    try:
        return crud_order.deliver_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/import/csv", response_model=Dict[str, int])
def import_historical_orders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a CSV file to import historical orders.
    CSV columns required: order_date, store_name, product_name, quantity, price_per_unit, owner_username
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be a CSV.")
    try:
        return import_orders_from_csv(db=db, file=file, current_user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to import CSV: {e}")
