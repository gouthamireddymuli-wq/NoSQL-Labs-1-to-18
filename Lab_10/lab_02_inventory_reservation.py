"""Lab 10.2 - Inventory Reservation with Deadlock Handling
E-commerce inventory reservation using multi-document transactions,
concurrent threads, write-conflict retry logic, and throughput measurement.

Requires: MongoDB 4.0+ running as a replica set (rs0).
"""

import sys, os, time, uuid, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient, WriteConcern, errors
from pymongo.errors import OperationFailure, PyMongoError

class WriteConflict(PyMongoError):
    """Raised on version mismatch or concurrent update conflict."""
    pass
errors.WriteConflict = WriteConflict
from config.connection import banner, get_client

MAX_RETRIES   = 5
BASE_DELAY_S  = 0.05   # 50 ms


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def seed_inventory(db, stock: int = 5):
    db.products.drop()
    db.orders.drop()
    db.products.insert_one({
        "product_id": "LAPTOP-PRO",
        "name":       "UltraBook Pro",
        "stock":      stock,
        "version":    0,
        "price":      999.99,
    })
    print(f"  [OK] Seeded 1 product with {stock} units.")


def current_stock(db):
    doc = db.products.find_one({"product_id": "LAPTOP-PRO"})
    return doc["stock"] if doc else 0


# ---------------------------------------------------------------------------
# Core reservation (single attempt inside an open session/transaction)
# ---------------------------------------------------------------------------

def _do_reserve(db, product_id, customer_id, qty, session):
    item = db.products.find_one({"product_id": product_id}, session=session)
    if item is None:
        raise ValueError(f"Product {product_id!r} not found")
    if item["stock"] < qty:
        raise ValueError(f"Insufficient stock: have {item['stock']}, need {qty}")

    # Decrement stock (optimistic concurrency via version field)
    result = db.products.update_one(
        {"product_id": product_id, "version": item["version"]},
        {"$inc": {"stock": -qty, "version": 1}},
        session=session,
    )
    if result.matched_count == 0:
        # Another transaction changed version between our read and write
        raise WriteConflict("Version mismatch – concurrent modification")

    order_id = str(uuid.uuid4())
    db.orders.insert_one(
        {
            "order_id":    order_id,
            "customer_id": customer_id,
            "items":       [{"product_id": product_id, "qty": qty, "price": item["price"]}],
            "status":      "pending",
            "total":       item["price"] * qty,
            "created_at":  time.time(),
        },
        session=session,
    )
    return order_id


# ---------------------------------------------------------------------------
# Public API – session management + retry with exponential back-off
# ---------------------------------------------------------------------------

def reserve_inventory(client, product_id, customer_id, qty=1):
    """Reserve inventory in a transaction.  Returns (success, message)."""
    db = client["inv_db"]

    for attempt in range(MAX_RETRIES):
        with client.start_session() as session:
            try:
                with session.start_transaction(
                    write_concern=WriteConcern(w="majority"),
                ):
                    order_id = _do_reserve(db, product_id, customer_id, qty, session)
                return True, f"RESERVED order {order_id[:8]}…"

            except ValueError as e:
                return False, f"INSUFFICIENT – {e}"

            except (WriteConflict, OperationFailure, PyMongoError) as e:
                labels = getattr(e, "error_labels", []) or []
                is_transient = (
                    isinstance(e, WriteConflict)
                    or "TransientTransactionError" in labels
                    or "WriteConflict" in str(e)
                )
                if is_transient and attempt < MAX_RETRIES - 1:
                    delay = BASE_DELAY_S * (2 ** attempt)
                    time.sleep(delay)
                else:
                    return False, f"CONFLICT after {attempt+1} attempts – {e}"

    return False, "EXHAUSTED retries"


# ---------------------------------------------------------------------------
# Concurrency test
# ---------------------------------------------------------------------------

def run_concurrent_test(client, n_threads: int, stock: int = 5):
    db = client["inv_db"]
    seed_inventory(db, stock)

    start = time.perf_counter()
    futures_map = {}
    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        for i in range(n_threads):
            cid = f"CUST-{i:03d}"
            f   = pool.submit(reserve_inventory, client, "LAPTOP-PRO", cid, 1)
            futures_map[f] = cid

    elapsed   = time.perf_counter() - start
    successes = sum(1 for f in futures_map if f.result()[0])
    remaining = current_stock(db)
    orders    = db.orders.count_documents({})

    return {
        "threads":    n_threads,
        "successes":  successes,
        "failures":   n_threads - successes,
        "remaining":  remaining,
        "orders":     orders,
        "elapsed_s":  round(elapsed, 3),
        "throughput": round(successes / elapsed, 2) if elapsed > 0 else 0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    banner("Lab 10.2: Inventory Reservation with Deadlock Handling")
    client = get_client()

    # --- Single-scenario demonstration ---
    print("\n=== Scenario: 10 threads competing for 5 units ===")
    res = run_concurrent_test(client, n_threads=10, stock=5)
    print(f"  Successes : {res['successes']}")
    print(f"  Failures  : {res['failures']}")
    print(f"  Remaining : {res['remaining']} units")
    print(f"  Orders    : {res['orders']}")
    print(f"  Elapsed   : {res['elapsed_s']} s")

    # --- Throughput sweep ---
    print("\n=== Throughput sweep (5 units, varying threads) ===")
    print(f"  {'Threads':>8}  {'Success':>8}  {'Fail':>6}  {'Stock':>6}  {'Orders':>7}  {'Elapsed':>8}  {'TPS':>7}")
    print("  " + "-" * 68)
    for n in [1, 4, 8, 16]:
        r = run_concurrent_test(client, n_threads=n, stock=5)
        print(
            f"  {r['threads']:>8}  {r['successes']:>8}  {r['failures']:>6}  "
            f"{r['remaining']:>6}  {r['orders']:>7}  {r['elapsed_s']:>8.3f}s  {r['throughput']:>6.2f}"
        )

    client.close()
    banner("Lab 10.2 Complete")


if __name__ == "__main__":
    main()
