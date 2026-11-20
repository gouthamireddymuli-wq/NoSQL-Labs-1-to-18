"""Activity 4.2: Try It Yourself - Idempotent Bulk Import Function
Objective: Implement an idempotent bulk import function that can be run multiple times
without creating duplicates, using upsert logic for each document.

Key Concepts:
- Idempotency Definition: f(f(x)) = f(x). Re-running an import operation multiple times
  leaves the database in the exact same state without producing side-effects (duplicates or corrupted data).
- Naive insert_many vs Idempotent Bulk Upsert:
  * Naive insert_many: Creates duplicate documents on re-runs (or throws DuplicateKeyError if unique index exists).
  * Idempotent Bulk Upsert (UpdateOne with upsert=True): Updates existing records and inserts only new records.
- Verification across 4 distinct execution phases:
  Phase 1: Initial bulk import (8 products).
  Phase 2: Immediate re-import of identical payload (verifies 0 upserts, 0 modifications, 0 duplicates).
  Phase 3: Incremental sync (updates to 5 existing products + 3 brand new products).
  Phase 4: Re-import of Phase 3 payload (verifies stability and zero further mutations).
- Export final collection state to idempotent_bulk_import.json.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

# Ensure parent directory is in path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from config.connection import get_db, banner, export_collection_to_json
from rich.console import Console
from rich.table import Table

console = Console()

# Batch 1: Initial 8 products to import
INITIAL_BATCH = [
    {"sku": "SKU-101", "name": "4K Ultra-Wide Monitor", "price": 499.99, "stock": 25, "category": "Displays", "tags": ["4K", "monitor", "productivity"]},
    {"sku": "SKU-102", "name": "Mechanical Tenkeyless Keyboard", "price": 109.99, "stock": 40, "category": "Keyboards", "tags": ["mechanical", "tkl", "rgb"]},
    {"sku": "SKU-103", "name": "Ergonomic Vertical Mouse", "price": 59.99, "stock": 60, "category": "Mice", "tags": ["ergonomic", "wireless"]},
    {"sku": "SKU-104", "name": "Studio Condenser Microphone", "price": 129.99, "stock": 15, "category": "Audio", "tags": ["audio", "studio", "usb"]},
    {"sku": "SKU-105", "name": "Wireless Charging Pad 15W", "price": 24.99, "stock": 100, "category": "Accessories", "tags": ["charging", "wireless", "fast"]},
    {"sku": "SKU-106", "name": "Thunderbolt 4 Docking Station", "price": 219.99, "stock": 18, "category": "Accessories", "tags": ["thunderbolt", "dock", "usb-c"]},
    {"sku": "SKU-107", "name": "Active Noise Cancelling Earbuds", "price": 149.99, "stock": 35, "category": "Audio", "tags": ["anc", "wireless", "earbuds"]},
    {"sku": "SKU-108", "name": "Smart Ambient Light Bar", "price": 69.99, "stock": 50, "category": "Lighting", "tags": ["smart-light", "rgb", "desk"]}
]

# Batch 2: Incremental sync containing 5 updated products and 3 new products
INCREMENTAL_SYNC_BATCH = [
    # Updated existing products (new prices and restocked inventory)
    {"sku": "SKU-101", "name": "4K Ultra-Wide Monitor (V2)", "price": 479.99, "stock": 40, "category": "Displays", "tags": ["4K", "monitor", "productivity", "hdr"]},
    {"sku": "SKU-102", "name": "Mechanical Tenkeyless Keyboard", "price": 99.99, "stock": 55, "category": "Keyboards", "tags": ["mechanical", "tkl", "rgb"]},
    {"sku": "SKU-103", "name": "Ergonomic Vertical Mouse", "price": 54.99, "stock": 75, "category": "Mice", "tags": ["ergonomic", "wireless"]},
    {"sku": "SKU-104", "name": "Studio Condenser Microphone", "price": 119.99, "stock": 30, "category": "Audio", "tags": ["audio", "studio", "usb"]},
    {"sku": "SKU-105", "name": "Wireless Charging Pad 15W", "price": 21.99, "stock": 150, "category": "Accessories", "tags": ["charging", "wireless", "fast"]},
    # 3 brand new products
    {"sku": "SKU-109", "name": "Dual Monitor Arm Mount", "price": 79.99, "stock": 28, "category": "Mounts", "tags": ["desk-mount", "ergonomic", "dual-arm"]},
    {"sku": "SKU-110", "name": "HD 1080p Pro Webcam with Privacy Shutter", "price": 89.99, "stock": 42, "category": "Cameras", "tags": ["webcam", "1080p", "streaming"]},
    {"sku": "SKU-111", "name": "Braided Cable Management Sleeve", "price": 14.99, "stock": 200, "category": "Accessories", "tags": ["cable-management", "organization"]}
]


def display_import_summary(phase_name, result, total_in_db):
    """Format and print results of bulk import."""
    table = Table(title=f"Bulk Import Execution Summary - {phase_name}", title_style="bold yellow", border_style="green")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Count", style="bold white", justify="center")
    table.add_column("Implication", style="dim")

    table.add_row("Matched Count", str(result.matched_count), "Documents that already existed in the collection")
    table.add_row("Modified Count", str(result.modified_count), "Existing documents whose values actually changed")
    table.add_row("Upserted Count", str(result.upserted_count), "Brand new documents created via upsert")
    table.add_row("Total in Database", str(total_in_db), "Current size of collection (proves no duplicates)")

    console.print(table)
    console.print()


def display_inventory_table(title, docs):
    """Render a clean rich table showing inventory state."""
    table = Table(title=title, title_style="bold blue", border_style="cyan")
    table.add_column("SKU", style="yellow", justify="center")
    table.add_column("Product Name", style="white")
    table.add_column("Category", style="magenta")
    table.add_column("Price ($)", style="green", justify="right")
    table.add_column("Stock", style="cyan", justify="center")
    table.add_column("Tags", style="dim")

    for doc in docs:
        table.add_row(
            doc.get("sku", "N/A"),
            doc.get("name", "N/A"),
            doc.get("category", "N/A"),
            f"${doc.get('price', 0):.2f}",
            str(doc.get("stock", 0)),
            ", ".join(doc.get("tags", []))
        )
    console.print(table)
    console.print()


def idempotent_bulk_import(col, product_list, key_field="sku"):
    """Idempotent bulk import function.
    Can be run repeatedly without creating duplicates, using upsert logic.
    - Matches on key_field (SKU)
    - Sets current document attributes with $set
    - Sets creation metadata only on new inserts with $setOnInsert
    """
    if not product_list:
        return None

    operations = []
    current_time = datetime.now(timezone.utc)

    for item in product_list:
        key_value = item[key_field]
        # Exclude key_field, created_at, and _id from $set to ensure true data idempotency
        set_fields = {k: v for k, v in item.items() if k not in ["_id", "created_at", key_field]}

        op = UpdateOne(
            {key_field: key_value},
            {
                "$set": set_fields,
                "$setOnInsert": {
                    key_field: key_value,
                    "created_at": current_time
                }
            },
            upsert=True
        )
        operations.append(op)

    try:
        bulk_result = col.bulk_write(operations, ordered=False)
        return bulk_result
    except BulkWriteError as bwe:
        console.print(f"[bold red]Bulk write encountered errors:[/bold red] {bwe.details}")
        raise


def main():
    banner("Activity 4.2: Try It Yourself - Idempotent Bulk Import")
    db = get_db("nosql_labs")

    # Reset collection
    col_name = "products_bulk_import"
    if col_name in db.list_collection_names():
        db.drop_collection(col_name)
    col = db[col_name]

    # Ensure unique index on sku (defense-in-depth)
    col.create_index("sku", unique=True)
    print(f"[OK] Initialized '{col_name}' collection with unique index on 'sku'.\n")

    # -------------------------------------------------------------------------
    # RUN 1: Initial Bulk Import of 8 Products
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("RUN 1: INITIAL BULK IMPORT (8 Products)")
    print("=" * 75)
    res_1 = idempotent_bulk_import(col, INITIAL_BATCH, key_field="sku")
    count_1 = col.count_documents({})
    display_import_summary("Run 1 (Initial Import)", res_1, count_1)

    # -------------------------------------------------------------------------
    # RUN 2: Immediate Re-run with the Exact Same 8 Products (IDEMPOTENCY TEST)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("RUN 2: RE-RUNNING THE SAME BATCH (Idempotency Verification)")
    print("=" * 75)
    print("Testing if re-running the exact same payload causes duplicate documents or unnecessary writes...\n")
    res_2 = idempotent_bulk_import(col, INITIAL_BATCH, key_field="sku")
    count_2 = col.count_documents({})
    display_import_summary("Run 2 (Identical Re-run)", res_2, count_2)

    # Verification assertions
    assert res_2.upserted_count == 0, "Upserted count must be 0 on re-run!"
    assert count_2 == count_1, "Total document count must remain identical (no duplicates)!"
    print("  [IDEMPOTENT VERIFIED] 0 documents upserted, 0 duplicates created. Total records: 8.\n")

    # -------------------------------------------------------------------------
    # RUN 3: Incremental Sync (5 Updated Products + 3 New Products)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("RUN 3: INCREMENTAL SYNC BATCH (5 Updates + 3 New Products)")
    print("=" * 75)
    res_3 = idempotent_bulk_import(col, INCREMENTAL_SYNC_BATCH, key_field="sku")
    count_3 = col.count_documents({})
    display_import_summary("Run 3 (Incremental Sync)", res_3, count_3)

    # -------------------------------------------------------------------------
    # RUN 4: Re-running Incremental Batch (IDEMPOTENCY OF COMPOSITE BATCH)
    # -------------------------------------------------------------------------
    print("=" * 75)
    print("RUN 4: RE-RUNNING INCREMENTAL SYNC BATCH (Stability Verification)")
    print("=" * 75)
    res_4 = idempotent_bulk_import(col, INCREMENTAL_SYNC_BATCH, key_field="sku")
    count_4 = col.count_documents({})
    display_import_summary("Run 4 (Re-run Incremental Sync)", res_4, count_4)

    assert res_4.upserted_count == 0, "Upserted count must be 0 on second run of incremental batch!"
    assert count_4 == count_3, "Collection count must remain 11!"
    print("  [IDEMPOTENT VERIFIED] System state is completely stable after repeated syncs.\n")

    # Display Final Collection Contents
    final_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    display_inventory_table("Final Database Collection State After All Import Runs (11 Products)", final_docs)

    # Export collection to JSON
    json_path = os.path.join(BASE_DIR, "idempotent_bulk_import.json")
    export_collection_to_json("nosql_labs", col_name, json_path)

    # Technical Comparison
    console.print("\n[bold yellow]=== Architectural Takeaways: Idempotency in Production ===[/bold yellow]")
    console.print("1. [bold cyan]Safe Retries:[/bold cyan] In distributed networks, API calls or cron tasks can fail due to timeouts.")
    console.print("   An idempotent import guarantees that re-triggering the pipeline produces no duplicate records.")
    console.print("2. [bold green]In-Place Upserts:[/bold green] UpdateOne with upsert=True combines insert and update in a single")
    console.print("   round-trip per batch, maximizing write throughput.")
    console.print("3. [bold magenta]$setOnInsert vs $set:[/bold magenta] Immutable fields (like created_at or original SKU) are preserved")
    console.print("   on updates, while dynamic fields (price, stock) stay synchronized.\n")

    banner("Activity 4.2: Try It Yourself Complete")


if __name__ == "__main__":
    main()
