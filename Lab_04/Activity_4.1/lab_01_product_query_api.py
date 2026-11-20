"""Lab 4.1: Build a Product Query API
Objective: Implement a set of CRUD operations for a product inventory system using all query operator categories.

Features:
1. Schema validation ($jsonSchema) requiring name, price (>0), stock (>=0), and tags (array of strings).
2. Comparison operators: $gte/$lte for price between 20 and 50, $eq for out of stock.
3. Logical operators: $or for out of stock OR price > 100; $and for in-stock AND tagged 'premium'.
4. Array operators: $all for BOTH 'electronics' and 'wireless', $size for exactly 2 tags.
5. Pagination function returning sliced, sorted products with metadata.
6. Export database collection to products_inventory.json.
"""

import os
import sys
import json
from datetime import datetime
from pymongo.errors import OperationFailure, WriteError

# Ensure parent directory is in path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from config.connection import get_db, banner, export_collection_to_json
from rich.console import Console
from rich.table import Table

console = Console()

# Comprehensive Product Dataset (12 products with varying attributes)
SAMPLE_PRODUCTS = [
    {
        "sku": "PROD-001",
        "name": "Wireless Ergonomic Keyboard",
        "category": "Peripherals",
        "price": 49.99,
        "stock": 25,
        "tags": ["electronics", "wireless", "ergonomic", "office"],
        "brand": "LogiTech",
        "is_active": True
    },
    {
        "sku": "PROD-002",
        "name": "Ultra HD 4K Gaming Monitor",
        "category": "Displays",
        "price": 349.99,
        "stock": 15,
        "tags": ["electronics", "premium", "gaming"],
        "brand": "ViewSonic",
        "is_active": True
    },
    {
        "sku": "PROD-003",
        "name": "Noise Cancelling Wireless Headphones",
        "category": "Audio",
        "price": 199.99,
        "stock": 0,
        "tags": ["electronics", "wireless", "premium"],
        "brand": "Sony",
        "is_active": False
    },
    {
        "sku": "PROD-004",
        "name": "USB-C Fast Charging Cable",
        "category": "Accessories",
        "price": 15.99,
        "stock": 120,
        "tags": ["electronics", "accessories"],
        "brand": "Anker",
        "is_active": True
    },
    {
        "sku": "PROD-005",
        "name": "Wireless Optical Mouse",
        "category": "Peripherals",
        "price": 29.99,
        "stock": 60,
        "tags": ["electronics", "wireless"],
        "brand": "LogiTech",
        "is_active": True
    },
    {
        "sku": "PROD-006",
        "name": "Mechanical RGB Gaming Keyboard",
        "category": "Peripherals",
        "price": 129.99,
        "stock": 18,
        "tags": ["electronics", "gaming", "premium"],
        "brand": "Corsair",
        "is_active": True
    },
    {
        "sku": "PROD-007",
        "name": "Executive Leather Office Chair",
        "category": "Furniture",
        "price": 249.99,
        "stock": 0,
        "tags": ["furniture", "office"],
        "brand": "HermanMiller",
        "is_active": False
    },
    {
        "sku": "PROD-008",
        "name": "Adjustable Aluminum Laptop Stand",
        "category": "Accessories",
        "price": 39.99,
        "stock": 45,
        "tags": ["accessories", "ergonomic"],
        "brand": "RainDesign",
        "is_active": True
    },
    {
        "sku": "PROD-009",
        "name": "Smart LED Desk Lamp",
        "category": "Lighting",
        "price": 45.00,
        "stock": 0,
        "tags": ["lighting", "smart-home"],
        "brand": "Philips",
        "is_active": False
    },
    {
        "sku": "PROD-010",
        "name": "Portable Bluetooth Wireless Speaker",
        "category": "Audio",
        "price": 79.99,
        "stock": 35,
        "tags": ["electronics", "wireless", "audio"],
        "brand": "JBL",
        "is_active": True
    },
    {
        "sku": "PROD-011",
        "name": "Premium Full-Grain Leather Desk Mat",
        "category": "Office",
        "price": 34.50,
        "stock": 50,
        "tags": ["office", "premium"],
        "brand": "Grovemade",
        "is_active": True
    },
    {
        "sku": "PROD-012",
        "name": "Full HD 1080p Streaming WebCam",
        "category": "Peripherals",
        "price": 49.00,
        "stock": 0,
        "tags": ["electronics", "video"],
        "brand": "LogiTech",
        "is_active": False
    }
]

# JSON Schema Validation Rule for the products collection
PRODUCTS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "price", "stock", "tags"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "Product name - must be a non-empty string"
            },
            "price": {
                "bsonType": ["double", "int", "decimal"],
                "minimum": 0.01,
                "description": "Price must be a positive number greater than zero"
            },
            "stock": {
                "bsonType": "int",
                "minimum": 0,
                "description": "Stock quantity must be a non-negative integer (>= 0)"
            },
            "tags": {
                "bsonType": "array",
                "description": "Tags must be an array of strings",
                "items": {
                    "bsonType": "string",
                    "description": "Each tag item must be a string"
                }
            },
            "sku": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "brand": {"bsonType": "string"},
            "is_active": {"bsonType": "bool"}
        }
    }
}


def create_validated_collection(db, col_name="products"):
    """Create collection with $jsonSchema validation, dropping old collection if present."""
    if col_name in db.list_collection_names():
        db.drop_collection(col_name)
    col = db.create_collection(
        col_name,
        validator=PRODUCTS_VALIDATOR,
        validationLevel="strict",
        validationAction="error"
    )
    print(f"[OK] Created collection '{col_name}' with strict $jsonSchema validation rules.")
    return col


def test_schema_validation(col):
    """Test schema validation by inserting a valid doc and testing invalid rejects."""
    print("\n--- Testing Schema Validation Rules ---")
    # 1. Valid test insert
    valid_doc = {
        "sku": "TEST-001",
        "name": "Test Valid Product",
        "price": 19.99,
        "stock": 10,
        "tags": ["testing", "verified"],
        "category": "Test"
    }
    col.insert_one(valid_doc)
    print("  [PASS] Valid document successfully inserted.")
    col.delete_one({"sku": "TEST-001"})

    # 2. Test Invalid: Negative price
    try:
        col.insert_one({
            "name": "Invalid Price Product",
            "price": -10.50,
            "stock": 5,
            "tags": ["invalid"]
        })
        print("  [FAIL] Validation did not catch negative price!")
    except (OperationFailure, WriteError) as e:
        print("  [PASS] Negative price rejected by $jsonSchema validation.")

    # 3. Test Invalid: Negative stock
    try:
        col.insert_one({
            "name": "Invalid Stock Product",
            "price": 25.00,
            "stock": -1,
            "tags": ["invalid"]
        })
        print("  [FAIL] Validation did not catch negative stock!")
    except (OperationFailure, WriteError) as e:
        print("  [PASS] Negative stock rejected by $jsonSchema validation.")

    # 4. Test Invalid: Missing required tags
    try:
        col.insert_one({
            "name": "Missing Tags Product",
            "price": 25.00,
            "stock": 10
        })
        print("  [FAIL] Validation did not catch missing required field!")
    except (OperationFailure, WriteError) as e:
        print("  [PASS] Missing required 'tags' rejected by $jsonSchema validation.\n")


def paginate_products(col, page=1, items_per_page=4, sort_field="name", sort_order=1):
    """Pagination function: returns sliced products sorted by name along with pagination metadata."""
    if page < 1:
        page = 1
    skip_count = (page - 1) * items_per_page
    total_items = col.count_documents({})
    total_pages = (total_items + items_per_page - 1) // items_per_page

    cursor = col.find({}, {"_id": 0, "sku": 1, "name": 1, "price": 1, "stock": 1, "tags": 1})
    cursor = cursor.sort(sort_field, sort_order).skip(skip_count).limit(items_per_page)
    items = list(cursor)

    return {
        "page": page,
        "items_per_page": items_per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "items": items
    }


def display_results_table(title, items, fields=None):
    """Render a clean rich table for query results."""
    table = Table(title=title, title_style="bold cyan", border_style="blue")
    table.add_column("SKU", style="yellow", justify="center")
    table.add_column("Product Name", style="white")
    table.add_column("Price ($)", style="green", justify="right")
    table.add_column("Stock", style="magenta", justify="center")
    table.add_column("Tags", style="cyan")

    for item in items:
        price_str = f"${item.get('price', 0):.2f}"
        stock_str = str(item.get("stock", 0))
        tags_str = ", ".join(item.get("tags", []))
        table.add_row(
            item.get("sku", "N/A"),
            item.get("name", "N/A"),
            price_str,
            stock_str,
            tags_str
        )
    console.print(table)
    console.print()


def main():
    banner("Lab 4.1: Build a Product Query API")
    db = get_db("nosql_labs")

    # Step 1: Create collection with schema validation & seed products
    col = create_validated_collection(db, "products")
    test_schema_validation(col)

    insert_result = col.insert_many(SAMPLE_PRODUCTS)
    print(f"[OK] Successfully inserted {len(insert_result.inserted_ids)} product documents into 'products' collection.\n")

    # Step 2: Comparison Operators
    print("=" * 70)
    print("STEP 2: COMPARISON OPERATORS QUERIES")
    print("=" * 70)

    # 2a: Products with price between 20 and 50 ($gte and $lte)
    query_price_20_50 = {"price": {"$gte": 20.0, "$lte": 50.0}}
    res_price_20_50 = list(col.find(query_price_20_50, {"_id": 0}))
    display_results_table(
        f"Comparison Query 1: Price Between $20 and $50 (Found {len(res_price_20_50)})",
        res_price_20_50
    )

    # 2b: Products with stock equal to 0 (out of stock) ($eq)
    query_out_of_stock = {"stock": {"$eq": 0}}
    res_out_of_stock = list(col.find(query_out_of_stock, {"_id": 0}))
    display_results_table(
        f"Comparison Query 2: Out of Stock ($eq: 0) (Found {len(res_out_of_stock)})",
        res_out_of_stock
    )

    # Step 3: Logical Operators
    print("=" * 70)
    print("STEP 3: LOGICAL OPERATORS QUERIES")
    print("=" * 70)

    # 3a: Out of stock OR priced above 100 ($or)
    query_or = {
        "$or": [
            {"stock": {"$eq": 0}},
            {"price": {"$gt": 100.0}}
        ]
    }
    res_or = list(col.find(query_or, {"_id": 0}))
    display_results_table(
        f"Logical Query 1: Out of Stock OR Price > $100 ($or) (Found {len(res_or)})",
        res_or
    )

    # 3b: In stock AND tagged as 'premium' ($and)
    query_and = {
        "$and": [
            {"stock": {"$gt": 0}},
            {"tags": "premium"}
        ]
    }
    res_and = list(col.find(query_and, {"_id": 0}))
    display_results_table(
        f"Logical Query 2: In Stock AND Tagged 'premium' ($and) (Found {len(res_and)})",
        res_and
    )

    # Step 4: Array Operators
    print("=" * 70)
    print("STEP 4: ARRAY OPERATORS QUERIES")
    print("=" * 70)

    # 4a: Products with BOTH 'electronics' AND 'wireless' in tags ($all)
    query_all_tags = {"tags": {"$all": ["electronics", "wireless"]}}
    res_all_tags = list(col.find(query_all_tags, {"_id": 0}))
    display_results_table(
        f"Array Query 1: Tags Contain BOTH 'electronics' AND 'wireless' ($all) (Found {len(res_all_tags)})",
        res_all_tags
    )

    # 4b: Products with exactly 2 tags ($size)
    query_size_2 = {"tags": {"$size": 2}}
    res_size_2 = list(col.find(query_size_2, {"_id": 0}))
    display_results_table(
        f"Array Query 2: Exactly 2 Tags ($size: 2) (Found {len(res_size_2)})",
        res_size_2
    )

    # Step 5: Pagination Implementation
    print("=" * 70)
    print("STEP 5: PAGINATION IMPLEMENTATION (Sorted by Name)")
    print("=" * 70)
    items_per_page = 4
    total_count = col.count_documents({})
    total_pages = (total_count + items_per_page - 1) // items_per_page
    print(f"Total Products: {total_count} | Items per Page: {items_per_page} | Total Pages: {total_pages}\n")

    for p in range(1, total_pages + 1):
        page_data = paginate_products(col, page=p, items_per_page=items_per_page, sort_field="name", sort_order=1)
        display_results_table(
            f"Page {page_data['page']} of {page_data['total_pages']} (Showing {len(page_data['items'])} items)",
            page_data["items"]
        )

    # Step 6: Export to JSON file
    json_path = os.path.join(BASE_DIR, "products_inventory.json")
    export_collection_to_json("nosql_labs", "products", json_path)

    banner("Lab 4.1 Execution Complete")


if __name__ == "__main__":
    main()
