# backend/app/services/import_service.py
import csv
import io
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.base_models import Order, OrderItem, OrderItemSplit, OrderStatus, FilamentSpool, FilamentStatus, SpoolType, User

def import_orders_from_csv(db: Session, file: UploadFile, current_user_id: int) -> Dict[str, int]:
    """
    Imports historical orders from a CSV file.
    CSV Format headers:
    order_date,store_name,product_name,quantity,price_per_unit,owner_username

    Historical orders are created with status 'DELIVERED' and their physical spools are automatically added to the inventory.
    """
    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contents))
    
    # Verify required headers are present
    required_headers = {"order_date", "store_name", "product_name", "quantity", "price_per_unit", "owner_username"}
    if not required_headers.issubset(set(reader.fieldnames or [])):
        raise ValueError(f"CSV is missing one or more required headers: {required_headers}")
        
    orders_created = 0
    items_created = 0
    spools_created = 0
    
    # Group rows by date and store to consolidate multiple items into single orders
    grouped_orders: Dict[tuple, List[dict]] = {}
    for row in reader:
        key = (row["order_date"].strip(), row["store_name"].strip())
        grouped_orders.setdefault(key, []).append(row)
        
    for (date_str, store_name), rows in grouped_orders.items():
        try:
            order_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            order_date = datetime.utcnow()
            
        # Create Order
        db_order = Order(
            order_date=order_date,
            store_name=store_name,
            status=OrderStatus.DELIVERED,
            creator_id=current_user_id
        )
        db.add(db_order)
        db.flush()  # Retrieve db_order.id
        orders_created += 1
        
        for row in rows:
            product_name = row["product_name"].strip()
            quantity = int(row["quantity"])
            price_per_unit = float(row["price_per_unit"])
            owner_username = row["owner_username"].strip()
            
            # Query owner ID, default to current user if username not found
            owner = db.query(User).filter(User.username == owner_username).first()
            owner_id = owner.id if owner else current_user_id
            
            # Create OrderItem
            db_item = OrderItem(
                product_name=product_name,
                quantity=quantity,
                price_per_unit=price_per_unit,
                order_id=db_order.id
            )
            db.add(db_item)
            db.flush()  # Retrieve db_item.id
            items_created += 1
            
            # Create OrderItemSplit (100% ownership)
            db_split = OrderItemSplit(
                order_item_id=db_item.id,
                user_id=owner_id,
                ownership_percentage=1.0
            )
            db.add(db_split)
            
            # Auto-create FilamentSpool records
            product_name_upper = product_name.upper()
            material_type = "PLA"
            for mat in ["PLA", "PETG", "ABS", "ASA", "TPU"]:
                if mat in product_name_upper:
                    material_type = mat
                    break
                    
            color_hex = "#FFFFFF"
            
            for _ in range(quantity):
                spool = FilamentSpool(
                    material_type=material_type,
                    color_hex=color_hex,
                    remaining_weight_g=1000.0,  # Full 1kg spool
                    price=price_per_unit,
                    spool_type=SpoolType.SPOOL,
                    status=FilamentStatus.AVAILABLE,  # Mark as available (historical)
                    owner_id=owner_id,
                    order_item_id=db_item.id
                )
                db.add(spool)
                spools_created += 1
                
    db.commit()
    return {
        "orders_imported": orders_created,
        "items_imported": items_created,
        "spools_created": spools_created
    }
