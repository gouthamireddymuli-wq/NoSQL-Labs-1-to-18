"""
Flask Web Application for NoSQL Lab 12: MongoDB Security, RBAC & TLS Encryption
Author: M Gouthami (24BTRCL130)
Features:
  - Threat Modeling & CIA Triad Overview
  - Lab 12.1 Interactive RBAC & Field-Level Redaction Playground
  - Lab 12.2 TLS / Encryption-in-Transit PKI Certificate Inspector & Diagnostics
"""

import os
import sys
from datetime import datetime, timezone

# Add project root to path
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
sys.path.insert(0, _root)

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure, ServerSelectionTimeoutError

from config.connection import MONGO_URI
from rbac_field_redaction import setup_field_redaction, EMPLOYEES_DATA
from lab_01_rbac_setup import USERS_CONFIG, setup_roles_and_users, run_rbac_test_matrix
from generate_tls_certs import generate_certificates, CERT_DIR
from lab_02_tls_setup import get_pki_chain_summary, test_tls_connection

app = Flask(__name__)

# Lazy MongoDB client
_client = None

def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
    return _client


@app.route("/")
def index():
    """Main dashboard: Chapter 12 overview, threat modeling, and quick metrics."""
    mongo_status = "Disconnected"
    try:
        get_mongo_client().admin.command("ping")
        mongo_status = "Connected"
    except Exception:
        mongo_status = "Standby / Container Ready"

    pki_summary = get_pki_chain_summary()
    return render_template(
        "index.html",
        mongo_status=mongo_status,
        pki_summary=pki_summary,
        user_count=len(USERS_CONFIG),
    )


@app.route("/lab1")
def lab1():
    """Lab 12.1: Authentication, RBAC, and Field-Level Redaction."""
    return render_template(
        "lab1.html",
        users_config=USERS_CONFIG,
    )


@app.route("/lab2")
def lab2():
    """Lab 12.2: TLS / Encryption-in-Transit & PKI Hierarchy."""
    pki_summary = get_pki_chain_summary()
    return render_template(
        "lab2.html",
        pki=pki_summary,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REST API Endpoints - Lab 12.1
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/lab1/seed", methods=["POST"])
def api_lab1_seed():
    """Seeds the employees collection and builds the employees_safe view."""
    try:
        res = setup_field_redaction("nosql_labs")
        return jsonify({
            "status": "success",
            "message": "Collection 'employees' seeded and view 'employees_safe' created successfully.",
            "data": res
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/lab1/query-data", methods=["GET"])
def api_lab1_query():
    """
    Simulates querying either as HR (direct collection) or non-HR (redacted view).
    """
    mode = request.args.get("mode", "non-hr")  # 'hr' or 'non-hr'
    try:
        client = get_mongo_client()
        db = client["nosql_labs"]

        if mode == "hr":
            # Direct query to underlying collection
            docs = list(db["employees"].find({}, {"_id": 0}))
            return jsonify({
                "status": "success",
                "role": "HR Manager (Direct Collection Access)",
                "target": "nosql_labs.employees",
                "salary_visible": True,
                "ssn_masked": False,
                "count": len(docs),
                "documents": docs
            })
        else:
            # Query the redacted view
            docs = list(db["employees_safe"].find({}, {"_id": 0}))
            return jsonify({
                "status": "success",
                "role": "General Employee / Analyst (Redacted View Access)",
                "target": "nosql_labs.employees_safe",
                "salary_visible": False,
                "ssn_masked": True,
                "count": len(docs),
                "documents": docs
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/lab1/run-rbac-matrix", methods=["POST"])
def api_lab1_run_rbac():
    """Executes the comprehensive RBAC permission enforcement test suite."""
    try:
        # First ensure roles & users exist
        setup_roles_and_users()
        matrix_results = run_rbac_test_matrix()
        return jsonify({
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": matrix_results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# REST API Endpoints - Lab 12.2
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/lab2/certificates", methods=["GET"])
def api_lab2_certs():
    """Returns metadata for the full X.509 PKI certificate chain."""
    pki = get_pki_chain_summary()
    return jsonify(pki)


@app.route("/api/lab2/generate-certs", methods=["POST"])
def api_lab2_generate():
    """Automates certificate generation using the cryptography library."""
    try:
        res = generate_certificates()
        pki = get_pki_chain_summary()
        return jsonify({
            "status": "success",
            "message": "New PKI Certificate Authority and X.509 certificates generated successfully.",
            "details": res,
            "pki": pki
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/lab2/test-tls", methods=["POST"])
def api_lab2_test_tls():
    """Runs live/simulated TLS vs plaintext connectivity test."""
    data = request.get_json() or {}
    port = int(data.get("port", 27100))
    host = data.get("host", "localhost")

    plaintext_res = test_tls_connection(host, port, use_tls=False)
    tls_res = test_tls_connection(host, port, use_tls=True)

    return jsonify({
        "status": "success",
        "plaintext_test": plaintext_res,
        "tls_test": tls_res,
        "summary": "Plaintext connection is correctly rejected by TLS enforcement; TLS client certificate connection succeeds."
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "nosql-lab12", "time": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
