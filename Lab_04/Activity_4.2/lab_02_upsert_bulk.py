"""Lab 4.2: Implement Upsert and Bulk Operations
Objective: Use upserts and bulk writes to handle conditional inserts and batch modifications.

Features:
1. upsert_product_price function using update_one(..., upsert=True) with $set and $setOnInsert.
   Demonstrates updating an existing product and creating a new product with default values.
2. Bulk write operation executing 5 simultaneous updates:
   - Increase stock by 10 for products A, B, and C ($inc operator).
   - Set is_active to False for products D and E ($set operator).
   - Demonstrate upsert inside bulk write (Product F) to verify upserted_count and upserted_ids.
3. Verification of bulk write result object (matched_count, modified_count, upserted_count).
4. Display before/after inventory tables.
5. Export final state to inventory_upsert_bulk.json.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pymongo import UpdateOne

# Ensure parent directory is in path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from config.connection import get_db, banner, export_collection_to_json
from rich.console import Console
from rich.table import Table

console = Console()

# Initial inventory products for Lab 4.2
INITIAL_INVENTORY = [
    {"sku": "PROD-A", "name": "Mechanical Keyboard A", "price": 89.99, "stock": 15, "is_active": True, "category": "Keyboards"},
    {"sku": "PROD-B", "name": "Wireless Mouse B", "price": 49.99, "stock": 30, "is_active": True, "category": "Mice"},
    {"sku": "PROD-C", "name": "Gaming Headset C", "price": 119.99, "stock": 50, "is_active": True, "category": "Audio"},
    {"sku": "PROD-D", "name": "USB Hub D", "price": 24.99, "stock": 20, "is_active": True, "category": "Accessories"},
    {"sku": "PROD-E", "name": "Webcam HD E", "price": 59.99, "stock": 10, "is_active": True, "category": "Cameras"}
]


def display_inventory_table(title, docs):
    """Render a clean rich table showing current inventory state."""
    table = Table(title=title, title_style="bold blue", border_style="cyan")
    table.add_column("SKU", style="yellow", justify="center")
    table.add_column("Product Name", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Price ($)", style="green", justify="right")
    table.add_column("Stock", style="cyan", justify="center")
    table.add_column("Active?", style="bold", justify="center")

    for doc in docs:
        active_str = "[green]YES[/green]" if doc.get("is_active", True) else "[red]NO[/red]"
        table.add_row(
            doc.get("sku", "N/A"),
            doc.get("name", "N/A"),
            doc.get("category", "N/A"),
            f"${doc.get('price', 0):.2f}",
            str(doc.get("stock", 0)),
            active_str
        )
    console.print(table)
    console.print()


def upsert_product_price(col, sku, price, default_values=None):
    """Takes SKU and price. If SKU exists, update price. If not, insert with default values."""
    if default_values is None:
        default_values = {}

    defaults = {
        "sku": sku,
        "name": default_values.get("name", f"Auto-Created Product {sku}"),
        "category": default_values.get("category", "General"),
        "stock": default_values.get("stock", 0),
        "is_active": default_values.get("is_active", True),
        "tags": default_values.get("tags", ["new-arrival", "auto-created"]),
        "created_at": datetime.now(timezone.utc)
    }

    result = col.update_one(
        {"sku": sku},
        {
            "$set": {
                "price": float(price),
                "updated_at": datetime.now(timezone.utc)
            },
            "$setOnInsert": defaults
        },
        upsert=True
    )

    action = "UPDATED (Existing)" if result.matched_count > 0 else "INSERTED (New Upsert)"
    print(f"  [{action}] SKU: {sku} | Matched: {result.matched_count} | Modified: {result.modified_count} | Upserted ID: {result.upserted_id}")
    return result


def main():
    banner("Lab 4.2: Implement Upsert and Bulk Operations")
    db = get_db("nosql_labs")

    # Reset collection and insert initial inventory
    col_name = "inventory_ops"
    if col_name in db.list_collection_names():
        db.drop_collection(col_name)
    col = db[col_name]

    col.insert_many(INITIAL_INVENTORY)
    print(f"[OK] Seeded '{col_name}' collection with {len(INITIAL_INVENTORY)} products (A, B, C, D, E).\n")

    # Display Initial State
    initial_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    display_inventory_table("Initial Inventory State (Before Upsert & Bulk Operations)", initial_docs)

    # -------------------------------------------------------------------------
    # PART 1: UPSERT DEMONSTRATIONS (update_one with upsert=True)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("PART 1: UPSERT OPERATIONS (Conditional Insert / Update)")
    print("=" * 75)

    # 1a. Upsert Existing Product (PROD-A) -> Should update price only
    print("\n[Case 1] Upsert on EXISTING SKU ('PROD-A'): Changing price from $89.99 to $99.95")
    upsert_product_price(col, "PROD-A", 99.95)
    doc_a = col.find_one({"sku": "PROD-A"}, {"_id": 0})
    print(f"  → Verified Record: {doc_a['name']} | Price: ${doc_a['price']:.2f} | Stock: {doc_a['stock']}")

    # 1b. Upsert Non-Existent Product (PROD-NEW) -> Should insert with default values
    print("\n[Case 2] Upsert on NON-EXISTENT SKU ('PROD-NEW'): Inserting new document with default values")
    upsert_product_price(col, "PROD-NEW", 149.50, default_values={
        "name": "Smart Wireless Earbuds",
        "category": "Audio",
        "stock": 40,
        "is_active": True,
        "tags": ["audio", "wireless", "premium"]
    })
    doc_new = col.find_one({"sku": "PROD-NEW"}, {"_id": 0})
    print(f"  → Verified Record: {doc_new['name']} | Price: ${doc_new['price']:.2f} | Stock: {doc_new['stock']} | Tags: {doc_new['tags']}\n")

    # -------------------------------------------------------------------------
    # PART 2: BULK WRITE OPERATION (5 Simultaneous Updates + Verification)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("PART 2: BULK WRITE OPERATION (5 Simultaneous Updates)")
    print("=" * 75)
    print("Requirements:")
    print("  • Increase stock by 10 for products A, B, and C ($inc)")
    print("  • Set is_active to False for products D and E ($set)")
    print("  • Plus an upserted product F to verify upserted_count and upserted_ids\n")

    bulk_operations = [
        # Op 1: Increase stock by 10 for Product A
        UpdateOne({"sku": "PROD-A"}, {"$inc": {"stock": 10}}),
        # Op 2: Increase stock by 10 for Product B
        UpdateOne({"sku": "PROD-B"}, {"$inc": {"stock": 10}}),
        # Op 3: Increase stock by 10 for Product C
        UpdateOne({"sku": "PROD-C"}, {"$inc": {"stock": 10}}),
        # Op 4: Set is_active to False for Product D
        UpdateOne({"sku": "PROD-D"}, {"$set": {"is_active": False}}),
        # Op 5: Set is_active to False for Product E
        UpdateOne({"sku": "PROD-E"}, {"$set": {"is_active": False}}),
        # Op 6 (Optional Upsert demonstration in bulk write): Product F
        UpdateOne(
            {"sku": "PROD-F"},
            {
                "$set": {"price": 199.99},
                "$setOnInsert": {
                    "sku": "PROD-F",
                    "name": "Product F Curved Display",
                    "stock": 25,
                    "is_active": True,
                    "category": "Displays"
                }
            },
            upsert=True
        )
    ]

    print(f"Executing bulk_write with {len(bulk_operations)} UpdateOne operations...")
    bulk_result = col.bulk_write(bulk_operations)

    # Result Verification
    print("\n--- Bulk Write Result Verification ---")
    print(f"  • Matched Count:     {bulk_result.matched_count} (Expected: 5 existing products A, B, C, D, E)")
    print(f"  • Modified Count:    {bulk_result.modified_count} (Expected: 5 modified)")
    print(f"  • Upserted Count:    {bulk_result.upserted_count} (Expected: 1 new product F upserted)")
    print(f"  • Upserted IDs:      {bulk_result.upserted_ids}")
    print(f"  • Acknowledged:      {bulk_result.acknowledged}")

    # Display Final State
    final_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    display_inventory_table("Final Inventory State (After Bulk Write Execution)", final_docs)

    # Export collection to JSON
    json_path = os.path.join(BASE_DIR, "inventory_upsert_bulk.json")
    export_collection_to_json("nosql_labs", col_name, json_path)

    banner("Lab 4.2 Execution Complete")


if __name__ == "__main__":
    main()
