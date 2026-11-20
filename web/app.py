"""Flask Web Application for NoSQL Lab 15: Multi-Tenancy & Tenant Migration.
Author: M Gouthami (24BTRCL130)

Features:
  - Lab 15.1: Multi-Tenant SaaS API (Tenant Scoping, Cross-Tenant BOLA Prevention, DB-Native Rate Limiter)
  - Lab 15.2: Tenant Isolation Migration (Shared-Collection to Dedicated DB, Dry-Run, Idempotency, Verification, Rollback)
  - Architecture Explorer & Interactive Security Simulator
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime, timezone
from bson import ObjectId
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config.connection import get_client, get_db, reset_collection

app = Flask(__name__)
CORS(app)

SHARED_DB = "saas_app"
SHARED_COLLECTION = "tasks"
RATE_COLLECTION = "rate_limits"


# ── Helpers ────────────────────────────────────────────────────────────────────

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def tenant_db_name(tenant_id: str) -> str:
    cleaned = tenant_id.replace("tenant-", "").replace("-", "_")
    return f"tenant_{cleaned}"


def content_checksum(docs: list) -> str:
    rows = [json.dumps(d, sort_keys=True, default=json_serial) for d in sorted(docs, key=lambda d: d.get("title", ""))]
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


# ── MongoDB API Logic from Lab 15.1 & 15.2 ─────────────────────────────────────

def db_check_rate_limit(tenant_id: str, limit: int = 10, window_secs: int = 60):
    """MongoDB-native rate limiter. Returns (is_allowed, current_count, limit, window)."""
    db = get_db(SHARED_DB)
    rate_col = db[RATE_COLLECTION]
    cutoff = time.time() - window_secs
    count = rate_col.count_documents({
        "tenant_id": tenant_id,
        "timestamp": {"$gt": cutoff}
    })
    if count >= limit:
        return False, count, limit, window_secs
    rate_col.insert_one({"tenant_id": tenant_id, "timestamp": time.time()})
    return True, count + 1, limit, window_secs


def api_create_task(tenant_id: str, title: str, description: str, priority: str = "medium", assignee: str = None):
    db = get_db(SHARED_DB)
    col = db[SHARED_COLLECTION]
    task = {
        "tenant_id": tenant_id,
        "title": title,
        "description": description,
        "priority": priority,
        "assignee": assignee,
        "status": "open",
        "created_at": time.time(),
        "updated_at": time.time(),
    }
    res = col.insert_one(task)
    task["_id"] = str(res.inserted_id)
    return task


def api_get_tasks(tenant_id: str, status: str = None, priority: str = None):
    db = get_db(SHARED_DB)
    col = db[SHARED_COLLECTION]
    query = {"tenant_id": tenant_id}
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    tasks = list(col.find(query))
    for t in tasks:
        t["_id"] = str(t["_id"])
    return tasks


def api_update_task_secure(tenant_id: str, task_id_str: str, updates: dict):
    """Tenant-scoped update. Filters on BOTH _id and tenant_id."""
    db = get_db(SHARED_DB)
    col = db[SHARED_COLLECTION]
    try:
        oid = ObjectId(task_id_str)
    except Exception:
        return False, "Invalid task ID format", 0, 0

    updates["updated_at"] = time.time()
    # CRITICAL: Tenant isolation
    filter_q = {"_id": oid, "tenant_id": tenant_id}
    res = col.update_one(filter_q, {"$set": updates})
    return res.matched_count > 0, filter_q, res.matched_count, res.modified_count


def api_update_task_vulnerable(task_id_str: str, updates: dict):
    """Vulnerable update. Filters ONLY on _id, ignoring tenant_id."""
    db = get_db(SHARED_DB)
    col = db[SHARED_COLLECTION]
    try:
        oid = ObjectId(task_id_str)
    except Exception:
        return False, "Invalid task ID format", 0, 0

    updates["updated_at"] = time.time()
    filter_q = {"_id": oid}
    res = col.update_one(filter_q, {"$set": updates})
    return res.matched_count > 0, filter_q, res.matched_count, res.modified_count


def seed_baseline():
    client = get_client()
    db = client[SHARED_DB]
    col = db[SHARED_COLLECTION]
    col.drop()
    docs = [
        {"tenant_id": "tenant-acme", "title": "Setup ML Pipeline", "description": "Configure training pipeline for fraud model", "status": "open", "priority": "high", "assignee": "arjun", "created_at": time.time(), "updated_at": time.time()},
        {"tenant_id": "tenant-acme", "title": "Data Validation", "description": "Validate input data schema", "status": "open", "priority": "medium", "assignee": "sneha", "created_at": time.time(), "updated_at": time.time()},
        {"tenant_id": "tenant-globex", "title": "API Integration", "description": "Connect to payment gateway", "status": "open", "priority": "high", "assignee": "rahul", "created_at": time.time(), "updated_at": time.time()},
        {"tenant_id": "tenant-globex", "title": "User Testing", "description": "Run UAT for v2 release", "status": "completed", "priority": "low", "assignee": None, "created_at": time.time(), "updated_at": time.time()},
    ]
    col.insert_many(docs)
    return len(docs)


def execute_migration(tenant_id: str, dry_run: bool = False):
    client = get_client()
    shared_col = client[SHARED_DB][SHARED_COLLECTION]

    source_docs = list(shared_col.find({"tenant_id": tenant_id}, {"_id": 0}))
    if not source_docs:
        return {
            "tenant_id": tenant_id,
            "status": "NO_DATA",
            "moved": 0,
            "target_db": tenant_db_name(tenant_id),
            "message": f"No documents found for tenant '{tenant_id}' in shared collection."
        }

    target_database = tenant_db_name(tenant_id)

    if dry_run:
        return {
            "tenant_id": tenant_id,
            "status": "DRY_RUN",
            "would_move": len(source_docs),
            "target_db": target_database,
            "sample_docs": source_docs[:3],
            "message": f"Dry-run simulated successfully: {len(source_docs)} documents identified for migration."
        }

    target_col = client[target_database][SHARED_COLLECTION]

    # Idempotent write: upsert on (tenant_id, title)
    moved = 0
    for doc in source_docs:
        target_col.update_one(
            {"tenant_id": doc["tenant_id"], "title": doc["title"]},
            {"$set": doc},
            upsert=True
        )
        moved += 1

    # Verification: document count and content checksum
    target_docs = list(target_col.find({}, {"_id": 0}))
    source_cs = content_checksum(source_docs)
    target_cs = content_checksum(target_docs)
    verified = (len(target_docs) == len(source_docs)) and (source_cs == target_cs)

    return {
        "tenant_id": tenant_id,
        "status": "MIGRATED" if verified else "VERIFICATION_FAILED",
        "moved": moved,
        "target_db": target_database,
        "source_count": len(source_docs),
        "target_count": len(target_docs),
        "source_checksum": source_cs,
        "target_checksum": target_cs,
        "verified": verified,
        "message": f"Migration complete. Verified={verified}. Target count: {len(target_docs)}."
    }


def rollback_database(tenant_id: str):
    client = get_client()
    target_database = tenant_db_name(tenant_id)
    client.drop_database(target_database)
    return {
        "tenant_id": tenant_id,
        "target_db": target_database,
        "status": "ROLLED_BACK",
        "message": f"Database '{target_database}' dropped. Shared collection '{SHARED_DB}.{SHARED_COLLECTION}' remains intact."
    }


# ── Web Template Routes ────────────────────────────────────────────────────────

@app.route("/")
def index():
    try:
        client = get_client()
        server_info = client.server_info()
        version = server_info.get("version", "7.0")
        connected = True
        all_dbs = client.list_database_names()
        dedicated_dbs = [db for db in all_dbs if db.startswith("tenant_")]
        shared_count = client[SHARED_DB][SHARED_COLLECTION].count_documents({})
        distinct_tenants = client[SHARED_DB][SHARED_COLLECTION].distinct("tenant_id")
    except Exception as e:
        connected = False
        version = "Unknown"
        all_dbs = []
        dedicated_dbs = []
        shared_count = 0
        distinct_tenants = []

    return render_template(
        "index.html",
        connected=connected,
        version=version,
        host=os.getenv("HOSTNAME", "localhost"),
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        all_dbs=all_dbs,
        dedicated_count=len(dedicated_dbs),
        shared_count=shared_count,
        tenants=distinct_tenants,
    )


@app.route("/lab1")
def lab1():
    return render_template("lab1.html")


@app.route("/lab2")
def lab2():
    return render_template("lab2.html")


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")


# ── REST API Endpoints ─────────────────────────────────────────────────────────

@app.route("/api/health")
def api_health():
    try:
        client = get_client()
        client.admin.command("ping")
        server_info = client.server_info()
        all_dbs = client.list_database_names()
        dedicated_dbs = [db for db in all_dbs if db.startswith("tenant_")]
        return jsonify({
            "status": "healthy",
            "mongodb_connected": True,
            "version": server_info.get("version", "unknown"),
            "shared_db": SHARED_DB,
            "dedicated_databases": dedicated_dbs,
            "total_databases": len(all_dbs)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb_connected": False,
            "error": str(e)
        }), 500


@app.route("/api/tenants")
def api_get_tenants():
    try:
        client = get_client()
        shared_tenants = client[SHARED_DB][SHARED_COLLECTION].distinct("tenant_id")
        all_dbs = client.list_database_names()
        dedicated_tenants = [f"tenant-{db.replace('tenant_', '').replace('_', '-')}" for db in all_dbs if db.startswith("tenant_")]
        combined = sorted(list(set(shared_tenants + dedicated_tenants + ["tenant-acme", "tenant-globex"])))
        return jsonify({"tenants": combined})
    except Exception as e:
        return jsonify({"tenants": ["tenant-acme", "tenant-globex"]})


@app.route("/api/tasks", methods=["GET", "POST"])
def api_tasks():
    tenant_id = request.headers.get("X-Tenant-ID") or request.args.get("tenant_id")
    if not tenant_id and request.is_json:
        tenant_id = request.json.get("tenant_id")

    if not tenant_id:
        return jsonify({"error": "tenant_id is required via header X-Tenant-ID or query param tenant_id"}), 400

    # Rate limiting on write/read
    if request.method == "POST":
        allowed, count, limit, window = db_check_rate_limit(tenant_id, limit=10, window_secs=60)
        if not allowed:
            return jsonify({
                "error": "Too Many Requests",
                "message": f"Tenant '{tenant_id}' exceeded rate limit ({limit} req / {window}s).",
                "current_count": count,
                "limit": limit
            }), 429

        data = request.get_json() or {}
        title = data.get("title")
        if not title:
            return jsonify({"error": "title is required"}), 400
        desc = data.get("description", "")
        priority = data.get("priority", "medium")
        assignee = data.get("assignee")
        task = api_create_task(tenant_id, title, desc, priority, assignee)
        return jsonify({"message": "Task created successfully", "task": task}), 201

    # GET
    status = request.args.get("status")
    priority = request.args.get("priority")
    tasks = api_get_tasks(tenant_id, status, priority)
    return jsonify({"tenant_id": tenant_id, "count": len(tasks), "tasks": tasks})


@app.route("/api/tasks/<task_id>", methods=["PUT"])
def api_task_update(task_id):
    tenant_id = request.headers.get("X-Tenant-ID") or request.args.get("tenant_id")
    data = request.get_json() or {}
    if not tenant_id:
        tenant_id = data.get("tenant_id")

    if not tenant_id:
        return jsonify({"error": "tenant_id is required"}), 400

    updates = {k: v for k, v in data.items() if k not in ["_id", "tenant_id", "created_at"]}
    success, filter_used, matched, modified = api_update_task_secure(tenant_id, task_id, updates)

    if not success:
        return jsonify({
            "error": "Task not found or unauthorized cross-tenant modification prevented",
            "success": False,
            "filter_applied": {k: str(v) for k, v in filter_used.items()} if isinstance(filter_used, dict) else filter_used,
            "matched_count": matched,
            "modified_count": modified,
            "tenant_id": tenant_id
        }), 404

    return jsonify({
        "success": True,
        "message": "Task updated successfully within tenant boundary",
        "matched_count": matched,
        "modified_count": modified
    })


@app.route("/api/security/simulate-attack", methods=["POST"])
def api_simulate_attack():
    """Demonstrate BOLA vulnerability vs tenant scoping protection."""
    data = request.get_json() or {}
    target_task_id = data.get("task_id")
    attacker_tenant = data.get("attacker_tenant", "tenant-globex")
    mode = data.get("mode", "secure")  # "vulnerable" or "secure"
    payload = data.get("updates", {"status": "MALICIOUSLY_ALTERED_BY_ATTACKER"})

    if not target_task_id:
        # Pick the first Acme task as target
        db = get_db(SHARED_DB)
        acme_doc = db[SHARED_COLLECTION].find_one({"tenant_id": "tenant-acme"})
        if not acme_doc:
            seed_baseline()
            acme_doc = db[SHARED_COLLECTION].find_one({"tenant_id": "tenant-acme"})
        target_task_id = str(acme_doc["_id"])

    # Read original task state
    db = get_db(SHARED_DB)
    original_task = db[SHARED_COLLECTION].find_one({"_id": ObjectId(target_task_id)})
    if not original_task:
        return jsonify({"error": f"Target task {target_task_id} not found."}), 404

    real_owner = original_task.get("tenant_id")

    if mode == "vulnerable":
        success, filter_used, matched, modified = api_update_task_vulnerable(target_task_id, payload.copy())
        explanation = (
            "VULNERABLE IMPLEMENTATION: Query used filter `{_id: ObjectId}` WITHOUT checking tenant_id. "
            f"Attacker '{attacker_tenant}' successfully compromised task belonging to '{real_owner}'! "
            "This is Broken Object Level Authorization (BOLA / IDOR)."
        )
    else:
        success, filter_used, matched, modified = api_update_task_secure(attacker_tenant, target_task_id, payload.copy())
        explanation = (
            "SECURE IMPLEMENTATION: Query used compound filter `{_id: ObjectId, tenant_id: attacker_tenant}`. "
            f"Even though the task ID exists in MongoDB, it belongs to '{real_owner}', not '{attacker_tenant}'. "
            "MongoDB matched 0 documents. Cross-tenant tampering is 100% BLOCKED."
        )

    # Read updated task state
    current_task = db[SHARED_COLLECTION].find_one({"_id": ObjectId(target_task_id)})
    current_task["_id"] = str(current_task["_id"])

    return jsonify({
        "mode": mode,
        "attacker_tenant": attacker_tenant,
        "target_task_id": target_task_id,
        "real_owner": real_owner,
        "filter_executed": {k: str(v) for k, v in filter_used.items()} if isinstance(filter_used, dict) else filter_used,
        "matched_count": matched,
        "modified_count": modified,
        "compromised": (modified > 0 and attacker_tenant != real_owner),
        "explanation": explanation,
        "current_task_state": current_task
    })


@app.route("/api/rate-limit/test", methods=["POST"])
def api_test_rate_limit():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id", "tenant-acme")
    burst = int(data.get("burst", 12))
    limit = int(data.get("limit", 10))
    window = int(data.get("window", 60))

    results = []
    for i in range(burst):
        allowed, count, lim, win = db_check_rate_limit(tenant_id, limit, window)
        results.append({
            "request_num": i + 1,
            "status": "ALLOWED" if allowed else "RATE LIMITED",
            "allowed": allowed,
            "count": count,
            "limit": lim,
            "timestamp": time.time()
        })

    return jsonify({
        "tenant_id": tenant_id,
        "limit": limit,
        "window_secs": window,
        "total_requests": burst,
        "allowed_count": sum(1 for r in results if r["allowed"]),
        "blocked_count": sum(1 for r in results if not r["allowed"]),
        "log": results
    })


@app.route("/api/rate-limit/reset", methods=["POST"])
def api_reset_rate_limit():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id")
    db = get_db(SHARED_DB)
    if tenant_id:
        db[RATE_COLLECTION].delete_many({"tenant_id": tenant_id})
    else:
        db[RATE_COLLECTION].drop()
    return jsonify({"success": True, "message": f"Rate limit records cleared for {tenant_id or 'all tenants'}."})


@app.route("/api/migration/seed", methods=["POST"])
def api_seed_migration():
    count = seed_baseline()
    return jsonify({"success": True, "count": count, "message": f"Seeded {count} baseline documents in {SHARED_DB}.{SHARED_COLLECTION}."})


@app.route("/api/migration/dry-run", methods=["POST"])
def api_dry_run():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id", "tenant-acme")
    res = execute_migration(tenant_id, dry_run=True)
    return jsonify(res)


@app.route("/api/migration/execute", methods=["POST"])
def api_run_migration():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id", "tenant-acme")
    res = execute_migration(tenant_id, dry_run=False)
    return jsonify(res)


@app.route("/api/migration/idempotency-test", methods=["POST"])
def api_idempotency_test():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id", "tenant-acme")
    run1 = execute_migration(tenant_id, dry_run=False)
    run2 = execute_migration(tenant_id, dry_run=False)
    idempotent = (run1["target_count"] == run2["target_count"]) and (run1["target_checksum"] == run2["target_checksum"])
    return jsonify({
        "tenant_id": tenant_id,
        "idempotent": idempotent,
        "run1": run1,
        "run2": run2,
        "conclusion": "Migration is strictly idempotent: re-running upserts existing documents rather than inserting duplicates." if idempotent else "FAILED: Document count altered on re-run."
    })


@app.route("/api/migration/rollback", methods=["POST"])
def api_rollback():
    data = request.get_json() or {}
    tenant_id = data.get("tenant_id", "tenant-acme")
    res = rollback_database(tenant_id)
    return jsonify(res)


@app.route("/api/migration/data-view", methods=["GET"])
def api_data_view():
    tenant_id = request.args.get("tenant_id", "tenant-acme")
    client = get_client()

    # Shared collection docs
    shared_col = client[SHARED_DB][SHARED_COLLECTION]
    shared_docs = list(shared_col.find({"tenant_id": tenant_id}))
    for d in shared_docs:
        d["_id"] = str(d["_id"])

    # Dedicated DB docs
    target_database = tenant_db_name(tenant_id)
    dedicated_docs = []
    has_dedicated_db = target_database in client.list_database_names()
    if has_dedicated_db:
        dedicated_col = client[target_database][SHARED_COLLECTION]
        dedicated_docs = list(dedicated_col.find({}))
        for d in dedicated_docs:
            d["_id"] = str(d["_id"])

    # Checksums
    s_cs = content_checksum(list(shared_col.find({"tenant_id": tenant_id}, {"_id": 0}))) if shared_docs else "N/A"
    d_cs = content_checksum(list(client[target_database][SHARED_COLLECTION].find({}, {"_id": 0}))) if dedicated_docs else "N/A"

    return jsonify({
        "tenant_id": tenant_id,
        "shared_collection": {
            "database": SHARED_DB,
            "collection": SHARED_COLLECTION,
            "count": len(shared_docs),
            "checksum": s_cs,
            "documents": shared_docs
        },
        "dedicated_database": {
            "database": target_database,
            "collection": SHARED_COLLECTION,
            "exists": has_dedicated_db,
            "count": len(dedicated_docs),
            "checksum": d_cs,
            "documents": dedicated_docs
        },
        "in_sync": (len(shared_docs) == len(dedicated_docs) and s_cs == d_cs) if dedicated_docs else False
    })


# ── CLI Runner entrypoint ──────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Lab 15 Multi-Tenant & Migration Web App on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
