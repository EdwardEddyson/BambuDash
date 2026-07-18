# scratch/test_csv_import_adversarial.py
import sys
import os
import io
from fastapi import UploadFile
from sqlmodel import SQLModel, create_engine, Session

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.models.base_models import User, Order, OrderItem, OrderItemSplit, FilamentSpool
from app.services.import_service import import_orders_from_csv

def setup_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

def test_csv_import_negative_quantity(engine):
    print("\n--- CSV Test 1: Import with negative quantity ---")
    with Session(engine) as session:
        # Create a user first
        user = User(username="test_user", hashed_password="xxx")
        session.add(user)
        session.flush()

        csv_content = (
            "order_date,store_name,product_name,quantity,price_per_unit,owner_username\n"
            "2026-07-08,Bambu Store,Bambu PLA Black,-5,19.99,test_user\n"
        )
        file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content.encode("utf-8")))

        res = import_orders_from_csv(session, file, user.id)
        print(f"Import results: {res}")

        # Check database
        orders = session.query(Order).all()
        print(f"Orders created: {len(orders)}, status: {[o.status for o in orders]}")
        items = session.query(OrderItem).all()
        print(f"OrderItems created: {len(items)}, quantity: {[i.quantity for i in items]}")
        spools = session.query(FilamentSpool).all()
        print(f"FilamentSpools created: {len(spools)}")

def test_csv_import_missing_headers(engine):
    print("\n--- CSV Test 2: Import with missing headers ---")
    with Session(engine) as session:
        # User is already created in previous test, let's query it
        user = session.query(User).filter(User.username == "test_user").first()

        # Missing 'owner_username'
        csv_content = (
            "order_date,store_name,product_name,quantity,price_per_unit\n"
            "2026-07-08,Bambu Store,Bambu PLA Black,2,19.99\n"
        )
        file = UploadFile(filename="test.csv", file=io.BytesIO(csv_content.encode("utf-8")))

        try:
            import_orders_from_csv(session, file, user.id)
            print("Import succeeded despite missing headers!")
        except ValueError as e:
            print(f"Caught expected ValueError: {e}")

if __name__ == "__main__":
    db = setup_db()
    test_csv_import_negative_quantity(db)
    test_csv_import_missing_headers(db)
