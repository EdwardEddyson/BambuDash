# scratch/verify_issue_7.py
import sys
import os
from sqlalchemy.pool import StaticPool

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import SQLModel, create_engine, Session
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.base_models import User, FilamentSpool, Order, OrderItem, OrderStatus, FilamentStatus, UserRole, SpoolType
from app.api.v1.api import api_router
from app.db.session import get_db

def setup_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

def test_unlinked_matches():
    print("Setting up test database...")
    engine = setup_db()

    # Create mock data
    with Session(engine) as session:
        # Create users
        user_a = User(username="user_a", hashed_password="xxx", role=UserRole.USER)
        user_b = User(username="user_b", hashed_password="xxx", role=UserRole.USER)
        session.add(user_a)
        session.add(user_b)
        session.flush()

        # Create orders & items to link to spools
        order = Order(store_name="Test Store", creator_id=user_a.id, status=OrderStatus.DELIVERED)
        session.add(order)
        session.flush()

        item_red_a = OrderItem(product_name="Red PLA Spool A", quantity=1, price_per_unit=20.0, order_id=order.id, sku="SKU-RED-A")
        item_red_communal = OrderItem(product_name="Red PLA Spool Communal", quantity=1, price_per_unit=20.0, order_id=order.id, sku="SKU-RED-COMMUNAL")
        item_petg = OrderItem(product_name="Red PETG Spool", quantity=1, price_per_unit=25.0, order_id=order.id, sku="SKU-PETG")
        item_blue = OrderItem(product_name="Blue PLA Spool", quantity=1, price_per_unit=20.0, order_id=order.id, sku="SKU-BLUE")
        item_red_b = OrderItem(product_name="Red PLA Spool B", quantity=1, price_per_unit=20.0, order_id=order.id, sku="SKU-RED-B")

        session.add(item_red_a)
        session.add(item_red_communal)
        session.add(item_petg)
        session.add(item_blue)
        session.add(item_red_b)
        session.flush()

        # Manually create physical spools corresponding to order items
        # Spool 1: PLA Red, owned by user_a, unlinked (tray_id is null)
        s1 = FilamentSpool(
            material_type="PLA",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_a.id,
            order_item_id=item_red_a.id,
            price=20.0,
            sku="SKU-RED-A"
        )
        # Spool 2: PLA Red, communal (owner_id is None), unlinked (tray_id is null)
        s2 = FilamentSpool(
            material_type="PLA",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=None,
            order_item_id=item_red_communal.id,
            price=20.0,
            sku="SKU-RED-COMMUNAL"
        )
        # Spool 3: PLA Red, owned by user_a, ALREADY AVAILABLE (enriched)
        s3 = FilamentSpool(
            material_type="PLA",
            color_hex="#FF0000",
            remaining_weight_g=800.0,
            status=FilamentStatus.AVAILABLE,
            owner_id=user_a.id,
            order_item_id=item_red_a.id,
            price=20.0
        )
        # Spool 4: PLA Red, owned by user_a, linked to AMS tray_id (not unlinked)
        s4 = FilamentSpool(
            material_type="PLA",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_a.id,
            order_item_id=item_red_a.id,
            bambu_tray_id="AMS_TRAY_1"
        )
        # Spool 5: PETG Red, owned by user_a, unlinked
        s5 = FilamentSpool(
            material_type="PETG",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_a.id,
            order_item_id=item_petg.id,
            price=25.0
        )
        # Spool 6: PLA Blue, owned by user_a, unlinked
        s6 = FilamentSpool(
            material_type="PLA",
            color_hex="#0000FF",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_a.id,
            order_item_id=item_blue.id,
            price=20.0
        )
        # Spool 7: PLA Red, owned by user_b, unlinked
        s7 = FilamentSpool(
            material_type="PLA",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_b.id,
            order_item_id=item_red_b.id,
            price=20.0
        )

        session.add(s1)
        session.add(s2)
        session.add(s3)
        session.add(s4)
        session.add(s5)
        session.add(s6)
        session.add(s7)

        # Spool 8: The auto-discovered draft spool from AMS (bambu_tray_id is set, status DRAFT, no order_item_id)
        # This is the spool we are enriching
        discovered_spool = FilamentSpool(
            material_type="PLA",
            bambu_tray_id="AMS_TRAY_DISCOVERED",
            color_hex="#FF0000",
            remaining_weight_g=1000.0,
            status=FilamentStatus.DRAFT,
            owner_id=user_a.id
        )
        session.add(discovered_spool)
        session.flush()

        discovered_spool_id = discovered_spool.id
        user_a_id = user_a.id
        user_b_id = user_b.id
        session.commit()

    # Setup FastAPI app with overrides
    test_app = FastAPI()
    test_app.include_router(api_router, prefix="/api/v1")

    def get_db_override():
        with Session(engine) as session:
            yield session

    test_app.dependency_overrides[get_db] = get_db_override
    client = TestClient(test_app)

    print("Running matching endpoint tests...")

    # Case 1: Match by material + color + owner_id (user_a)
    print("Test 1: Match by material_type, color_hex, owner_id (user_a)")
    response = client.get("/api/v1/filaments/unlinked-matches", params={
        "material_type": "PLA",
        "color_hex": "#FF0000",
        "owner_id": user_a_id
    })
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert len(data) == 2, f"Expected 2 matches, got {len(data)}"
    matched_ids = [item["id"] for item in data]
    assert 1 in matched_ids, "Should match Spool 1"
    assert 2 in matched_ids, "Should match Spool 2 (communal)"
    # Verify extra details are returned
    for item in data:
        assert item["order_id"] is not None
        assert item["order_date"] is not None
        assert item["sku"] is not None
    print("Test 1 passed.")

    # Case 2: Match by material + color + owner_id (None)
    print("Test 2: Match by material_type, color_hex, owner_id (None)")
    response = client.get("/api/v1/filaments/unlinked-matches", params={
        "material_type": "PLA",
        "color_hex": "#FF0000"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1, f"Expected 1 match, got {len(data)}"
    assert data[0]["id"] == 2, f"Expected Spool 2, got {data[0]['id']}"
    print("Test 2 passed.")

    # Case 3: Match by spool_id (using the auto-discovered spool ID)
    print("Test 3: Match by spool_id")
    response = client.get("/api/v1/filaments/unlinked-matches", params={
        "spool_id": discovered_spool_id
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2, f"Expected 2 matches, got {len(data)}"
    matched_ids = [item["id"] for item in data]
    assert 1 in matched_ids
    assert 2 in matched_ids
    print("Test 3 passed.")

    # Case 4: Non-existent spool_id
    print("Test 4: Match by non-existent spool_id")
    response = client.get("/api/v1/filaments/unlinked-matches", params={
        "spool_id": 9999
    })
    assert response.status_code == 404
    print("Test 4 passed.")

    # Case 5: Missing parameters
    print("Test 5: Match by missing parameters")
    response = client.get("/api/v1/filaments/unlinked-matches", params={
        "material_type": "PLA"
    })
    assert response.status_code == 400
    print("Test 5 passed.")

    print("All backend unlinked-matches API tests passed successfully!")

if __name__ == "__main__":
    test_unlinked_matches()
