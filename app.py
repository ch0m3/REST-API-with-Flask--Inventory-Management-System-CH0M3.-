from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---- MOCK DATABASE (in-memory array) ----
items = []
next_id = 1  # auto-increment id

OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"


def make_item(name, brand=None, ingredients=None, quantity=0, barcode=None):
    global next_id
    item = {
        "id": next_id,
        "name": name,
        "brand": brand,
        "ingredients": ingredients,
        "barcode": barcode,
        "quantity": quantity,
    }
    next_id += 1
    return item


def fetch_openfoodfacts(barcode):
    """
    Call OpenFoodFacts API and return basic product info
    that resembles their structure but only with fields we care about.
    """
    url = OPENFOODFACTS_URL.format(barcode=barcode)
    resp = requests.get(url)

    if resp.status_code != 200:
        return None

    data = resp.json()
    if data.get("status") != 1:
        # product not found
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name", "Unknown product"),
        "brand": product.get("brands", "Unknown brand"),
        "ingredients": product.get("ingredients_text", ""),
        "barcode": barcode,
    }

def fetch_openfoodfacts_by_name(name):
    """
    Search OpenFoodFacts by product name.
    We take the first matching product from the search results.
    """
    search_url = "https://world.openfoodfacts.org/api/v2/search"
    params = {
        "search_terms": name,
        "page_size": 1,  # just grab the first result
    }
    resp = requests.get(search_url, params=params)

    if resp.status_code != 200:
        return None

    data = resp.json()
    products = data.get("products", [])
    if not products:
        return None

    product = products[0]

    return {
        "name": product.get("product_name", "Unknown product"),
        "brand": product.get("brands", "Unknown brand"),
        "ingredients": product.get("ingredients_text", ""),
        "barcode": product.get("code"),  # product code in OFF
    }


# ---------- CRUD ROUTES (RESTful /inventory) ----------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Inventory API is running",
        "endpoints": [
            "GET /inventory",
            "POST /inventory",
            "PATCH /inventory/<id>",
            "DELETE /inventory/<id>",
            "GET /inventory/lookup/<barcode>",
            "GET /inventory/search?name=..."
        ]
    }), 200


# READ ALL: GET /inventory
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(items), 200


# READ ONE: GET /inventory/<id>
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404


# CREATE: POST /inventory
# Option A: client sends { "name": "...", "quantity": 5, "barcode": "..." }
# Option B: client sends { "barcode": "..." } only, and we fetch details from OpenFoodFacts
@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json() or {}

    name = data.get("name")
    brand = data.get("brand")
    ingredients = data.get("ingredients")
    barcode = data.get("barcode")
    quantity = data.get("quantity", 0)

    # If no name, but barcode present -> try to fetch product info
    if not name and barcode:
        product_info = fetch_openfoodfacts(barcode)
        if not product_info:
            # product not found in OpenFoodFacts
            return jsonify(
                {"error": "Could not find product for given barcode"}
            ), 400

        # Only reach here if product_info is valid
        name = product_info["name"]
        brand = product_info["brand"]
        ingredients = product_info["ingredients"]

    if not name:
        return jsonify({"error": "Field 'name' or 'barcode' is required"}), 400

    new_item = make_item(
        name=name,
        brand=brand,
        ingredients=ingredients,
        quantity=quantity,
        barcode=barcode,
    )
    items.append(new_item)

    return jsonify(new_item), 201


# UPDATE: PATCH /inventory/<id>
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    data = request.get_json() or {}

    for item in items:
        if item["id"] == item_id:
            if "name" in data:
                item["name"] = data["name"]
            if "brand" in data:
                item["brand"] = data["brand"]
            if "ingredients" in data:
                item["ingredients"] = data["ingredients"]
            if "quantity" in data:
                item["quantity"] = data["quantity"]
            if "barcode" in data:
                item["barcode"] = data["barcode"]
            return jsonify(item), 200

    return jsonify({"error": "Item not found"}), 404


# DELETE: DELETE /inventory/<id>
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            items.pop(index)
            return "", 204

    return jsonify({"error": "Item not found"}), 404


# EXTRA: Lookup product by barcode WITHOUT saving to inventory
# (Not required in the list but nice for the “external API” part)
@app.route("/inventory/lookup/<barcode>", methods=["GET"])
def lookup_inventory_product(barcode):
    product_info = fetch_openfoodfacts(barcode)
    if not product_info:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_info), 200

@app.route("/inventory/search", methods=["GET"])
def search_inventory_product():
    """
    Search OpenFoodFacts by product name (no save).
    Example: GET /inventory/search?name=almond%20milk
    """
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Query parameter 'name' is required"}), 400

    product_info = fetch_openfoodfacts_by_name(name)
    if not product_info:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(product_info), 200


if __name__ == "__main__":
    app.run(debug=True)