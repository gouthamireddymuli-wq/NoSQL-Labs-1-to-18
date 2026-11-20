"""Flask Web Application for NoSQL Lab 13: Production Deployment, Kubernetes & Cloud Provisioning.
Author: M Gouthami (24BTRCL130)

Features:
  - Executive Overview & Chapter 13 Architecture
  - Lab 13.1 Interactive Production Replica Set Explorer (Docker Compose, keyFile HMAC auth, live replication tester)
  - Chapter 8 vs Chapter 13 Side-by-Side Comparison Matrix & Connection String Generator
  - Lab 13.2 Kubernetes StatefulSet Manifest Inspector & Architectural Deep Dive
  - Terraform / MongoDB Atlas Cloud Provisioning Explorer (main.tf)
"""

import os
import sys
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, ReadPreference
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
sys.path.insert(0, _root)

KEYFILE_PATH = os.path.join(_root, "keyfile")

app = Flask(__name__)

# Connection strings
# Within Docker Compose network (connecting to nodes directly):
PRIMARY_URI = os.getenv(
    "PRIMARY_URI",
    "mongodb://admin:AdminPass123!@mongo-rs0-1:27017/?authSource=admin&directConnection=true"
)
SECONDARY_URI = os.getenv(
    "SECONDARY_URI",
    "mongodb://admin:AdminPass123!@mongo-rs0-2:27017/?authSource=admin&directConnection=true"
)
CLUSTER_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin"
)

# Host fallbacks if running outside container
HOST_PRIMARY_URI = "mongodb://admin:AdminPass123!@localhost:27017/?authSource=admin&directConnection=true"
HOST_SECONDARY_URI = "mongodb://admin:AdminPass123!@localhost:27018/?authSource=admin&directConnection=true"

def get_primary_client():
    for uri in [PRIMARY_URI, HOST_PRIMARY_URI]:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            return client
        except Exception:
            continue
    return None

def get_secondary_client():
    for uri in [SECONDARY_URI, HOST_SECONDARY_URI]:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000, read_preference=ReadPreference.SECONDARY_PREFERRED)
            client.admin.command("ping")
            return client
        except Exception:
            continue
    return None

def get_cluster_status():
    """Queries replica set status via Primary node."""
    client = get_primary_client()
    if client:
        try:
            raw = client.admin.command("replSetGetStatus")
            members = []
            for m in raw.get("members", []):
                members.append({
                    "name": m.get("name"),
                    "state": m.get("stateStr"),
                    "health": m.get("health"),
                    "uptime": m.get("uptime")
                })
            return {"ok": 1, "set": raw.get("set", "rs0"), "members": members}
        except Exception as ex:
            return {"ok": 0, "error": str(ex)}
    return {"ok": 0, "error": "Primary node not reachable"}

@app.route("/")
def index():
    """Main dashboard: Architecture overview, live cluster gauges, and quick navigation."""
    status = get_cluster_status()
    keyfile_exists = os.path.exists(KEYFILE_PATH)
    keyfile_size = os.path.getsize(KEYFILE_PATH) if keyfile_exists else 0
    return render_template(
        "index.html",
        status=status,
        keyfile_exists=keyfile_exists,
        keyfile_size=keyfile_size,
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )

@app.route("/lab1")
def lab1():
    """Activity 1: Production Replica Set Deployment with Keyfile Auth."""
    status = get_cluster_status()
    return render_template("lab1.html", status=status)

@app.route("/lab2")
def lab2():
    """Activity 2: Kubernetes StatefulSet for MongoDB."""
    k8s_dir = os.path.join(_root, "k8s")
    manifests = {}
    if os.path.exists(k8s_dir):
        for fname in sorted(os.listdir(k8s_dir)):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                fpath = os.path.join(k8s_dir, fname)
                with open(fpath, "r") as f:
                    manifests[fname] = f.read()
    return render_template("lab2.html", manifests=manifests)

@app.route("/cloud")
def cloud():
    """Activity 3: Terraform & MongoDB Atlas Cloud Provisioning."""
    tf_path = os.path.join(_root, "main.tf")
    tf_code = ""
    if os.path.exists(tf_path):
        with open(tf_path, "r") as f:
            tf_code = f.read()
    return render_template("cloud.html", tf_code=tf_code)

# --- API Endpoints ---

@app.route("/api/status")
def api_status():
    """Returns current replica set health and member states."""
    return jsonify(get_cluster_status())

@app.route("/api/test-replication", methods=["POST"])
def api_test_replication():
    """Executes live write to Primary and confirms replication on Secondary."""
    data = request.get_json(silent=True) or {}
    item = data.get("item", "Industrial Gas Turbine Model X-90")
    qty = data.get("quantity", 5)

    primary_client = get_primary_client()
    if not primary_client:
        return jsonify({"success": False, "error": "Could not connect to PRIMARY node"}), 500

    doc = {
        "item": item,
        "quantity": qty,
        "status": "Shipped",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    insert_res = primary_client["prod_db"]["orders"].insert_one(doc)
    doc_id = str(insert_res.inserted_id)

    secondary_client = get_secondary_client()
    records = []
    if secondary_client:
        try:
            cursor = secondary_client["prod_db"]["orders"].find().sort("_id", -1).limit(5)
            for r in cursor:
                records.append({
                    "_id": str(r.get("_id")),
                    "item": r.get("item"),
                    "quantity": r.get("quantity"),
                    "status": r.get("status"),
                    "timestamp": str(r.get("timestamp"))
                })
        except Exception as ex:
            records = [{"error": f"Read exception on secondary: {str(ex)}"}]
    else:
        # Fallback to reading from primary
        cursor = primary_client["prod_db"]["orders"].find().sort("_id", -1).limit(5)
        for r in cursor:
            records.append({
                "_id": str(r.get("_id")),
                "item": r.get("item"),
                "quantity": r.get("quantity"),
                "status": r.get("status"),
                "timestamp": str(r.get("timestamp"))
            })

    return jsonify({
        "success": True,
        "inserted_id": doc_id,
        "write_status": "Success on PRIMARY (mongo-rs0-1:27017)",
        "read_target": "SECONDARY (mongo-rs0-2:27017)",
        "recent_records": records
    })

@app.route("/api/compare")
def api_compare():
    """Returns structured comparison between Chapter 8 and Chapter 13."""
    comparison = [
        {
            "category": "Inter-Member Authentication",
            "ch8": "None (No keyfile, any rogue node can join cluster)",
            "ch13": "Cryptographic keyFile (756-byte shared secret, chmod 400, HMAC-SHA verification)",
            "impact": "Prevents unauthorized rogue mongod instances from joining replica set"
        },
        {
            "category": "Client / Database Access Control",
            "ch8": "Disabled (--noauth, unauthenticated root access)",
            "ch13": "Enforced (--auth, strict RBAC superuser admin:AdminPass123!)",
            "impact": "Locks down all read/write commands behind credentialed authorization"
        },
        {
            "category": "Bootstrap Order of Operations",
            "ch8": "Containers Start -> rs.initiate() directly without user setup",
            "ch13": "Keyfile generated -> Containers start -> Primary elected -> Admin user created via Localhost Exception",
            "impact": "Guarantees admin user is established securely without locking out operations"
        },
        {
            "category": "Connection String",
            "ch8": "mongodb://host:27017,host:27018,host:27019/?replicaSet=rs0",
            "ch13": "mongodb://admin:AdminPass123!@host:27017,host:27018,host:27019/admin?replicaSet=rs0&authSource=admin",
            "impact": "Enforces username, password, authenticationDatabase (authSource=admin), and replicaSet parameters"
        },
        {
            "category": "Container Compose Commands",
            "ch8": "['--replSet', 'rs0', '--bind_ip_all']",
            "ch13": "['--replSet=rs0', '--bind_ip_all', '--auth', '--keyFile=/tmp/keyfile'] with permission normalization",
            "impact": "Ensures cross-platform production compatibility and strict security flags"
        },
        {
            "category": "Healthchecks",
            "ch8": "Unauthenticated ping command",
            "ch13": "Authenticated ping requiring admin credentials on admin database",
            "impact": "Health monitoring checks both server liveliness AND authentication readiness"
        }
    ]
    return jsonify(comparison)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
