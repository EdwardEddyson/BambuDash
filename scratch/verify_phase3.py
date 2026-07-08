# scratch/verify_phase3.py
import sys
import os
import re
import json
from unittest.mock import patch, MagicMock

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.base_models import User, Printer, FilamentSpool, Order, OrderItem, OrderItemSplit, OrderStatus, FilamentStatus, UserRole
from app.api.v1.api import api_router
from app.db.session import get_db
from app.api.deps import get_current_user

def setup_db():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

def test_schema(engine):
    print("Running schema validation test...")
    with Session(engine) as session:
        # Create a printer with location
        printer = Printer(name="Test Printer", type="X1C", connection_info="192.168.1.50", location="Room 101")
        session.add(printer)

        # Create user
        user = User(username="test_user", hashed_password="xxx", role=UserRole.USER)
        session.add(user)
        session.flush()

        # Create order
        order = Order(store_name="Test Store", creator_id=user.id, status=OrderStatus.PLANNING)
        session.add(order)
        session.flush()

        # Create order item with metadata
        item = OrderItem(
            product_name="Bambu PLA Basic Black",
            quantity=2,
            price_per_unit=19.99,
            order_id=order.id,
            product_slug="bambu-pla-basic",
            sku="FL-PLA-BLK",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        # Create spool with metadata
        spool = FilamentSpool(
            material_type="PLA",
            color_hex="#000000",
            remaining_weight_g=1000.0,
            location="Plauen Shelf A",
            product_slug="bambu-pla-basic",
            sku="FL-PLA-BLK",
            variant_title="Black",
            owner_id=user.id,
            order_item_id=item.id
        )
        session.add(spool)
        session.commit()

        # Assertions
        db_printer = session.get(Printer, printer.id)
        assert db_printer.location == "Room 101"

        db_spool = session.get(FilamentSpool, spool.id)
        assert db_spool.location == "Plauen Shelf A"
        assert db_spool.product_slug == "bambu-pla-basic"
        assert db_spool.sku == "FL-PLA-BLK"
        assert db_spool.variant_title == "Black"

        db_item = session.get(OrderItem, item.id)
        assert db_item.product_slug == "bambu-pla-basic"
        assert db_item.sku == "FL-PLA-BLK"
        assert db_item.variant_title == "Black"

    print("Schema validation test: PASSED")

def test_split_billing_delivery(engine):
    print("Running delivery split-billing auto-allocation test...")
    from app.crud.crud_order import order as crud_order

    with Session(engine) as session:
        # Create users
        user_a = User(username="user_a", hashed_password="xxx")
        user_b = User(username="user_b", hashed_password="xxx")
        session.add(user_a)
        session.add(user_b)
        session.flush()

        # Create an order
        order = Order(store_name="Bambu Lab Store", creator_id=user_a.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Create item with quantity 3 and split 50-50
        item = OrderItem(
            product_name="Bambu PLA Basic Black",
            quantity=3,
            price_per_unit=25.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-BLK",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        split_a = OrderItemSplit(order_item_id=item.id, user_id=user_a.id, ownership_percentage=0.5)
        split_b = OrderItemSplit(order_item_id=item.id, user_id=user_b.id, ownership_percentage=0.5)
        session.add(split_a)
        session.add(split_b)

        # Create another item with quantity 1 and split 100% to user B
        item2 = OrderItem(
            product_name="Bambu PETG Tough Green",
            quantity=1,
            price_per_unit=30.00,
            order_id=order.id,
            product_slug="petg-tough",
            sku="SKU-PETG-GRN",
            variant_title="Green"
        )
        session.add(item2)
        session.flush()

        split_c = OrderItemSplit(order_item_id=item2.id, user_id=user_b.id, ownership_percentage=1.0)
        session.add(split_c)

        # Create a third item with PVA material and Grey variant_title to check new material and color logic
        item3 = OrderItem(
            product_name="Bambu PVA Grey Spool",
            quantity=1,
            price_per_unit=45.00,
            order_id=order.id,
            product_slug="pva-grey",
            sku="SKU-PVA-GRY",
            variant_title="Grey"
        )
        session.add(item3)
        session.flush()

        split_d = OrderItemSplit(order_item_id=item3.id, user_id=user_a.id, ownership_percentage=1.0)
        session.add(split_d)

        session.commit()

        # Reload order
        db_order = session.get(Order, order.id)

        # Call deliver_order
        delivered = crud_order.deliver_order(session, order=db_order)

        assert delivered.status == OrderStatus.DELIVERED

        # Fetch spools created (using select for clean warnings)
        spools = session.exec(select(FilamentSpool)).all()
        print(f"DEBUG: Found {len(spools)} spools: {[s.id for s in spools]}")
        for s in spools:
            print(f"DEBUG: Spool ID={s.id}, owner={s.owner_id}, item={s.order_item_id}, material={s.material_type}")
        # Total spools: 3 (from item 1) + 1 (from item 2) + 1 (from item 3) = 5
        assert len(spools) == 5

        # Spools from item 1:
        spools_item1 = [s for s in spools if s.order_item_id == item.id]
        assert len(spools_item1) == 3
        # Splits: user_a: 50%, user_b: 50%.
        # int(3 * 0.5 + 1e-9) = 1 spool for each.
        # remaining = 3 - 2 = 1 spool communal (owner_id = None).
        owners_item1 = [s.owner_id for s in spools_item1]
        assert owners_item1.count(user_a.id) == 1
        assert owners_item1.count(user_b.id) == 1
        assert owners_item1.count(None) == 1

        for s in spools_item1:
            assert s.status == FilamentStatus.DRAFT
            assert s.price == 25.00
            assert s.material_type == "PLA"
            assert s.product_slug == "pla-basic"
            assert s.sku == "SKU-PLA-BLK"
            assert s.variant_title == "Black"
            assert s.color_hex == "#000000"

        # Spools from item 2:
        spools_item2 = [s for s in spools if s.order_item_id == item2.id]
        assert len(spools_item2) == 1
        assert spools_item2[0].owner_id == user_b.id
        assert spools_item2[0].status == FilamentStatus.DRAFT
        assert spools_item2[0].price == 30.00
        assert spools_item2[0].material_type == "PETG"
        assert spools_item2[0].product_slug == "petg-tough"
        assert spools_item2[0].sku == "SKU-PETG-GRN"
        assert spools_item2[0].variant_title == "Green"
        assert spools_item2[0].color_hex == "#00FF00"

        # Spools from item 3:
        spools_item3 = [s for s in spools if s.order_item_id == item3.id]
        assert len(spools_item3) == 1
        assert spools_item3[0].owner_id == user_a.id
        assert spools_item3[0].status == FilamentStatus.DRAFT
        assert spools_item3[0].price == 45.00
        assert spools_item3[0].material_type == "PVA"
        assert spools_item3[0].product_slug == "pva-grey"
        assert spools_item3[0].sku == "SKU-PVA-GRY"
        assert spools_item3[0].variant_title == "Grey"
        assert spools_item3[0].color_hex == "#808080"

    print("Delivery split billing auto-allocation test: PASSED")

def test_makerworld_proxy():
    print("Running MakerWorld Search API proxy test...")
    test_app = FastAPI()
    test_app.include_router(api_router, prefix="/api/v1")
    client = TestClient(test_app)

    # Mock data for design/list API
    mock_api_data = {
        "code": 0,
        "msg": "success",
        "data": {
            "list": [
                {
                    "id": 1001,
                    "title": "API Model 1",
                    "cover": "https://makerworld.com/api/cover1.jpg",
                    "url": "/en/models/1001"
                },
                {
                    "id": 1002,
                    "title": "API Model 2",
                    "cover": "https://makerworld.com/api/cover2.jpg",
                    "url": "/en/models/1002"
                }
            ]
        }
    }

    # Test path 1: successful API response
    with patch("httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_data
        mock_get.return_value = mock_response

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["design_id"] == "1001"
        assert data[0]["title"] == "API Model 1"
        assert data[0]["image_url"] == "https://makerworld.com/api/cover1.jpg"
        assert data[0]["url"] == "https://makerworld.com/en/models/1001"

    print("MakerWorld API proxy path test: PASSED")

    # Test path 2: API fails, fallback to Next.js data scraper
    mock_html = """
    <html>
      <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
          "props": {
            "pageProps": {
              "dehydratedState": {
                "queries": [
                  {
                    "state": {
                      "data": {
                        "list": [
                          {
                            "id": 2001,
                            "title": "Scraped Model 1",
                            "cover": "https://makerworld.com/scraped1.jpg",
                            "url": "/en/models/2001"
                          }
                        ]
                      }
                    }
                  }
                ]
              }
            }
          }
        }
        </script>
      </body>
    </html>
    """
    with patch("httpx.get") as mock_get:
        # First call (API list endpoint) fails
        mock_response_api = MagicMock()
        mock_response_api.status_code = 500

        # Second call (search models endpoint) succeeds with html
        mock_response_scrape = MagicMock()
        mock_response_scrape.status_code = 200
        mock_response_scrape.text = mock_html

        mock_get.side_effect = [mock_response_api, mock_response_scrape]

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["design_id"] == "2001"
        assert data[0]["title"] == "Scraped Model 1"
        assert data[0]["image_url"] == "https://makerworld.com/scraped1.jpg"
        assert data[0]["url"] == "https://makerworld.com/en/models/2001"

    print("MakerWorld scraper fallback path test: PASSED")

    # Test path 3: Both fail, returns empty list
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = Exception("Network Down")
        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    print("MakerWorld failure path test: PASSED")

def test_split_validation():
    print("Running split validation constraints test...")
    from pydantic import ValidationError
    from app.schemas.order import OrderItemSplitCreate
    from app.models.base_models import OrderItemSplit

    # Test schema validation
    try:
        OrderItemSplitCreate(user_id=1, ownership_percentage=-0.1)
        raise AssertionError("ValidationError not raised for negative ownership_percentage in schema")
    except ValidationError:
        pass

    try:
        OrderItemSplitCreate(user_id=1, ownership_percentage=1.1)
        raise AssertionError("ValidationError not raised for ownership_percentage > 1.0 in schema")
    except ValidationError:
        pass

    # Also test model/db level validation using Pydantic validation methods
    try:
        if hasattr(OrderItemSplit, "model_validate"):
            OrderItemSplit.model_validate({"order_item_id": 1, "user_id": 1, "ownership_percentage": -0.1})
        else:
            OrderItemSplit.validate({"order_item_id": 1, "user_id": 1, "ownership_percentage": -0.1})
        raise AssertionError("ValidationError not raised for negative ownership_percentage in model")
    except ValidationError:
        pass

    try:
        if hasattr(OrderItemSplit, "model_validate"):
            OrderItemSplit.model_validate({"order_item_id": 1, "user_id": 1, "ownership_percentage": 1.1})
        else:
            OrderItemSplit.validate({"order_item_id": 1, "user_id": 1, "ownership_percentage": 1.1})
        raise AssertionError("ValidationError not raised for ownership_percentage > 1.0 in model")
    except ValidationError:
        pass

    print("Split validation constraints test: PASSED")

def test_delivery_authorization(engine):
    print("Running delivery authorization test...")
    test_app = FastAPI()
    test_app.include_router(api_router, prefix="/api/v1")

    # Setup test users and order in the DB
    with Session(engine) as session:
        user_creator = User(username="creator", hashed_password="xxx", role=UserRole.USER)
        user_other = User(username="other", hashed_password="xxx", role=UserRole.USER)
        user_admin = User(username="admin", hashed_password="xxx", role=UserRole.ADMIN)
        session.add(user_creator)
        session.add(user_other)
        session.add(user_admin)
        session.flush()

        order = Order(store_name="Test Store", creator_id=user_creator.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.commit()

        order_id = order.id
        creator_id = user_creator.id
        other_id = user_other.id
        admin_id = user_admin.id

    # Mock database session dependency override
    def get_db_override():
        with Session(engine) as session:
            yield session

    test_app.dependency_overrides[get_db] = get_db_override

    # Test 1: Creator user
    def get_current_user_creator():
        with Session(engine) as session:
            return session.get(User, creator_id)

    # Test 2: Other user (should return 403 Forbidden)
    def get_current_user_other():
        with Session(engine) as session:
            return session.get(User, other_id)

    # Test 3: Admin user (should succeed)
    def get_current_user_admin():
        with Session(engine) as session:
            return session.get(User, admin_id)

    client = TestClient(test_app)

    # Make request as non-creator/non-admin (other user)
    test_app.dependency_overrides[get_current_user] = get_current_user_other
    response = client.post(f"/api/v1/orders/{order_id}/deliver")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to deliver this order."

    # Make request as admin user (admin)
    test_app.dependency_overrides[get_current_user] = get_current_user_admin
    response = client.post(f"/api/v1/orders/{order_id}/deliver")
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"

    # Reset order status to test creator
    with Session(engine) as session:
        db_order = session.get(Order, order_id)
        db_order.status = OrderStatus.ORDERED
        session.add(db_order)
        session.commit()

    # Make request as creator user (creator)
    test_app.dependency_overrides[get_current_user] = get_current_user_creator
    response = client.post(f"/api/v1/orders/{order_id}/deliver")
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"

    test_app.dependency_overrides.clear()
    print("Delivery authorization test: PASSED")

def test_split_billing_overallocation(engine):
    print("Running delivery split-billing over-allocation cap test...")
    from app.crud.crud_order import order as crud_order
    with Session(engine) as session:
        user_a = User(username="user_oa", hashed_password="xxx")
        user_b = User(username="user_ob", hashed_password="xxx")
        session.add(user_a)
        session.add(user_b)
        session.flush()

        order = Order(store_name="Bambu Lab Store", creator_id=user_a.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Quantity 2. Splits: User A: 0.6, User B: 0.6 (Sum = 1.2, which is over 1.0)
        item = OrderItem(
            product_name="Bambu PLA Over",
            quantity=2,
            price_per_unit=25.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-OVR",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        split_a = OrderItemSplit(order_item_id=item.id, user_id=user_a.id, ownership_percentage=0.6)
        split_b = OrderItemSplit(order_item_id=item.id, user_id=user_b.id, ownership_percentage=0.6)
        session.add(split_a)
        session.add(split_b)
        session.commit()

        db_order = session.get(Order, order.id)
        crud_order.deliver_order(session, order=db_order)

        spools = session.exec(select(FilamentSpool).where(FilamentSpool.order_item_id == item.id)).all()
        # Should create exactly 2 spools, capped by remaining_qty
        assert len(spools) == 2
        owners = [s.owner_id for s in spools]
        assert owners.count(user_a.id) == 1
        assert owners.count(user_b.id) == 1

    print("Delivery split-billing over-allocation cap test: PASSED")

def test_makerworld_helpers():
    print("Running MakerWorld helper functions tests...")
    from app.api.v1.endpoints.makerworld import find_designs_in_dict

    # Test Mixed List check: first element is a string, second is a dict design.
    mixed_list = [
        "some metadata string",
        {"id": 123, "title": "Design 1", "cover": "http://img"}
    ]
    res = find_designs_in_dict(mixed_list)
    assert len(res) == 1
    assert res[0]["id"] == 123

    # Test Recursion limit check: very deep dict.
    deep_dict = {}
    curr = deep_dict
    for _ in range(20):
        curr["child"] = {}
        curr = curr["child"]
    curr["id"] = 999
    curr["title"] = "Deep Design"

    res_deep = find_designs_in_dict(deep_dict)
    # Recursion depth > 10 should return [] and not crash with RecursionError.
    assert res_deep == []

    print("MakerWorld helper functions tests: PASSED")

def test_csv_import_validation(engine):
    print("Running CSV import validation test...")
    import io
    from app.services.import_service import import_orders_from_csv
    from fastapi import UploadFile

    # Setup test user
    with Session(engine) as session:
        user = User(username="csv_user", hashed_password="xxx")
        session.add(user)
        session.commit()
        user_id = user.id

    # Scenario 1: Negative quantity
    csv_content_neg_qty = (
        "order_date,store_name,product_name,quantity,price_per_unit,owner_username\n"
        "2026-07-08,Bambu Lab,PLA,-1,19.99,csv_user\n"
    )
    file_neg_qty = UploadFile(filename="test.csv", file=io.BytesIO(csv_content_neg_qty.encode("utf-8")))

    with Session(engine) as session:
        try:
            import_orders_from_csv(session, file_neg_qty, user_id)
            raise AssertionError("ValueError not raised for negative quantity in CSV")
        except ValueError as e:
            assert "Quantity must be non-negative." in str(e)

    # Scenario 2: Negative price
    csv_content_neg_price = (
        "order_date,store_name,product_name,quantity,price_per_unit,owner_username\n"
        "2026-07-08,Bambu Lab,PLA,1,-19.99,csv_user\n"
    )
    file_neg_price = UploadFile(filename="test.csv", file=io.BytesIO(csv_content_neg_price.encode("utf-8")))

    with Session(engine) as session:
        try:
            import_orders_from_csv(session, file_neg_price, user_id)
            raise AssertionError("ValueError not raised for negative price in CSV")
        except ValueError as e:
            assert "Price per unit must be non-negative." in str(e)

    print("CSV import validation test: PASSED")

if __name__ == "__main__":
    test_split_validation()
    test_makerworld_helpers()
    test_schema(setup_db())
    test_split_billing_delivery(setup_db())
    test_split_billing_overallocation(setup_db())
    test_delivery_authorization(setup_db())
    test_csv_import_validation(setup_db())
    test_makerworld_proxy()
    print("All tests completed successfully!")
