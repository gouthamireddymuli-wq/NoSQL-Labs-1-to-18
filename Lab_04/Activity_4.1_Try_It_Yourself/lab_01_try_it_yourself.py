"""Activity 4.1: Try It Yourself - Text Search Using $regex Operator
Objective: Add a text search capability using the $regex operator to find products
whose name contains a search string (case-insensitive).

Features:
1. Case-insensitive substring matching using {"name": {"$regex": pattern, "$options": "i"}}.
2. Prefix pattern search (^ anchor) to demonstrate index-friendly search patterns.
3. Suffix pattern search ($ anchor) for end-of-name matching.
4. Compound query combining $regex text search with numeric filter ($lte price constraint).
5. Input sanitization using re.escape to prevent regex injection vulnerabilities.
6. Export demonstration search results and products to products_regex_search.json.
"""

import os
import sys
import re
import json

# Ensure parent directory is in path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from config.connection import get_db, banner, export_collection_to_json
from rich.console import Console
from rich.table import Table

console = Console()


def search_by_name_regex(col, search_term, prefix_only=False, suffix_only=False, case_insensitive=True, extra_filter=None):
    """Search products where name matches the search term using $regex."""
    # Sanitize search term to prevent regex injection
    safe_term = re.escape(search_term.strip())
    
    if prefix_only:
        pattern = f"^{safe_term}"
    elif suffix_only:
        pattern = f"{safe_term}$"
    else:
        pattern = safe_term

    options = "i" if case_insensitive else ""

    query = {"name": {"$regex": pattern, "$options": options}}
    if extra_filter:
        query.update(extra_filter)

    cursor = col.find(query, {"_id": 0, "sku": 1, "name": 1, "price": 1, "stock": 1, "category": 1, "tags": 1})
    cursor = cursor.sort("name", 1)
    results = list(cursor)
    return pattern, options, query, results


def display_search_table(title, pattern, options, query, results):
    """Display pretty formatted table of search results."""
    table = Table(title=title, title_style="bold green", border_style="cyan")
    table.add_column("SKU", style="yellow", justify="center")
    table.add_column("Product Name", style="bold white")
    table.add_column("Category", style="magenta")
    table.add_column("Price ($)", style="green", justify="right")
    table.add_column("Stock", style="blue", justify="center")
    table.add_column("Tags", style="cyan")

    for doc in results:
        table.add_row(
            doc.get("sku", "N/A"),
            doc.get("name", "N/A"),
            doc.get("category", "N/A"),
            f"${doc.get('price', 0):.2f}",
            str(doc.get("stock", 0)),
            ", ".join(doc.get("tags", []))
        )

    console.print(table)
    console.print(f"  [dim]MongoDB Filter: {json.dumps(query, default=str)}[/dim]")
    console.print(f"  [bold cyan]→ Total Matches Found: {len(results)}[/bold cyan]\n")


def main():
    banner("Activity 4.1: Try It Yourself - Text Search with $regex")
    db = get_db("nosql_labs")
    col = db["products"]

    # Verify collection has documents
    doc_count = col.count_documents({})
    if doc_count == 0:
        print("[!] Products collection is empty. Run Lab 4.1 first to seed data.")
        return

    print(f"[OK] Connected to 'products' collection ({doc_count} documents available).\n")

    all_search_exports = {}

    # Test 1: Substring Case-Insensitive Search for "wireless"
    print("=" * 75)
    print("TEST 1: Substring Search for 'wireless' (Case-Insensitive)")
    print("=" * 75)
    pat, opt, q, res = search_by_name_regex(col, "wireless", case_insensitive=True)
    display_search_table("Search: Name contains 'wireless' (case-insensitive)", pat, opt, q, res)
    all_search_exports["search_wireless"] = {"query": q, "count": len(res), "results": res}

    # Test 2: Substring Case-Insensitive Search for "keyboard"
    print("=" * 75)
    print("TEST 2: Substring Search for 'keyboard' (Case-Insensitive)")
    print("=" * 75)
    pat, opt, q, res = search_by_name_regex(col, "keyboard", case_insensitive=True)
    display_search_table("Search: Name contains 'keyboard' (case-insensitive)", pat, opt, q, res)
    all_search_exports["search_keyboard"] = {"query": q, "count": len(res), "results": res}

    # Test 3: Prefix Anchored Search (^ anchor) for "Ultra"
    print("=" * 75)
    print("TEST 3: Prefix-Anchored Search for names starting with 'Ultra' (^Ultra)")
    print("=" * 75)
    pat, opt, q, res = search_by_name_regex(col, "Ultra", prefix_only=True, case_insensitive=True)
    display_search_table("Prefix Search: Name starts with 'Ultra'", pat, opt, q, res)
    all_search_exports["prefix_ultra"] = {"query": q, "count": len(res), "results": res}

    # Test 4: Suffix Anchored Search ($ anchor) for "Stand"
    print("=" * 75)
    print("TEST 4: Suffix-Anchored Search for names ending with 'Stand' (Stand$)")
    print("=" * 75)
    pat, opt, q, res = search_by_name_regex(col, "Stand", suffix_only=True, case_insensitive=True)
    display_search_table("Suffix Search: Name ends with 'Stand'", pat, opt, q, res)
    all_search_exports["suffix_stand"] = {"query": q, "count": len(res), "results": res}

    # Test 5: Compound Query ($regex Name Search + Numeric Filter: Price <= 100)
    print("=" * 75)
    print("TEST 5: Compound Query ($regex Name search 'desk' AND price <= 50.00)")
    print("=" * 75)
    pat, opt, q, res = search_by_name_regex(
        col, "desk",
        case_insensitive=True,
        extra_filter={"price": {"$lte": 50.0}}
    )
    display_search_table("Compound Search: 'desk' IN name AND price <= $50.00", pat, opt, q, res)
    all_search_exports["compound_desk_budget"] = {"query": q, "count": len(res), "results": res}

    # Export comprehensive search results to JSON
    json_path = os.path.join(BASE_DIR, "products_regex_search.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_search_exports, f, indent=2, default=str)
    print(f"[OK] Exported regex search results to {json_path}")

    # Technical Notes Summary
    console.print("\n[bold yellow]=== Technical Performance & Indexing Analysis of $regex ===[/bold yellow]")
    console.print("1. [bold green]Prefix Anchored Queries (^pattern):[/bold green] If an index exists on the 'name' field,")
    console.print("   MongoDB can use index range scans because it knows the start boundary.")
    console.print("2. [bold red]Unanchored Substring Queries (pattern):[/bold red] Requires scanning all index keys or documents,")
    console.print("   as the target substring could appear anywhere in the string.")
    console.print("3. [bold cyan]Case-Insensitive Flag ($options: 'i'):[/bold cyan] In MongoDB, using 'i' inhibits normal index prefix")
    console.print("   optimization unless a Collation index with strength: 1 or 2 is defined on the collection.")
    console.print("4. [bold magenta]Alternative ($text Index):[/bold magenta] For large corpora, full-text search indexes ($text)")
    console.print("   provide tokenized stemming and inverted index lookups with superior scale.\n")

    banner("Activity 4.1: Try It Yourself Complete")


if __name__ == "__main__":
    main()
