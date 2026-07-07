import os
import sys
from unittest.mock import patch, MagicMock

# --- Make sure Python can find inventory_cli in the project root ---
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from inventory_cli import commands  # import your commands module


@patch("inventory_cli.commands.requests.get")
def test_list_inventory_empty(mock_get, capsys):
    """
    CLI: list_inventory should handle empty inventory correctly.
    We mock the API to return an empty list.
    """
    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = []
    mock_get.return_value = fake_resp

    commands.list_inventory()

    captured = capsys.readouterr()
    assert "Inventory is empty." in captured.out


@patch("inventory_cli.commands.requests.post")
@patch("builtins.input", side_effect=["1234567890123", "3"])
def test_add_item_from_barcode_success(mock_input, mock_post, capsys):
    """
    CLI: add_item_from_barcode should POST to /inventory
    and print 'Item created:' when successful.
    """
    fake_resp = MagicMock()
    fake_resp.status_code = 201
    fake_resp.json.return_value = {
        "id": 1,
        "name": "Mock Product",
        "brand": "Mock Brand",
        "ingredients": "Mock ingredients",
        "barcode": "1234567890123",
        "quantity": 3,
    }
    mock_post.return_value = fake_resp

    commands.add_item_from_barcode()

    # Ensure POST was called with expected payload
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "/inventory" in args[0]
    assert kwargs["json"]["barcode"] == "1234567890123"
    assert kwargs["json"]["quantity"] == 3

    captured = capsys.readouterr()
    assert "Item created:" in captured.out


@patch("inventory_cli.commands.requests.delete")
@patch("builtins.input", side_effect=["5"])
def test_delete_item_not_found(mock_input, mock_delete, capsys):
    """
    CLI: delete_item should handle 404 from API.
    """
    fake_resp = MagicMock()
    fake_resp.status_code = 404
    fake_resp.text = "Not Found"
    mock_delete.return_value = fake_resp

    commands.delete_item()

    captured = capsys.readouterr()
    assert "Item not found." in captured.out