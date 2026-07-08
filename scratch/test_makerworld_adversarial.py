# scratch/test_makerworld_adversarial.py
import sys
import os
from unittest.mock import patch, MagicMock
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Include backend directory in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.api.v1.api import api_router

def test_makerworld_endpoint():
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    client = TestClient(app)

    print("\n--- Test 1: MakerWorld Malformed JSON in Method 1 ---")
    with patch("httpx.get") as mock_get:
        # Method 1 returns malformed JSON
        mock_resp_1 = MagicMock()
        mock_resp_1.status_code = 200
        mock_resp_1.json.side_effect = ValueError("Malformed JSON")

        # Method 2 returns empty list / fail
        mock_resp_2 = MagicMock()
        mock_resp_2.status_code = 500

        mock_get.side_effect = [mock_resp_1, mock_resp_2]

        response = client.get("/api/v1/makerworld/search?q=test")
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.json()}")
        assert response.status_code == 200
        assert response.json() == []

    print("\n--- Test 2: MakerWorld Slow Network (Timeout) ---")
    with patch("httpx.get") as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Timeout")

        response = client.get("/api/v1/makerworld/search?q=test")
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.json()}")
        assert response.status_code == 200
        assert response.json() == []

    print("\n--- Test 3: MakerWorld Unexpected Nested Data Formats ---")
    with patch("httpx.get") as mock_get:
        # Method 1: returns custom nested dictionaries instead of expected lists
        custom_data = {
            "some_weird_wrapper": {
                "sub_wrapper": [
                    {"id": 9999, "name": "Deep Model", "cover": "http://img.png", "url": "/deep"}
                ]
            }
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = custom_data

        mock_get.return_value = mock_resp

        response = client.get("/api/v1/makerworld/search?q=test")
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["design_id"] == "9999"
        assert data[0]["title"] == "Deep Model"

    print("\n--- Test 4: MakerWorld Non-dict items in list ---")
    with patch("httpx.get") as mock_get:
        # Method 1: list contains invalid non-dict items
        custom_data = {
            "data": {
                "list": [
                    "invalid string item",
                    {"id": 8888, "title": "Valid Model", "cover": "http://img.png"}
                ]
            }
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = custom_data

        # Second mock response (in case it tries method 2)
        mock_resp_2 = MagicMock()
        mock_resp_2.status_code = 500
        mock_get.side_effect = [mock_resp, mock_resp_2]

        response = client.get("/api/v1/makerworld/search?q=test")
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.json()}")
        # Check if it handled the non-dict item without crashing
        assert response.status_code == 200

    print("\n--- Test 5: MakerWorld circular reference simulation ---")
    # Actually, JSON parsed by json.loads cannot have circular references,
    # but let's test find_designs_in_dict directly with a Python dict that has a cycle.
    # Note: If it loops infinitely, it will crash with RecursionError.
    from app.api.v1.endpoints.makerworld import find_designs_in_dict

    cycle_dict = {}
    cycle_dict["self_ref"] = cycle_dict

    try:
        res = find_designs_in_dict(cycle_dict)
        print(f"Circular reference check finished. Returned: {res}")
    except RecursionError:
        print("CRITICAL BUG: Circular reference causes RecursionError!")

    print("\n--- Test 6: MakerWorld Deep Nesting simulation ---")
    # Nesting depth: 1500 (python max recursion depth is typically 1000)
    deep_dict = {}
    curr = deep_dict
    for i in range(1500):
        curr["child"] = {}
        curr = curr["child"]
    curr["id"] = 123
    curr["title"] = "Deep Model"

    try:
        res = find_designs_in_dict(deep_dict)
        print(f"Deep nesting check finished. Returned: {res}")
    except RecursionError:
        print("CRITICAL BUG: Deep nesting causes RecursionError!")


if __name__ == "__main__":
    test_makerworld_endpoint()
