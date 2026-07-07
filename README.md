# REST-API-with-Flask--Inventory-Management-System-CH0M3.-

You have been hired by a small retail company to develop an inventory management system. This system will allow employees to add, edit, view, and delete inventory items. Additionally, the system will fetch real-time product data from an external API (e.g., OpenFoodFacts API)(https://openfoodfacts.github.io/openfoodfacts-server/api/) to supplement product details.

You are tasked with creating an administrator portal for an e-commerce website which will include.

A Flask-based REST API with CRUD operations for managing inventory.
An external API integration to fetch product details by barcode or name.
A CLI-based interface to interact with the API.
Unit tests to validate functionality and interactions.




Routes

Get items from https://openfoodfacts.github.io/openfoodfacts-server/api/
Get item by barcode. 
Get item by name.
Put an item 
Patch an item
Delete an item . 


nstallation & Setup
1. Clone the repo
git clone https://github.com/ch0m3/REST-API-with-Flask--Inventory-Management-System-CH0M3.-.git
cd Python-REST-API-with-Flask--Inventory-Management-System-CH0M3.-

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python app.py

http://127.0.0.1:5000

python cli.py

API Endpoints
Base URL
http://127.0.0.1:5000

CRUD Routes
Method	Route	Description
GET	/inventory	Get all items
GET	/inventory/<id>	Get item by ID
POST	/inventory	Create item (manual or via barcode)
PATCH	/inventory/<id>	Update an item
DELETE	/inventory/<id>	Delete an item
External API (OpenFoodFacts)
Method	Route	Description
GET	/inventory/lookup/<barcode>	Fetch product by barcode
GET	/inventory/search?name=milk	Search product by name

External API: OpenFoodFacts

This project integrates with the public OpenFoodFacts database:

Fetch product by barcode

Search products by name


CLI Commands (User Flow)

When you run:

python cli.py


You will see:

=== Inventory Management CLI ===
1. View all inventory
2. View item details
3. Add item from barcode
4. Add item manually
5. Update stock quantity
6. Delete item
7. Find item on OpenFoodFacts (no save)
8. Quit

Running Tests
pytest


✔ Tests run in isolated environment
✔ Mocked network calls
✔ Coverage includes CRUD logic + external API integration

Example JSON Request
Create item manually:
POST /inventory
{
  "name": "House Blend Coffee",
  "brand": "Starbucks",
  "quantity": 5
}

Create item using barcode:
POST /inventory
{
  "barcode": "737628064502",
  "quantity": 1
}

Author

MiuTonny
