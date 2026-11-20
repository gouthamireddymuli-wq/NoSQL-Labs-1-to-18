"""
Lab 12.1: Authentication & Role-Based Access Control (RBAC) Setup & Verification
Demonstrates:
  1. Creation of least-privilege roles (analyticsReader, limitedWriter, hrRole)
  2. Creation of specific application users (admin, app_user_read, app_user_write, hr_manager, etc.)
  3. Strict enforcement verification: tests permitted vs unpermitted operations
  4. Integration with field-level redaction
"""

import os
import sys
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.connection import MONGO_URI, banner

# Default credential configuration for the lab
USERS_CONFIG = {
    "admin": {
        "pwd": "AdminSecurePassword123!",
        "roles": [
            {"role": "userAdminAnyDatabase", "db": "admin"},
            {"role": "clusterAdmin", "db": "admin"},
            {"role": "readWriteAnyDatabase", "db": "admin"}
        ],
        "description": "Full Cluster and User Administrator"
    },
    "app_user_read": {
        "pwd": "ReaderPassword123!",
        "roles": [
            {"role": "read", "db": "nosql_labs"},
            {"role": "analyticsReader", "db": "admin"}
        ],
        "description": "Read-Only Application Analyst (nosql_labs & analytics)"
    },
    "app_user_write": {
        "pwd": "WriterPassword123!",
        "roles": [
            {"role": "readWrite", "db": "nosql_labs"}
        ],
        "description": "Read-Write Application Service (nosql_labs only)"
    },
    "log_writer": {
        "pwd": "LogWriterPassword123!",
        "roles": [
            {"role": "limitedWriter", "db": "nosql_labs"}
        ],
        "description": "Custom Least-Privilege Role: insert/update on logs, read on nosql_labs"
    },
    "hr_manager": {
        "pwd": "HRManagerPassword123!",
        "roles": [
            {"role": "hrRole", "db": "nosql_labs"}
        ],
        "description": "HR Officer: Full access to sensitive employees collection"
    }
}


def setup_roles_and_users(base_uri=MONGO_URI):
    banner("Lab 12.1: Setting Up MongoDB Roles & RBAC Users")
    client = MongoClient(base_uri, serverSelectionTimeoutMS=5000)
    admin_db = client["admin"]
    labs_db = client["nosql_labs"]

    results = []

    # 1. Custom Role: analyticsReader (on admin db for analytics db)
    # Note: In MongoDB, the 'find' action authorizes both find and aggregate operations.
    try:
        admin_db.command(
            "createRole",
            "analyticsReader",
            privileges=[
                {
                    "resource": {"db": "analytics", "collection": ""},
                    "actions": ["find"]
                }
            ],
            roles=[]
        )
        print("[OK] Created Role: 'analyticsReader' (admin DB)")
        results.append({"role": "analyticsReader", "status": "Created", "db": "admin"})
    except OperationFailure as e:
        if "already exists" in str(e):
            print("[*] Role 'analyticsReader' already exists, updating...")
            admin_db.command(
                "updateRole",
                "analyticsReader",
                privileges=[
                    {
                        "resource": {"db": "analytics", "collection": ""},
                        "actions": ["find"]
                    }
                ],
                roles=[]
            )
            results.append({"role": "analyticsReader", "status": "Updated", "db": "admin"})
        else:
            print(f"[!] Role creation error: {e}")

    # 2. Custom Role: limitedWriter (on nosql_labs)
    try:
        labs_db.command(
            "createRole",
            "limitedWriter",
            privileges=[
                {"resource": {"db": "nosql_labs", "collection": "logs"}, "actions": ["find", "insert", "update"]},
                {"resource": {"db": "nosql_labs", "collection": ""}, "actions": ["find"]}
            ],
            roles=[]
        )
        print("[OK] Created Role: 'limitedWriter' (nosql_labs DB)")
        results.append({"role": "limitedWriter", "status": "Created", "db": "nosql_labs"})
    except OperationFailure as e:
        if "already exists" in str(e):
            print("[*] Role 'limitedWriter' already exists, updating...")
            labs_db.command(
                "updateRole",
                "limitedWriter",
                privileges=[
                    {"resource": {"db": "nosql_labs", "collection": "logs"}, "actions": ["find", "insert", "update"]},
                    {"resource": {"db": "nosql_labs", "collection": ""}, "actions": ["find"]}
                ],
                roles=[]
            )
            results.append({"role": "limitedWriter", "status": "Updated", "db": "nosql_labs"})
        else:
            print(f"[!] Role creation error: {e}")

    # 3. Custom Role: hrRole (on nosql_labs)
    try:
        labs_db.command(
            "createRole",
            "hrRole",
            privileges=[
                {"resource": {"db": "nosql_labs", "collection": "employees"}, "actions": ["find", "insert", "update", "remove"]},
                {"resource": {"db": "nosql_labs", "collection": "employees_safe"}, "actions": ["find"]}
            ],
            roles=[]
        )
        print("[OK] Created Role: 'hrRole' (nosql_labs DB)")
        results.append({"role": "hrRole", "status": "Created", "db": "nosql_labs"})
    except OperationFailure as e:
        if "already exists" in str(e):
            print("[*] Role 'hrRole' already exists, updating...")
            labs_db.command(
                "updateRole",
                "hrRole",
                privileges=[
                    {"resource": {"db": "nosql_labs", "collection": "employees"}, "actions": ["find", "insert", "update", "remove"]},
                    {"resource": {"db": "nosql_labs", "collection": "employees_safe"}, "actions": ["find"]}
                ],
                roles=[]
            )
            results.append({"role": "hrRole", "status": "Updated", "db": "nosql_labs"})
        else:
            print(f"[!] Role creation error: {e}")

    # 4. Create Users
    user_results = []
    for username, udata in USERS_CONFIG.items():
        auth_db = admin_db if username in ["admin", "app_user_read"] else labs_db
        try:
            auth_db.command(
                "createUser",
                username,
                pwd=udata["pwd"],
                roles=udata["roles"]
            )
            print(f"[OK] Created User: '{username}' ({udata['description']})")
            user_results.append({"user": username, "status": "Created", "roles": udata["roles"]})
        except OperationFailure as e:
            if "already exists" in str(e):
                auth_db.command(
                    "updateUser",
                    username,
                    pwd=udata["pwd"],
                    roles=udata["roles"]
                )
                print(f"[*] Updated User: '{username}'")
                user_results.append({"user": username, "status": "Updated", "roles": udata["roles"]})
            else:
                print(f"[!] Error with user '{username}': {e}")
                user_results.append({"user": username, "status": f"Error: {e}", "roles": udata["roles"]})

    return {"roles": results, "users": user_results}


def run_rbac_test_matrix(base_host=None, base_port=27017):
    # Derive host from MONGO_URI if not explicitly supplied
    if base_host is None:
        import urllib.parse as _up
        _p = _up.urlparse(MONGO_URI.replace("mongodb://", "http://"))
        base_host = _p.hostname or "localhost"
        if _p.port:
            base_port = _p.port
    """
    Simulates / tests operations across users and verifies authorization enforcement.
    """
    banner("Testing RBAC Permission Enforcement Matrix")

    test_matrix = [
        {
            "test_id": "TEST-01",
            "user": "app_user_read",
            "auth_db": "admin",
            "action": "READ",
            "target": "nosql_labs.orders",
            "op": lambda db: list(db.orders.find().limit(1)),
            "expected": "PASS",
            "rule": "Role 'read' on 'nosql_labs' permits find queries"
        },
        {
            "test_id": "TEST-02",
            "user": "app_user_read",
            "auth_db": "admin",
            "action": "WRITE",
            "target": "nosql_labs.orders",
            "op": lambda db: db.orders.insert_one({"item": "unauthorized_write", "val": 99}),
            "expected": "REJECTED",
            "rule": "Role 'read' strictly prohibits insert operations"
        },
        {
            "test_id": "TEST-03",
            "user": "app_user_write",
            "auth_db": "nosql_labs",
            "action": "WRITE",
            "target": "nosql_labs.orders",
            "op": lambda db: db.orders.insert_one({"item": "authorized_write", "qty": 10, "status": "active"}),
            "expected": "PASS",
            "rule": "Role 'readWrite' on 'nosql_labs' permits inserts"
        },
        {
            "test_id": "TEST-04",
            "user": "app_user_write",
            "auth_db": "nosql_labs",
            "action": "CROSS-DB READ",
            "target": "bookstore.inventory",
            "op": lambda db: list(db.client.bookstore.inventory.find().limit(1)),
            "expected": "REJECTED",
            "rule": "No privileges granted on foreign database 'bookstore'"
        },
        {
            "test_id": "TEST-05",
            "user": "log_writer",
            "auth_db": "nosql_labs",
            "action": "WRITE TO LOGS",
            "target": "nosql_labs.logs",
            "op": lambda db: db.logs.insert_one({"level": "INFO", "msg": "Audit log entry"}),
            "expected": "PASS",
            "rule": "Custom 'limitedWriter' grants insert on 'logs'"
        },
        {
            "test_id": "TEST-06",
            "user": "log_writer",
            "auth_db": "nosql_labs",
            "action": "WRITE TO ORDERS",
            "target": "nosql_labs.orders",
            "op": lambda db: db.orders.insert_one({"hacked": True}),
            "expected": "REJECTED",
            "rule": "Custom 'limitedWriter' permits read-only on non-log collections"
        },
        {
            "test_id": "TEST-07",
            "user": "admin",
            "auth_db": "admin",
            "action": "ADMIN SERVER STATUS",
            "target": "admin.serverStatus",
            "op": lambda db: db.client.admin.command("serverStatus")["ok"],
            "expected": "PASS",
            "rule": "Role 'clusterAdmin' allows cluster-wide management"
        }
    ]

    results = []

    for t in test_matrix:
        user = t["user"]
        pwd = USERS_CONFIG[user]["pwd"]
        auth_db = t["auth_db"]
        uri = f"mongodb://{user}:{pwd}@{base_host}:{base_port}/?authSource={auth_db}"

        client = None
        status = "UNKNOWN"
        error_msg = ""
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            target_db = client["nosql_labs"]
            t["op"](target_db)
            status = "PASS"
        except OperationFailure as e:
            if "not authorized" in str(e).lower() or "unauthorized" in str(e).lower() or 13 == e.code:
                status = "REJECTED"
                error_msg = f"MongoServerError[13]: {e.details.get('errmsg', str(e))[:70]}"
            else:
                status = "ERROR"
                error_msg = str(e)[:70]
        except PyMongoError as e:
            status = "ERROR"
            error_msg = str(e)[:70]
        finally:
            if client:
                client.close()

        match = (status == t["expected"])
        result_entry = {
            "test_id": t["test_id"],
            "user": user,
            "action": t["action"],
            "target": t["target"],
            "expected": t["expected"],
            "actual": status,
            "error_msg": error_msg,
            "rule": t["rule"],
            "success": match
        }
        results.append(result_entry)

        res_tag = "[PASS - ENFORCED]" if match else f"[{status}]"
        print(f"  {t['test_id']} | User: {user:<14} | Action: {t['action']:<18} | "
              f"Exp: {t['expected']:<8} | Act: {status:<8} -> {res_tag}")
        if error_msg:
            print(f"      Details: {error_msg}")

    print("=" * 65)
    return results


if __name__ == "__main__":
    setup_roles_and_users()
    run_rbac_test_matrix()
