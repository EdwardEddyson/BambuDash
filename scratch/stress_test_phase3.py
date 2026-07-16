# scratch/stress_test_phase3.py
import sys
import os
import re
import json
from unittest.mock import patch, MagicMock
import httpx

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.models.base_models import User, Printer, FilamentSpool, Order, OrderItem, OrderItemSplit, OrderStatus, FilamentStatus, UserRole
from app.api.v1.api import api_router
from app.crud.crud_order import order as crud_order

def setup_db():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

def test_split_billing_negative_splits(engine):
    print("Running stress test: split billing with negative/overflowing percentages...")
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

        # Quantity 2. Splits sum to 1.0 but contain negative/overflow:
        # User A: -0.5, User B: 1.5
        item = OrderItem(
            product_name="Bambu PLA Basic Black",
            quantity=2,
            price_per_unit=25.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-BLK",
            variant_title="Black"
        )
        session.add(item)
        session.flush()

        split_a = OrderItemSplit(order_item_id=item.id, user_id=user_a.id, ownership_percentage=-0.5)
        split_b = OrderItemSplit(order_item_id=item.id, user_id=user_b.id, ownership_percentage=1.5)
        session.add(split_a)
        session.add(split_b)
        session.commit()

        db_order = session.get(Order, order.id)

        # Execute delivery
        try:
            delivered = crud_order.deliver_order(session, order=db_order)
            spools = session.exec(select(FilamentSpool).where(FilamentSpool.order_item_id == item.id)).all()
            print(f"-> Negative/overflow splits test completed. Quantity={item.quantity}, Created Spools={len(spools)}")
            for s in spools:
                print(f"   Spool ID={s.id}, Owner={s.owner_id}")

            # Check if quantity was violated
            if len(spools) != item.quantity:
                print(f"BUG DETECTED: Created {len(spools)} spools for an ordered quantity of {item.quantity}!")
        except Exception as e:
            print(f"-> Negative/overflow splits test raised exception: {type(e).__name__}: {str(e)}")

def test_split_billing_extremely_tiny_splits(engine):
    print("Running stress test: split billing with extremely tiny percentages...")
    with Session(engine) as session:
        user_a = User(username="user_a2", hashed_password="xxx")
        user_b = User(username="user_b2", hashed_password="xxx")
        session.add(user_a)
        session.add(user_b)
        session.flush()

        order = Order(store_name="Bambu Lab Store", creator_id=user_a.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Quantity 1. Splits: User A: 1e-15, User B: 1.0 (fails sum check? Or passes?)
        # Let's try splits that sum to exactly 1.0 (e.g. A: 1e-15, B: 1.0 - 1e-15)
        item = OrderItem(
            product_name="Bambu PLA Basic White",
            quantity=1,
            price_per_unit=25.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-WHT",
            variant_title="White"
        )
        session.add(item)
        session.flush()

        split_a = OrderItemSplit(order_item_id=item.id, user_id=user_a.id, ownership_percentage=1e-15)
        split_b = OrderItemSplit(order_item_id=item.id, user_id=user_b.id, ownership_percentage=1.0 - 1e-15)
        session.add(split_a)
        session.add(split_b)
        session.commit()

        db_order = session.get(Order, order.id)
        delivered = crud_order.deliver_order(session, order=db_order)
        spools = session.exec(select(FilamentSpool).where(FilamentSpool.order_item_id == item.id)).all()
        print(f"-> Tiny splits test completed. Quantity={item.quantity}, Created Spools={len(spools)}")
        for s in spools:
            print(f"   Spool ID={s.id}, Owner={s.owner_id}")
            # User B should own the spool because User A's split is tiny and rounds to 0. Let's see.
            # 1 * (1.0 - 1e-15) + 1e-9 = 1.000000001 -> int is 1. So User B gets it.
            # 1 * 1e-15 + 1e-9 = 1.000001e-9 -> int is 0. User A gets 0.

def test_split_billing_no_splits(engine):
    print("Running stress test: split billing with 0 splits (no links)...")
    with Session(engine) as session:
        user_a = User(username="user_a3", hashed_password="xxx")
        session.add(user_a)
        session.flush()

        order = Order(store_name="Bambu Lab Store", creator_id=user_a.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Quantity 2. No splits.
        item = OrderItem(
            product_name="Bambu PLA Basic Gray",
            quantity=2,
            price_per_unit=25.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-GRY",
            variant_title="Gray"
        )
        session.add(item)
        session.flush()
        # Do not add any OrderItemSplit
        session.commit()

        db_order = session.get(Order, order.id)
        delivered = crud_order.deliver_order(session, order=db_order)
        spools = session.exec(select(FilamentSpool).where(FilamentSpool.order_item_id == item.id)).all()
        print(f"-> No splits test completed. Quantity={item.quantity}, Created Spools={len(spools)}")
        for s in spools:
            print(f"   Spool ID={s.id}, Owner={s.owner_id}")

def test_split_billing_large_quantity(engine):
    print("Running stress test: split billing with large quantity...")
    with Session(engine) as session:
        user_a = User(username="user_a4", hashed_password="xxx")
        user_b = User(username="user_b4", hashed_password="xxx")
        session.add(user_a)
        session.add(user_b)
        session.flush()

        order = Order(store_name="Bambu Lab Store", creator_id=user_a.id, status=OrderStatus.ORDERED)
        session.add(order)
        session.flush()

        # Quantity 10,000. Splits: A: 0.6, B: 0.4
        item = OrderItem(
            product_name="Bambu PLA Large Qty",
            quantity=10000,
            price_per_unit=15.00,
            order_id=order.id,
            product_slug="pla-basic",
            sku="SKU-PLA-QTY",
            variant_title="Large"
        )
        session.add(item)
        session.flush()

        split_a = OrderItemSplit(order_item_id=item.id, user_id=user_a.id, ownership_percentage=0.6)
        split_b = OrderItemSplit(order_item_id=item.id, user_id=user_b.id, ownership_percentage=0.4)
        session.add(split_a)
        session.add(split_b)
        session.commit()

        db_order = session.get(Order, order.id)
        delivered = crud_order.deliver_order(session, order=db_order)
        spools = session.exec(select(FilamentSpool).where(FilamentSpool.order_item_id == item.id)).all()
        print(f"-> Large quantity test completed. Quantity={item.quantity}, Created Spools={len(spools)}")
        owners = [s.owner_id for s in spools]
        print(f"   A owned spools: {owners.count(user_a.id)}")
        print(f"   B owned spools: {owners.count(user_b.id)}")
        print(f"   Communal spools: {owners.count(None)}")

def test_makerworld_proxy_stress():
    print("Running stress test: MakerWorld API proxy error handling & malformed data...")
    test_app = FastAPI()
    test_app.include_router(api_router, prefix="/api/v1")
    client = TestClient(test_app)

    # Scenario 1: API returns malformed JSON (Syntax Error)
    print("Scenario 1: API returns malformed JSON")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 200
        mock_response_api.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)

        mock_response_scrape = MagicMock()
        mock_response_scrape.status_code = 500  # Scraper fails too

        mock_get.side_effect = [mock_response_api, mock_response_scrape]

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        assert response.json() == []

    # Scenario 2: API returns empty dictionary
    print("Scenario 2: API returns empty dict")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 200
        mock_response_api.json.return_value = {}

        mock_response_scrape = MagicMock()
        mock_response_scrape.status_code = 500

        mock_get.side_effect = [mock_response_api, mock_response_scrape]

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        assert response.json() == []

    # Scenario 3: API returns valid structure but design has missing fields
    print("Scenario 3: API returns data with missing ID or title")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 200
        mock_response_api.json.return_value = {
            "data": {
                "list": [
                    {"title": "Missing ID"}, # missing id
                    {"id": 1234},            # missing title
                    {"id": 5678, "title": "Good Model", "cover": "https://img.com"} # good
                ]
            }
        }

        mock_get.return_value = mock_response_api

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 2
        assert results[0]["design_id"] == "1234"
        assert results[0]["title"] == "Untitled"
        assert results[1]["design_id"] == "5678"
        assert results[1]["title"] == "Good Model"

    # Scenario 4: Scraper returns HTML with malformed __NEXT_DATA__
    print("Scenario 4: Scraper returns HTML with malformed __NEXT_DATA__")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 500

        mock_response_scrape = MagicMock()
        mock_response_scrape.status_code = 200
        mock_response_scrape.text = '<html><body><script id="__NEXT_DATA__" type="application/json">{"invalid":json}</script></body></html>'

        mock_get.side_effect = [mock_response_api, mock_response_scrape]

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        assert response.json() == []

    # Scenario 5: Scraper returns HTML without __NEXT_DATA__
    print("Scenario 5: Scraper returns HTML without __NEXT_DATA__")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 500

        mock_response_scrape = MagicMock()
        mock_response_scrape.status_code = 200
        mock_response_scrape.text = '<html><body><h1>No next data here</h1></body></html>'

        mock_get.side_effect = [mock_response_api, mock_response_scrape]

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        assert response.json() == []

    # Scenario 6: Network times out
    print("Scenario 6: Network times out")
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        response = client.get("/api/v1/makerworld/search?q=test")
        assert response.status_code == 200
        assert response.json() == []

    # Scenario 7: SQL Injection query or extremely long query
    print("Scenario 7: Malicious or extremely long query")
    with patch("httpx.get") as mock_get:
        mock_response_api = MagicMock()
        mock_response_api.status_code = 200
        mock_response_api.json.return_value = {"data": {"list": []}}
        mock_get.return_value = mock_response_api

        long_query = "a" * 10000
        response = client.get(f"/api/v1/makerworld/search?q={long_query}")
        assert response.status_code == 200

    print("MakerWorld API proxy stress tests: COMPLETED")

if __name__ == "__main__":
    db_engine = setup_db()
    test_split_billing_negative_splits(db_engine)
    test_split_billing_extremely_tiny_splits(db_engine)
    test_split_billing_no_splits(db_engine)
    test_split_billing_large_quantity(db_engine)
    test_makerworld_proxy_stress()
    print("All stress tests completed.")
