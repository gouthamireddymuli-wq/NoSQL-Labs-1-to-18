"""Flask Web Application for NoSQL Lab 14: Monitoring, Backup & Restore.
Author: M Gouthami (24BTRCL130)

Features:
  - Lab 14.1: Live MongoDB Monitoring Dashboard (serverStatus metrics, WiredTiger cache, op counters)
  - Lab 14.2: Automated Backup & Restore Verification (mongodump/mongorestore + count+checksum verification)
  - Real-time metrics polling via SSE / JSON API
  - Threshold alert system with configurable limits
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import shutil
import threading
import logging
import re
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
sys.path.insert(0, _root)

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

app = Flask(__name__)

# ── Logging setup ──────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(_root, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "metrics.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

BACKUP_ROOT = os.path.join(_root, "backups")
os.makedirs(BACKUP_ROOT, exist_ok=True)

# ── MongoDB connection ─────────────────────────────────────────────────────────
MONGO_URI_RS = os.getenv(
    "MONGO_URI",
    "mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin"
)
MONGO_URI_LOCAL = os.getenv("MONGO_URI_STANDALONE", "mongodb://localhost:27017")

DB_NAME = "nosql_labs"
COLLECTION = "backup_demo"

SEED_DOCS = [
    {"order_id": f"ORD-{i:04d}", "customer": f"cust-{i % 20}", "amount": round(10 + i * 3.37, 2)}
    for i in range(500)
]

# ── Backup job state (global, thread-safe enough for a demo) ───────────────────
_backup_log: list[str] = []
_backup_running = False
_backup_result: dict | None = None


def get_mongo_client():
    """Try replica-set URI first, fall back to standalone."""
    for uri in [MONGO_URI_RS, MONGO_URI_LOCAL]:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2500)
            client.admin.command("ping")
            return client
        except Exception:
            continue
    return None


# ══════════════════════════════════════════════════════════════════════════════
# LAB 14.1 – MONITORING DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def _collect_metrics(client) -> dict:
    status = client.admin.command("serverStatus")
    wt = status.get("wiredTiger", {}).get("cache", {})
    connections = status.get("connections", {})
    opcounters = status.get("opcounters", {})
    cache_bytes = wt.get("bytes currently in the cache", 0)
    cache_max = wt.get("maximum bytes configured", 1)
    cache_dirty = wt.get("tracked dirty bytes in the cache", 0)
    cache_pct = round((cache_bytes / cache_max) * 100, 2) if cache_max > 0 else 0

    # Replication lag (best-effort)
    repl_lag_ms = None
    try:
        repl_status = client.admin.command("replSetGetStatus")
        primary_optime = None
        for m in repl_status.get("members", []):
            if m.get("stateStr") == "PRIMARY":
                primary_optime = m.get("optimeDate")
        for m in repl_status.get("members", []):
            if m.get("stateStr") == "SECONDARY" and primary_optime:
                sec_optime = m.get("optimeDate")
                if sec_optime and primary_optime:
                    repl_lag_ms = int((primary_optime - sec_optime).total_seconds() * 1000)
    except Exception:
        pass

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "connections_current": connections.get("current", 0),
        "connections_available": connections.get("available", 0),
        "connections_total_created": connections.get("totalCreated", 0),
        "op_insert": opcounters.get("insert", 0),
        "op_query": opcounters.get("query", 0),
        "op_update": opcounters.get("update", 0),
        "op_delete": opcounters.get("delete", 0),
        "op_getmore": opcounters.get("getmore", 0),
        "op_command": opcounters.get("command", 0),
        "cache_bytes_in_use": cache_bytes,
        "cache_max_bytes": cache_max,
        "cache_dirty_bytes": cache_dirty,
        "cache_pct": cache_pct,
        "pages_read_into_cache": wt.get("pages read into cache", 0),
        "repl_lag_ms": repl_lag_ms,
        "uptime_seconds": status.get("uptime", 0),
        "version": status.get("version", "unknown"),
        "host": status.get("host", "unknown"),
    }

    # Threshold alerts
    alerts = []
    if cache_pct > 80:
        alerts.append(f"Cache usage {cache_pct:.1f}% exceeds 80% threshold")
    conn_total = connections.get("current", 0) + connections.get("available", 1)
    if conn_total > 0 and connections.get("current", 0) / conn_total > 0.8:
        alerts.append(f"Connections near limit: {connections.get('current')}/{conn_total}")
    if repl_lag_ms is not None and repl_lag_ms > 10000:
        alerts.append(f"Replication lag {repl_lag_ms}ms exceeds 10s threshold")

    metrics["alerts"] = alerts
    return metrics


@app.route("/api/metrics")
def api_metrics():
    client = get_mongo_client()
    if not client:
        return jsonify({"error": "Cannot connect to MongoDB"}), 503
    try:
        m = _collect_metrics(client)
        logging.info(json.dumps({k: v for k, v in m.items() if k != "alerts"}))
        return jsonify(m)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()


@app.route("/api/metrics/stream")
def api_metrics_stream():
    """Server-Sent Events stream: pushes a fresh metrics snapshot every 3 s."""
    def generate():
        for _ in range(20):  # 20 iterations × 3 s = 60 s max
            client = get_mongo_client()
            if client:
                try:
                    m = _collect_metrics(client)
                    logging.info(json.dumps({k: v for k, v in m.items() if k != "alerts"}))
                    yield f"data: {json.dumps(m)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                finally:
                    client.close()
            else:
                yield f"data: {json.dumps({'error': 'No MongoDB connection'})}\n\n"
            time.sleep(3)
        yield "data: {\"done\": true}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ══════════════════════════════════════════════════════════════════════════════
# LAB 14.2 – BACKUP & RESTORE
# ══════════════════════════════════════════════════════════════════════════════

def _tools_available() -> bool:
    return shutil.which("mongodump") is not None and shutil.which("mongorestore") is not None


def _checksum_collection(col) -> str:
    rows = []
    for doc in col.find({}, {"_id": 0}).sort([("order_id", 1)]):
        rows.append(json.dumps(doc, sort_keys=True))
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def _run_backup_job(mongo_uri: str):
    global _backup_running, _backup_result, _backup_log
    _backup_log = []
    _backup_running = True
    _backup_result = None

    def log(msg):
        _backup_log.append(msg)
        print(msg)

    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = os.path.join(BACKUP_ROOT, timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        tools_uri = re.sub(r'(\d+)/[a-zA-Z0-9_-]+(\?|$)', r'\1/\2', mongo_uri)

        # Step 1 – Seed
        log("=== Step 1: Seed collection and record baseline checksum ===")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        db[COLLECTION].drop()
        col = db[COLLECTION]
        col.insert_many(SEED_DOCS)
        original_count = col.count_documents({})
        original_checksum = _checksum_collection(col)
        log(f"  [OK] Seeded {original_count} documents.")
        log(f"  Baseline checksum: {original_checksum[:16]}...")

        # Step 2 – Dump
        log(f"\n=== Step 2: Backup to {backup_dir} ===")
        t_dump_start = time.time()
        dump_result = subprocess.run(
            ["mongodump", f"--uri={tools_uri}", f"--db={DB_NAME}",
             f"--collection={COLLECTION}", f"--out={backup_dir}"],
            capture_output=True, text=True
        )
        dump_elapsed = round(time.time() - t_dump_start, 2)
        if dump_result.returncode != 0:
            log(f"  [ERROR] mongodump failed: {dump_result.stderr[-400:]}")
            _backup_result = {"success": False, "error": "mongodump failed", "log": _backup_log.copy()}
            return
        log(f"  [OK] Backup complete in {dump_elapsed}s.")

        # Step 3 – Simulate data loss
        log("\n=== Step 3: Simulate data loss (drop the collection) ===")
        col.drop()
        log(f"  [OK] Collection dropped. Count now: {db[COLLECTION].count_documents({})}")

        # Step 4 – Restore
        log("\n=== Step 4: Restore with mongorestore ===")
        t_restore_start = time.time()
        restore_result = subprocess.run(
            ["mongorestore", f"--uri={tools_uri}",
             f"--nsInclude={DB_NAME}.{COLLECTION}", backup_dir],
            capture_output=True, text=True
        )
        restore_elapsed = round(time.time() - t_restore_start, 2)
        if restore_result.returncode != 0:
            log(f"  [ERROR] mongorestore failed: {restore_result.stderr[-400:]}")
            _backup_result = {"success": False, "error": "mongorestore failed", "log": _backup_log.copy()}
            return
        log(f"  [OK] Restore complete in {restore_elapsed}s.")

        # Step 5 – Verify
        log("\n=== Step 5: Verify restore integrity ===")
        restored_col = db[COLLECTION]
        restored_count = restored_col.count_documents({})
        restored_checksum = _checksum_collection(restored_col)
        count_ok = restored_count == original_count
        checksum_ok = restored_checksum == original_checksum

        log(f"  Document count:  original={original_count}  restored={restored_count}  {'[OK]' if count_ok else '[MISMATCH]'}")
        log(f"  Content checksum: {'MATCH' if checksum_ok else 'MISMATCH'} ({restored_checksum[:16]}...)")

        if count_ok and checksum_ok:
            log("\n  [OK] Restore verified: document count AND content checksum match.")
        else:
            log("\n  [FAIL] Restore does NOT match the original.")

        client.close()

        _backup_result = {
            "success": count_ok and checksum_ok,
            "original_count": original_count,
            "restored_count": restored_count,
            "count_ok": count_ok,
            "checksum_ok": checksum_ok,
            "original_checksum": original_checksum[:16] + "...",
            "restored_checksum": restored_checksum[:16] + "...",
            "dump_elapsed_s": dump_elapsed,
            "restore_elapsed_s": restore_elapsed,
            "backup_dir": backup_dir,
            "timestamp": timestamp,
            "log": _backup_log.copy(),
        }
    except Exception as ex:
        _backup_log.append(f"[ERROR] {ex}")
        _backup_result = {"success": False, "error": str(ex), "log": _backup_log.copy()}
    finally:
        _backup_running = False


@app.route("/api/backup/start", methods=["POST"])
def api_backup_start():
    global _backup_running
    if _backup_running:
        return jsonify({"error": "Backup already running"}), 409
    if not _tools_available():
        return jsonify({"error": "mongodump/mongorestore not found on PATH"}), 500

    client = get_mongo_client()
    if not client:
        return jsonify({"error": "Cannot connect to MongoDB"}), 503
    # Determine which URI actually worked
    uri_to_use = MONGO_URI_LOCAL
    for uri in [MONGO_URI_RS, MONGO_URI_LOCAL]:
        try:
            MongoClient(uri, serverSelectionTimeoutMS=2500).admin.command("ping")
            uri_to_use = uri
            break
        except Exception:
            continue
    client.close()

    t = threading.Thread(target=_run_backup_job, args=(uri_to_use,), daemon=True)
    t.start()
    return jsonify({"started": True})


@app.route("/api/backup/status")
def api_backup_status():
    return jsonify({
        "running": _backup_running,
        "result": _backup_result,
        "log": _backup_log.copy(),
    })


@app.route("/api/backup/logs")
def api_backup_logs():
    """Return recent backup log entries from the logs directory."""
    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        entries = lines[-50:]  # last 50 lines
    return jsonify({"lines": [l.rstrip() for l in entries]})


# ══════════════════════════════════════════════════════════════════════════════
# GENERAL ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    client = get_mongo_client()
    connected = client is not None
    version = "unknown"
    host = "unknown"
    if client:
        try:
            status = client.admin.command("serverStatus")
            version = status.get("version", "unknown")
            host = status.get("host", "unknown")
        except Exception:
            pass
        client.close()
    tools_ok = _tools_available()
    return render_template("index.html",
                           connected=connected,
                           version=version,
                           host=host,
                           tools_ok=tools_ok,
                           now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


@app.route("/lab1")
def lab1():
    return render_template("lab1.html")


@app.route("/lab2")
def lab2():
    return render_template("lab2.html", tools_ok=_tools_available())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
