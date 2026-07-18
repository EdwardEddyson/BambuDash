# backend/app/crud/crud_order.py
from typing import Optional, List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.base_models import Order, OrderItem, OrderItemSplit, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderItemCreate, CartItemUpdate

def parse_color_hex(text: str) -> str:
    import re
    color_map = {
        "black": "#000000",
        "white": "#FFFFFF",
        "red": "#FF0000",
        "green": "#00FF00",
        "blue": "#0000FF",
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "grey": "#808080",
        "gray": "#808080",
        "silver": "#C0C0C0",
        "gold": "#FFD700",
        "purple": "#800080",
        "pink": "#FFC0CB",
        "brown": "#A52A2A"
    }
    text_lower = text.lower()
    for color, hex_code in color_map.items():
        if re.search(r'\b' + re.escape(color) + r'\b', text_lower):
            return hex_code
    return "#FFFFFF"

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create_with_creator(self, db: Session, *, obj_in: OrderCreate, creator_id: int) -> Order:
        # Create order in PLANNING status
        db_obj = Order(
            store_name=obj_in.store_name,
            creator_id=creator_id,
            status=OrderStatus.PLANNING
        )
        db.add(db_obj)
        db.flush()  # Populate db_obj.id

        # Process each item in the order
        for item_in in obj_in.items:
            db_item = OrderItem(
                product_name=item_in.product_name,
                quantity=item_in.quantity,
                price_per_unit=item_in.price_per_unit,
                order_id=db_obj.id,
                product_slug=item_in.product_slug,
                sku=item_in.sku,
                variant_title=item_in.variant_title
            )
            db.add(db_item)
            db.flush()  # Populate db_item.id

            if not item_in.splits:
                # Default to 100% ownership for the creator if no splits are specified
                db_split = OrderItemSplit(
                    order_item_id=db_item.id,
                    user_id=creator_id,
                    ownership_percentage=1.0
                )
                db.add(db_split)
            else:
                # Validate splits sum to 1.0 (100%)
                total_percentage = sum(s.ownership_percentage for s in item_in.splits)
                if abs(total_percentage - 1.0) > 1e-4:
                    raise ValueError(
                        f"Ownership percentages for item '{item_in.product_name}' must sum to exactly 1.0 (100%). "
                        f"Found: {total_percentage}"
                    )

                for split_in in item_in.splits:
                    db_split = OrderItemSplit(
                        order_item_id=db_item.id,
                        user_id=split_in.user_id,
                        ownership_percentage=split_in.ownership_percentage
                    )
                    db.add(db_split)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_active_cart(self, db: Session, *, creator_id: int) -> Optional[Order]:
        """
        Retrieves the active planning order (shopping cart) for a user.
        """
        return db.query(Order).filter(
            Order.creator_id == creator_id,
            Order.status == OrderStatus.PLANNING
        ).first()

    def get_or_create_active_cart(self, db: Session, *, creator_id: int) -> Order:
        """
        Gets the active cart, or creates a new empty one if none exists.
        """
        cart = self.get_active_cart(db, creator_id=creator_id)
        if not cart:
            cart = Order(
                store_name="Bambu Lab Store",
                creator_id=creator_id,
                status=OrderStatus.PLANNING
            )
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    def add_item_to_cart(self, db: Session, *, cart: Order, item_in: OrderItemCreate, creator_id: int) -> OrderItem:
        """
        Adds a new item to the active cart, or increments quantity and updates splits if it already exists.
        """
        existing_item = db.query(OrderItem).filter(
            OrderItem.order_id == cart.id,
            OrderItem.product_name == item_in.product_name
        ).first()

        if existing_item:
            existing_item.quantity += item_in.quantity
            db.add(existing_item)
            db.flush()

            if item_in.splits:
                # Delete existing splits and replace with new ones
                db.query(OrderItemSplit).filter(OrderItemSplit.order_item_id == existing_item.id).delete()
                total_percentage = sum(s.ownership_percentage for s in item_in.splits)
                if abs(total_percentage - 1.0) > 1e-4:
                    raise ValueError(f"Splits must sum to 1.0. Found: {total_percentage}")

                for split_in in item_in.splits:
                    db_split = OrderItemSplit(
                        order_item_id=existing_item.id,
                        user_id=split_in.user_id,
                        ownership_percentage=split_in.ownership_percentage
                    )
                    db.add(db_split)

            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            db_item = OrderItem(
                product_name=item_in.product_name,
                quantity=item_in.quantity,
                price_per_unit=item_in.price_per_unit,
                order_id=cart.id,
                product_slug=item_in.product_slug,
                sku=item_in.sku,
                variant_title=item_in.variant_title
            )
            db.add(db_item)
            db.flush()

            if not item_in.splits:
                db_split = OrderItemSplit(
                    order_item_id=db_item.id,
                    user_id=creator_id,
                    ownership_percentage=1.0
                )
                db.add(db_split)
            else:
                total_percentage = sum(s.ownership_percentage for s in item_in.splits)
                if abs(total_percentage - 1.0) > 1e-4:
                    raise ValueError(f"Splits must sum to 1.0. Found: {total_percentage}")
                for split_in in item_in.splits:
                    db_split = OrderItemSplit(
                        order_item_id=db_item.id,
                        user_id=split_in.user_id,
                        ownership_percentage=split_in.ownership_percentage
                    )
                    db.add(db_split)

            db.commit()
            db.refresh(db_item)
            return db_item

    def update_cart_item(self, db: Session, *, item_id: int, item_in: CartItemUpdate, creator_id: int) -> OrderItem:
        """
        Updates an existing item's quantity, price, or splits in the active cart.
        """
        db_item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not db_item:
            raise ValueError("Item not found.")

        cart = db_item.order
        if cart.status != OrderStatus.PLANNING or cart.creator_id != creator_id:
            raise PermissionError("Cannot modify items in a submitted order or another user's cart.")

        if item_in.quantity is not None:
            db_item.quantity = item_in.quantity
        if item_in.price_per_unit is not None:
            db_item.price_per_unit = item_in.price_per_unit
        if item_in.product_slug is not None:
            db_item.product_slug = item_in.product_slug
        if item_in.sku is not None:
            db_item.sku = item_in.sku
        if item_in.variant_title is not None:
            db_item.variant_title = item_in.variant_title

        if item_in.splits is not None:
            db.query(OrderItemSplit).filter(OrderItemSplit.order_item_id == db_item.id).delete()
            if not item_in.splits:
                db_split = OrderItemSplit(
                    order_item_id=db_item.id,
                    user_id=creator_id,
                    ownership_percentage=1.0
                )
                db.add(db_split)
            else:
                total_percentage = sum(s.ownership_percentage for s in item_in.splits)
                if abs(total_percentage - 1.0) > 1e-4:
                    raise ValueError(f"Splits must sum to 1.0. Found: {total_percentage}")
                for split_in in item_in.splits:
                    db_split = OrderItemSplit(
                        order_item_id=db_item.id,
                        user_id=split_in.user_id,
                        ownership_percentage=split_in.ownership_percentage
                    )
                    db.add(db_split)

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def remove_cart_item(self, db: Session, *, item_id: int, creator_id: int) -> OrderItem:
        """
        Removes an item from the shopping cart.
        """
        db_item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not db_item:
            raise ValueError("Item not found.")

        cart = db_item.order
        if cart.status != OrderStatus.PLANNING or cart.creator_id != creator_id:
            raise PermissionError("Cannot remove items from a submitted order or another user's cart.")

        # Delete splits first
        db.query(OrderItemSplit).filter(OrderItemSplit.order_item_id == item_id).delete()
        db.delete(db_item)
        db.commit()
        return db_item

    def checkout_cart(self, db: Session, *, cart: Order) -> Order:
        """
        Submits the cart, changing status from PLANNING to ORDERED.
        """
        if cart.status != OrderStatus.PLANNING:
            raise ValueError("Only planning orders (carts) can be checked out.")
        if not cart.items:
            raise ValueError("Cannot checkout an empty shopping cart.")

        cart.status = OrderStatus.ORDERED
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    def deliver_order(self, db: Session, *, order: Order) -> Order:
        """
        Marks an order as delivered and automatically generates a FilamentSpool DRAFT
        in the database for each unit of items in the order using split billing allocation.
        """
        if order.status != OrderStatus.ORDERED:
            raise ValueError("Only ordered orders can be marked as delivered.")

        from app.models.base_models import FilamentSpool, FilamentStatus, SpoolType

        order.status = OrderStatus.DELIVERED
        db.add(order)

        # Auto-create physical spools
        for item in order.items:
            product_name_upper = item.product_name.upper()
            material_type = "PLA"  # Default fallback
            for mat in ["PLA", "PETG", "ABS", "ASA", "TPU", "PA", "PC", "PET", "PVA"]:
                if mat in product_name_upper:
                    material_type = mat
                    break

            # Simple color parser (e.g. searching for names) or default white
            color_hex = parse_color_hex((item.variant_title or "") + " " + item.product_name)

            # Sort splits by user_id to ensure deterministic order.
            sorted_splits = sorted(item.user_links, key=lambda s: s.user_id)
            allocated_owners = []
            for split in sorted_splits:
                num_spools = int(item.quantity * split.ownership_percentage + 1e-9)
                remaining_qty = max(0, item.quantity - len(allocated_owners))
                num_spools = min(num_spools, remaining_qty)
                num_spools = max(0, num_spools)
                allocated_owners.extend([split.user_id] * num_spools)

            # Pad remaining spools with None (communal)
            while len(allocated_owners) < item.quantity:
                allocated_owners.append(None)

            # Create a spool for each unit
            for owner_id in allocated_owners:
                spool = FilamentSpool(
                    material_type=material_type,
                    color_hex=color_hex,
                    remaining_weight_g=1000.0,  # 1kg standard size
                    price=item.price_per_unit,
                    spool_type=SpoolType.SPOOL,
                    status=FilamentStatus.DRAFT,  # Needs enrichment
                    owner_id=owner_id,
                    order_item_id=item.id,
                    product_slug=item.product_slug,
                    sku=item.sku,
                    variant_title=item.variant_title
                )
                db.add(spool)

        db.commit()
        db.refresh(order)
        return order


order = CRUDOrder(Order)
