"""Flask web application for NoSQL Lab 10 – interactive demo of
Lab 10.1 (Bank Transfer) and Lab 10.2 (Inventory Reservation).
"""

import os, sys, time, threading, uuid

# ── path setup: works both locally and inside Docker (/app) ─────────────────
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, ".."))

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, WriteConcern, errors
from pymongo.read_concern import ReadConcern
from pymongo.errors import OperationFailure, PyMongoError

class WriteConflict(PyMongoError):
    """Raised on version mismatch or concurrent update conflict."""
    pass
errors.WriteConflict = WriteConflict

MONGO_URI   = os.getenv("MONGO_URI", "mongodb://mongo:27017/?replicaSet=rs0")
MAX_RETRIES = 5
BASE_DELAY  = 0.1

app = Flask(__name__)

# ── lazy singleton client (connects on first request) ───────────────────────
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000)
    return _client

def _db_bank(): return _get_client()["bank"]
def _db_inv():  return _get_client()["inv_db"]

# ── data helpers ─────────────────────────────────────────────────────────────

def _accounts():
    return list(_db_bank()["accounts"].find({}, {"_id": 0}).sort("account_id", 1))

def _products():
    return list(_db_inv()["products"].find({}, {"_id": 0}))

def _orders():
    return list(_db_inv()["orders"].find({}, {"_id": 0}).sort("created_at", -1).limit(50))

def _txn_log():
    return list(_db_bank()["transactions"].find({}, {"_id": 0}).sort("timestamp", -1).limit(50))


# ── Lab 10.1 – bank transfer ─────────────────────────────────────────────────

def _transfer(from_id, to_id, amount, description):
    col = _db_bank()["accounts"]
    for attempt in range(MAX_RETRIES):
        with _get_client().start_session() as session:
            try:
                with session.start_transaction(
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern(w="majority"),
                ):
                    r = col.update_one(
                        {"account_id": from_id, "balance": {"$gte": amount}},
                        {"$inc": {"balance": -amount, "version": 1}},
                        session=session,
                    )
                    if r.matched_count == 0:
                        return {"ok": False, "msg": f"Insufficient funds in {from_id}"}
                    col.update_one(
                        {"account_id": to_id},
                        {"$inc": {"balance": amount, "version": 1}},
                        session=session,
                    )
                    _db_bank()["transactions"].insert_one(
                        {"from": from_id, "to": to_id, "amount": amount,
                         "description": description, "timestamp": time.time()},
                        session=session,
                    )
                return {"ok": True, "msg": f"Transferred ${amount:.2f}: {from_id} to {to_id}"}
            except (OperationFailure, PyMongoError) as e:
                labels = getattr(e, "error_labels", []) or []
                if "TransientTransactionError" in labels and attempt < MAX_RETRIES - 1:
                    time.sleep(BASE_DELAY * (2 ** attempt))
                else:
                    return {"ok": False, "msg": str(e)}
    return {"ok": False, "msg": "Exhausted retries"}


# ── Lab 10.2 – inventory reservation ─────────────────────────────────────────

def _reserve(product_id, customer_id, qty=1):
    db = _db_inv()
    for attempt in range(MAX_RETRIES):
        with _get_client().start_session() as session:
            try:
                with session.start_transaction(write_concern=WriteConcern(w="majority")):
                    item = db.products.find_one({"product_id": product_id}, session=session)
                    if not item:
                        return {"ok": False, "msg": "Product not found"}
                    if item["stock"] < qty:
                        return {"ok": False, "msg": f"Insufficient stock ({item['stock']} left)"}
                    r = db.products.update_one(
                        {"product_id": product_id, "version": item["version"]},
                        {"$inc": {"stock": -qty, "version": 1}},
                        session=session,
                    )
                    if r.matched_count == 0:
                        raise WriteConflict("Version mismatch")
                    order_id = str(uuid.uuid4())
                    db.orders.insert_one({
                        "order_id": order_id, "customer_id": customer_id,
                        "items": [{"product_id": product_id, "qty": qty, "price": item["price"]}],
                        "status": "pending", "total": item["price"] * qty,
                        "created_at": time.time(),
                    }, session=session)
                return {"ok": True, "msg": f"Reserved {qty}x {product_id}", "order_id": order_id}
            except (WriteConflict, OperationFailure, PyMongoError) as e:
                labels = getattr(e, "error_labels", []) or []
                is_t = isinstance(e, WriteConflict) or "TransientTransactionError" in labels
                if is_t and attempt < MAX_RETRIES - 1:
                    time.sleep(BASE_DELAY * (2 ** attempt))
                else:
                    return {"ok": False, "msg": f"Conflict: {e}"}
    return {"ok": False, "msg": "Exhausted retries"}


# ── Page routes ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lab1")
def lab1():
    try:
        accounts = _accounts()
        txn_log  = _txn_log()
    except Exception:
        accounts, txn_log = [], []
    return render_template("lab1.html", accounts=accounts, txn_log=txn_log)

@app.route("/lab2")
def lab2():
    try:
        products = _products()
        orders   = _orders()
    except Exception:
        products, orders = [], []
    return render_template("lab2.html", products=products, orders=orders)


# ── Lab 10.1 API ─────────────────────────────────────────────────────────────

@app.route("/api/accounts")
def api_accounts():
    return jsonify(_accounts())

@app.route("/api/accounts/seed", methods=["POST"])
def api_seed_accounts():
    col = _db_bank()["accounts"]
    col.drop()
    _db_bank()["transactions"].drop()
    col.insert_many([
        {"account_id": "ACC-001", "holder": "Arjun",  "balance": 5000.00, "version": 0},
        {"account_id": "ACC-002", "holder": "Sneha",  "balance": 3000.00, "version": 0},
        {"account_id": "ACC-003", "holder": "Rahul",  "balance": 1000.00, "version": 0},
    ])
    return jsonify({"ok": True, "msg": "Accounts re-seeded"})

@app.route("/api/transfer", methods=["POST"])
def api_transfer():
    d = request.json
    result = _transfer(d["from_id"], d["to_id"], float(d["amount"]), d.get("description", "Web transfer"))
    result["accounts"] = _accounts()
    result["txn_log"]  = _txn_log()
    return jsonify(result)

@app.route("/api/transactions")
def api_transactions():
    return jsonify(_txn_log())


# ── Lab 10.2 API ─────────────────────────────────────────────────────────────

@app.route("/api/products")
def api_products():
    return jsonify(_products())

@app.route("/api/products/seed", methods=["POST"])
def api_seed_products():
    db = _db_inv()
    db.products.drop()
    db.orders.drop()
    db.products.insert_many([
        {"product_id": "LAPTOP-PRO", "name": "UltraBook Pro",  "stock": 5,  "version": 0, "price": 999.99},
        {"product_id": "HEADPHONES", "name": "Studio Headset", "stock": 10, "version": 0, "price": 149.99},
        {"product_id": "WEBCAM-HD",  "name": "HD Webcam Pro",  "stock": 8,  "version": 0, "price": 79.99},
    ])
    return jsonify({"ok": True, "msg": "Inventory re-seeded"})

@app.route("/api/reserve", methods=["POST"])
def api_reserve():
    d = request.json
    result = _reserve(d["product_id"], d.get("customer_id", "CUST-WEB"), int(d.get("qty", 1)))
    result["products"] = _products()
    result["orders"]   = _orders()
    return jsonify(result)

@app.route("/api/concurrent-test", methods=["POST"])
def api_concurrent_test():
    d          = request.json
    n_threads  = int(d.get("threads", 8))
    product_id = d.get("product_id", "LAPTOP-PRO")
    stock      = int(d.get("stock", 5))

    db = _db_inv()
    db.products.update_one({"product_id": product_id}, {"$set": {"stock": stock, "version": 0}})
    db.orders.delete_many({"items.0.product_id": product_id})

    results, lock = [], threading.Lock()

    def worker(i):
        r = _reserve(product_id, f"CUST-{i:03d}", 1)
        with lock:
            results.append(r)

    start = time.perf_counter()
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    elapsed = round(time.perf_counter() - start, 3)

    successes = sum(1 for r in results if r["ok"])
    return jsonify({
        "ok": True,
        "threads":    n_threads,
        "successes":  successes,
        "failures":   n_threads - successes,
        "elapsed_s":  elapsed,
        "throughput": round(successes / elapsed, 2) if elapsed > 0 else 0,
        "results":    results,
        "products":   _products(),
        "orders":     _orders(),
    })

@app.route("/api/orders")
def api_orders():
    return jsonify(_orders())

@app.route("/health")
def health():
    try:
        _get_client().admin.command("ping")
        return jsonify({"status": "ok", "mongo": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "mongo": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
