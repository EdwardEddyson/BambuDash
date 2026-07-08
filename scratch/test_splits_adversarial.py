# scratch/test_splits_adversarial.py
import sys
import os

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import SQLModel, create_engine, Session
from app.models.base_models import User, Order, OrderItem, OrderItemSplit, OrderStatus, FilamentSpool
from app.crud.crud_order import order as crud_order

def setup_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

def test_split_precision_issues(engine):
    print("\n--- Test 1: 3-way split (33.3%, 33.3%, 33.4%) with Qty 3 ---")
    with Session(engine) as session:
        # Create users
        u1 = User(username="user1", hashed_password="x")
        u2 = User(username="user2", hashed_password="x")
        u3 = User(username="user3", hashed_password="x")
        session.add_all([u1, u2, u3])
        session.flush()

        # Create Order
        order = Order(store_name="Bambu Store", creator_id=u1.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Create Item with quantity 3
        item = OrderItem(
            product_name="Bambu PLA Basic Black",
            quantity=3,
            price_per_unit=20.0,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-1",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        # Create Splits (sum to 1.0)
        split1 = OrderItemSplit(order_item_id=item.id, user_id=u1.id, ownership_percentage=0.333)
        split2 = OrderItemSplit(order_item_id=item.id, user_id=u2.id, ownership_percentage=0.333)
        split3 = OrderItemSplit(order_item_id=item.id, user_id=u3.id, ownership_percentage=0.334)
        session.add_all([split1, split2, split3])
        session.commit()

        # Deliver
        crud_order.deliver_order(session, order=order)

        # Check spools
        spools = session.query(FilamentSpool).filter(FilamentSpool.order_item_id == item.id).all()
        print(f"Total spools created: {len(spools)} (expected: 3)")
        owners = [s.owner_id for s in spools]
        print(f"Spool owners: {owners}")
        print(f"User 1 (33.3%): {owners.count(u1.id)} spools (expected: 1)")
        print(f"User 2 (33.3%): {owners.count(u2.id)} spools (expected: 1)")
        print(f"User 3 (33.4%): {owners.count(u3.id)} spools (expected: 1)")
        print(f"Communal (None): {owners.count(None)} spools (expected: 0)")

def test_split_over_allocation(engine):
    print("\n--- Test 2: Over-allocation due to splits > 1.0 (but within 1e-4 limit) ---")
    with Session(engine) as session:
        u1 = User(username="user1_o", hashed_password="x")
        u2 = User(username="user2_o", hashed_password="x")
        session.add_all([u1, u2])
        session.flush()

        order = Order(store_name="Bambu Store", creator_id=u1.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Item quantity = 20,000
        item = OrderItem(
            product_name="Bambu PLA Basic Black Large",
            quantity=20000,
            price_per_unit=20.0,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-2",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        # Create Splits that sum to 1.0001 (deviation is 0.0001 <= 1e-4, so it is allowed)
        split1 = OrderItemSplit(order_item_id=item.id, user_id=u1.id, ownership_percentage=0.50005)
        split2 = OrderItemSplit(order_item_id=item.id, user_id=u2.id, ownership_percentage=0.50005)
        session.add_all([split1, split2])
        session.commit()

        # Deliver
        try:
            crud_order.deliver_order(session, order=order)
            spools = session.query(FilamentSpool).filter(FilamentSpool.order_item_id == item.id).all()
            print(f"Total spools created: {len(spools)} (expected: 20000)")
            if len(spools) > 20000:
                print(f"CRITICAL BUG: Created {len(spools)} spools, which exceeds the order quantity of 20000!")
        except Exception as e:
            print(f"Failed with exception: {e}")

def test_zero_and_negative_splits(engine):
    print("\n--- Test 3: Zero and Negative splits (if bypass validation/insert directly) ---")
    with Session(engine) as session:
        u1 = User(username="user1_neg", hashed_password="x")
        u2 = User(username="user2_neg", hashed_password="x")
        session.add_all([u1, u2])
        session.flush()

        order = Order(store_name="Bambu Store", creator_id=u1.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        item = OrderItem(
            product_name="Bambu PLA Basic Black Neg",
            quantity=2,
            price_per_unit=20.0,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-3",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        # Split: user1 = -0.5, user2 = 1.5 (total = 1.0)
        split1 = OrderItemSplit(order_item_id=item.id, user_id=u1.id, ownership_percentage=-0.5)
        split2 = OrderItemSplit(order_item_id=item.id, user_id=u2.id, ownership_percentage=1.5)
        session.add_all([split1, split2])
        session.commit()

        # Deliver
        crud_order.deliver_order(session, order=order)
        spools = session.query(FilamentSpool).filter(FilamentSpool.order_item_id == item.id).all()
        print(f"Total spools created: {len(spools)} (expected: 2)")
        owners = [s.owner_id for s in spools]
        print(f"Spool owners: {owners}")
        print(f"User 1 (-50%): {owners.count(u1.id)} spools (expected: 0)")
        print(f"User 2 (150%): {owners.count(u2.id)} spools (expected: 3? Or 2?)")

if __name__ == "__main__":
    db = setup_db()
    test_split_precision_issues(db)
    test_split_over_allocation(db)
    test_zero_and_negative_splits(db)
