import os
import sys
import json
from unittest.mock import patch, MagicMock

# --- Make sure Python can find app.py in the project root ---
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import app  # import the whole module so we can reset its globals


def setup_function():
    """
    Runs before each test function.
    Clear and reset the mock database so tests don't interfere.
    """
    app.items.clear()
    app.next_id = 1


# ---------- BASIC CRUD TESTS (no external API) ----------

def test_get_inventory_empty():
    client = app.app.test_client()

    resp = client.get("/inventory")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data == []


def test_create_inventory_item_with_name_only():
    client = app.app.test_client()

    payload = {"name": "Test Product", "quantity": 3}
    resp = client.post(
        "/inventory",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 201
    data = resp.get_json()

    assert data["id"] == 1
    assert data["name"] == "Test Product"
    assert data["quantity"] == 3
    assert data["brand"] is None
    assert data["ingredients"] is None


def test_create_inventory_item_missing_name_and_barcode():
    client = app.app.test_client()

    # no name, no barcode -> should fail
    payload = {"quantity": 1}
    resp = client.post(
        "/inventory",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_update_inventory_quantity():
    client = app.app.test_client()

    # First create an item
    create_resp = client.post(
        "/inventory",
        data=json.dumps({"name": "Milk", "quantity": 2}),
        content_type="application/json",
    )
    assert create_resp.status_code == 201
    item = create_resp.get_json()
    item_id = item["id"]

    # Now update quantity
    update_resp = client.patch(
        f"/inventory/{item_id}",
        data=json.dumps({"quantity": 10}),
        content_type="application/json",
    )
    assert update_resp.status_code == 200
    updated = update_resp.get_json()
    assert updated["quantity"] == 10


def test_delete_inventory_item():
    client = app.app.test_client()

    # Create an item
    create_resp = client.post(
        "/inventory",
        data=json.dumps({"name": "Yogurt", "quantity": 5}),
        content_type="application/json",
    )
    assert create_resp.status_code == 201
    item_id = create_resp.get_json()["id"]

    # Delete it
    delete_resp = client.delete(f"/inventory/{item_id}")
    assert delete_resp.status_code == 204

    # Confirm it is gone
    get_resp = client.get(f"/inventory/{item_id}")
    assert get_resp.status_code == 404


# ---------- EXTERNAL API INTERACTION (mocked) ----------

@patch("app.requests.get")
def test_create_inventory_item_with_barcode_uses_openfoodfacts(mock_get):
    """
    Test that POST /inventory with only a barcode calls OpenFoodFacts
    and stores the enhanced product data. We MOCK the external API.
    """
    client = app.app.test_client()

    # Configure mock response from requests.get
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
        },
    }
    mock_get.return_value = fake_response

    payload = {"barcode": "1234567890123", "quantity": 4}
    resp = client.post(
        "/inventory",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 201
    data = resp.get_json()

    # Check that external API was called
    mock_get.assert_called_once()
    assert data["name"] == "Organic Almond Milk"
    assert data["brand"] == "Silk"
    assert data["ingredients"].startswith("Filtered water")
    assert data["barcode"] == "1234567890123"
    assert data["quantity"] == 4