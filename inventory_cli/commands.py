import requests

BASE_URL = "http://127.0.0.1:5000"


def list_inventory():
    """View all inventory items."""
    try:
        resp = requests.get(f"{BASE_URL}/inventory")
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code != 200:
        print("Error fetching inventory:", resp.status_code, resp.text)
        return

    items = resp.json()
    if not items:
        print("Inventory is empty.")
        return

    print("\n--- Inventory ---")
    for item in items:
        print(
            f"ID {item['id']}: {item['name']} "
            f"(brand: {item.get('brand') or 'N/A'}, "
            f"qty: {item['quantity']}, "
            f"barcode: {item.get('barcode') or 'N/A'})"
        )


def view_item_details():
    """View a single item's full details."""
    item_id_str = input("Enter item ID: ").strip()
    try:
        item_id = int(item_id_str)
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    try:
        resp = requests.get(f"{BASE_URL}/inventory/{item_id}")
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code == 404:
        print("Item not found.")
        return

    if resp.status_code != 200:
        print("Error fetching item:", resp.status_code, resp.text)
        return

    item = resp.json()
    print("\n--- Item Details ---")
    print(f"ID: {item['id']}")
    print(f"Name: {item['name']}")
    print(f"Brand: {item.get('brand')}")
    print(f"Ingredients: {item.get('ingredients')}")
    print(f"Barcode: {item.get('barcode')}")
    print(f"Quantity (stock level): {item['quantity']}")


def add_item_from_barcode():
    """Add a new inventory item using OpenFoodFacts and a barcode."""
    barcode = input("Enter product barcode: ").strip()
    if not barcode:
        print("Barcode is required.")
        return

    quantity_str = input("Enter quantity (stock): ").strip() or "1"
    try:
        quantity = int(quantity_str)
    except ValueError:
        print("Invalid quantity, defaulting to 1.")
        quantity = 1

    payload = {"barcode": barcode, "quantity": quantity}

    try:
        resp = requests.post(f"{BASE_URL}/inventory", json=payload)
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code == 201:
        item = resp.json()
        print(f"\nItem created: ID #{item['id']} - {item['name']}")
        print(f"Quantity: {item['quantity']}, Barcode: {item.get('barcode')}")
    else:
        print("Error creating item:", resp.status_code, resp.text)


def add_item_manual():
    """Add a new inventory item manually (without OpenFoodFacts)."""
    name = input("Enter product name: ").strip()
    if not name:
        print("Name is required.")
        return

    brand = input("Enter brand (optional): ").strip() or None
    ingredients = input("Enter ingredients (optional): ").strip() or None
    barcode = input("Enter barcode (optional): ").strip() or None

    quantity_str = input("Enter quantity (stock): ").strip() or "1"
    try:
        quantity = int(quantity_str)
    except ValueError:
        print("Invalid quantity, defaulting to 1.")
        quantity = 1

    payload = {
        "name": name,
        "brand": brand,
        "ingredients": ingredients,
        "barcode": barcode,
        "quantity": quantity,
    }

    try:
        resp = requests.post(f"{BASE_URL}/inventory", json=payload)
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code == 201:
        item = resp.json()
        print(f"\nItem created: ID #{item['id']} - {item['name']}")
        print(f"Quantity: {item['quantity']}, Barcode: {item.get('barcode')}")
    else:
        print("Error creating item:", resp.status_code, resp.text)


def update_item_stock():
    """Update an item's stock level (quantity)."""
    item_id_str = input("Enter item ID to update: ").strip()
    try:
        item_id = int(item_id_str)
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    quantity_str = input("Enter new quantity (stock): ").strip()
    try:
        quantity = int(quantity_str)
    except ValueError:
        print("Invalid quantity.")
        return

    payload = {"quantity": quantity}

    try:
        resp = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code == 200:
        print("Updated item:")
        print(resp.json())
    elif resp.status_code == 404:
        print("Item not found.")
    else:
        print("Error updating item:", resp.status_code, resp.text)


def delete_item():
    """Delete an item from inventory."""
    item_id_str = input("Enter item ID to delete: ").strip()
    try:
        item_id = int(item_id_str)
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return

    try:
        resp = requests.delete(f"{BASE_URL}/inventory/{item_id}")
    except requests.RequestException as e:
        print("Error contacting API:", e)
        return

    if resp.status_code == 204:
        print("Item deleted.")
    elif resp.status_code == 404:
        print("Item not found.")
    else:
        print("Error deleting item:", resp.status_code, resp.text)


def find_item_on_api():
    """
    Find an item using the external API via your Flask routes.
    Does NOT save the item; just shows info.
    """
    print("\nSearch on OpenFoodFacts via API:")
    print("1. By barcode")
    print("2. By product name")
    choice = input("Choose search type: ").strip()

    if choice == "1":
        barcode = input("Enter barcode: ").strip()
        if not barcode:
            print("Barcode is required.")
            return

        try:
            resp = requests.get(f"{BASE_URL}/inventory/lookup/{barcode}")
        except requests.RequestException as e:
            print("Error contacting API:", e)
            return

    elif choice == "2":
        name = input("Enter product name: ").strip()
        if not name:
            print("Name is required.")
            return

        try:
            resp = requests.get(
                f"{BASE_URL}/inventory/search", params={"name": name}
            )
        except requests.RequestException as e:
            print("Error contacting API:", e)
            return
    else:
        print("Invalid choice.")
        return

    if resp.status_code == 200:
        data = resp.json()
        print("\n--- Product from OpenFoodFacts ---")
        print(f"Name: {data['name']}")
        print(f"Brand: {data.get('brand')}")
        print(f"Ingredients: {data.get('ingredients')}")
        print(f"Barcode: {data.get('barcode')}")
    elif resp.status_code == 404:
        print("Product not found.")
    else:
        print("Error searching product:", resp.status_code, resp.text)