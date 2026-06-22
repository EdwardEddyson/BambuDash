# backend/app/services/order_service.py
from sqlalchemy.orm import Session
from app.models.base_models import Order, User

def calculate_user_share_for_order(db: Session, order: Order, user: User) -> float:
    """
    Calculates a single user's total financial share for a given order.
    The core of the split-billing logic.
    """
    total_share = 0.0
    for item in order.items:
        for split in item.user_links:
            if split.user_id == user.id:
                # Add this user's share of the current item to their total
                item_cost = item.price_per_unit * item.quantity
                total_share += item_cost * split.ownership_percentage
                break # Move to the next item
    return total_share
