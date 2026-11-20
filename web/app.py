"""Flask Web Application for NoSQL Lab 18: Comparative Capstone Lab.
Author: M Gouthami (24BTRCL130)

Features:
  - Activity 1: Comparative Capstone Lab (Synthetic Transaction Generation, 4 Benchmark Queries, Latency Timing)
  - Activity 2: Comparative Analysis Technical Report (Live MongoDB Benchmark + Architectural Estimates)
  - Fraud Ring & Device Sharing Explorer (Simulated Neo4j Graph Traversal vs MongoDB)
  - Polyglot Architecture Dashboard & Database Scorecard (MongoDB vs Cassandra vs Neo4j)
  - Interactive Benchmark Runner, REST APIs, and PDF Report Exporter
"""

import os
import sys
import time
import glob
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config.connection import get_client, get_db, reset_collection
import lab_01_comparative_capstone as lab01
import lab_02_comparative_report as lab02

app = Flask(__name__)
CORS(app)

DB_NAME = "capstone"
TXN_COLLECTION = "transactions"
REPORTS_DIR = os.path.join(_root, "reports")


def get_collection():
    db = get_db(DB_NAME)
    return db[TXN_COLLECTION]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/benchmark")
def benchmark_page():
    return render_template("benchmark.html")


@app.route("/report")
def report_page():
    return render_template("report.html")


@app.route("/fraud-rings")
def fraud_rings_page():
    return render_template("fraud_rings.html")


# ---------------------------------------------------------
# REST APIs
# ---------------------------------------------------------

@app.route("/api/health")
def api_health():
    try:
        client = get_client()
        ping_res = client.admin.command("ping")
        return jsonify({
            "status": "healthy",
            "mongodb": "connected",
            "ping": ping_res,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "mongodb": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


@app.route("/api/stats")
def api_stats():
    try:
        col = get_collection()
        total_txns = col.count_documents({})
        fraud_txns = col.count_documents({"is_fraud": True})
        high_risk = col.count_documents({"risk_score": {"$gt": 0.8}})
        
        avg_risk = 0.0
        categories_count = 0
        if total_txns > 0:
            agg_risk = list(col.aggregate([
                {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
            ]))
            if agg_risk:
                avg_risk = round(agg_risk[0]["avg_risk"], 4)
            categories_count = len(col.distinct("category"))

        indexes = list(col.index_information().keys()) if total_txns > 0 else []

        return jsonify({
            "success": True,
            "total_transactions": total_txns,
            "fraud_count": fraud_txns,
            "high_risk_count": high_risk,
            "avg_risk_score": avg_risk,
            "categories_count": categories_count,
            "indexes": indexes,
            "database": DB_NAME,
            "collection": TXN_COLLECTION
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lab1/generate", methods=["POST"])
def api_generate_data():
    try:
        data = request.get_json() or {}
        num_records = int(data.get("count", 10000))
        num_fraud = int(data.get("fraud_pct", 200))
        
        col = reset_collection(DB_NAME, TXN_COLLECTION)
        
        start_gen = time.perf_counter()
        txns = lab01.generate_transactions(n=num_records, fraud_pct=num_fraud)
        gen_time = time.perf_counter() - start_gen

        start_insert = time.perf_counter()
        col.insert_many(txns)
        insert_time = time.perf_counter() - start_insert

        # Automatically create indexes for fair benchmarks
        start_idx = time.perf_counter()
        col.create_index([("user_id", 1), ("timestamp", -1)], name="idx_user_time")
        col.create_index([("risk_score", -1)], name="idx_risk")
        col.create_index([("category", 1)], name="idx_category")
        idx_time = time.perf_counter() - start_idx

        return jsonify({
            "success": True,
            "message": f"Successfully generated and indexed {num_records:,} transactions",
            "total_records": num_records,
            "fraud_records": num_fraud,
            "generation_time_ms": round(gen_time * 1000, 2),
            "insert_time_ms": round(insert_time * 1000, 2),
            "index_time_ms": round(idx_time * 1000, 2),
            "throughput_docs_per_sec": round(num_records / insert_time, 0) if insert_time > 0 else 0
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lab1/benchmark", methods=["POST"])
def api_run_benchmark():
    try:
        col = get_collection()
        doc_count = col.count_documents({})
        if doc_count == 0:
            # Seed if empty
            txns = lab01.generate_transactions(n=10000, fraud_pct=200)
            col.insert_many(txns)
            col.create_index([("user_id", 1), ("timestamp", -1)], name="idx_user_time")
            col.create_index([("risk_score", -1)], name="idx_risk")
            col.create_index([("category", 1)], name="idx_category")

        # Run benchmark
        bench_results = lab01.benchmark_mongodb(col, [])

        formatted_results = []
        for name, latency, count in bench_results:
            c_latency, c_note = lab02.CASSANDRA_ESTIMATES.get(name, ("N/A", ""))
            n_latency, n_note = lab02.NEO4J_ESTIMATES.get(name, ("N/A", ""))
            
            mongo_ms = round(latency * 1000, 2)
            formatted_results.append({
                "query": name,
                "mongo_latency_ms": mongo_ms,
                "mongo_count": count,
                "cassandra_latency": c_latency,
                "cassandra_note": c_note,
                "neo4j_latency": n_latency,
                "neo4j_note": n_note,
                "description": {
                    "Transaction History": "Point lookup by user_id + timestamp sort (Index Scan)",
                    "High-Risk Query": "Range query risk_score > 0.8 (Bounded Index Scan)",
                    "Category Analytics": "Group by category with sum(amount) & count (Aggregation Pipeline)",
                    "Write Throughput": "Bulk write of 1,000 documents with indexes maintained"
                }.get(name, "")
            })

        return jsonify({
            "success": True,
            "measured": True,
            "dataset_size": col.count_documents({}),
            "results": formatted_results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        # Fallback to labeled estimates
        results, measured = lab02.get_mongo_benchmark()
        formatted_results = []
        for name, latency, count in results:
            c_latency, c_note = lab02.CASSANDRA_ESTIMATES.get(name, ("N/A", ""))
            n_latency, n_note = lab02.NEO4J_ESTIMATES.get(name, ("N/A", ""))
            formatted_results.append({
                "query": name,
                "mongo_latency_ms": round(latency * 1000, 2),
                "mongo_count": count,
                "cassandra_latency": c_latency,
                "cassandra_note": c_note,
                "neo4j_latency": n_latency,
                "neo4j_note": n_note
            })
        return jsonify({
            "success": True,
            "measured": False,
            "warning": str(e),
            "results": formatted_results,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })


@app.route("/api/lab1/query", methods=["GET"])
def api_custom_query():
    try:
        col = get_collection()
        user_id = request.args.get("user_id")
        min_risk = request.args.get("min_risk")
        category = request.args.get("category")
        limit = min(int(request.args.get("limit", 25)), 100)

        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        if min_risk:
            query_filter["risk_score"] = {"$gte": float(min_risk)}
        if category:
            query_filter["category"] = category

        start = time.perf_counter()
        cursor = col.find(query_filter, {"_id": 0}).sort("timestamp", -1).limit(limit)
        results = list(cursor)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        # Get explain plan
        explain = col.find(query_filter).sort("timestamp", -1).limit(limit).explain()
        winning_plan = explain.get("queryPlanner", {}).get("winningPlan", {})

        return jsonify({
            "success": True,
            "count": len(results),
            "latency_ms": elapsed_ms,
            "query_filter": query_filter,
            "results": results,
            "stage": winning_plan.get("stage", "COLLSCAN"),
            "input_stage": winning_plan.get("inputStage", {}).get("stage", "None")
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lab1/fraud-rings")
def api_fraud_rings():
    """Simulates Neo4j graph traversal for fraud ring detection:
    identifies device IDs shared by 2 or more users, especially where at least one is fraudulent.
    """
    try:
        col = get_collection()
        pipeline = [
            {"$group": {
                "_id": "$device_id",
                "user_count": {"$addToSet": "$user_id"},
                "fraud_count": {"$sum": {"$cond": ["$is_fraud", 1, 0]}},
                "total_txns": {"$sum": 1},
                "max_risk": {"$max": "$risk_score"},
                "locations": {"$addToSet": "$location"}
            }},
            {"$project": {
                "device_id": "$_id",
                "unique_users_count": {"$size": "$user_count"},
                "users": "$user_count",
                "fraud_count": 1,
                "total_txns": 1,
                "max_risk": 1,
                "locations": 1,
                "_id": 0
            }},
            {"$match": {"unique_users_count": {"$gte": 2}}},
            {"$sort": {"fraud_count": -1, "unique_users_count": -1}},
            {"$limit": 20}
        ]
        shared_devices = list(col.aggregate(pipeline))
        
        # Build graph node & link representation for D3 / Vis visualizer
        nodes = []
        links = []
        node_ids = set()

        for ring in shared_devices[:10]:
            dev_id = ring["device_id"]
            if dev_id not in node_ids:
                nodes.append({
                    "id": dev_id,
                    "label": dev_id,
                    "type": "device",
                    "fraud_count": ring["fraud_count"],
                    "risk": ring["max_risk"]
                })
                node_ids.add(dev_id)

            for u in ring["users"][:5]:  # show top users
                if u not in node_ids:
                    nodes.append({
                        "id": u,
                        "label": u,
                        "type": "user"
                    })
                    node_ids.add(u)
                links.append({
                    "source": u,
                    "target": dev_id,
                    "relationship": "SHARES_DEVICE"
                })

        return jsonify({
            "success": True,
            "shared_devices_count": len(shared_devices),
            "rings": shared_devices,
            "graph": {
                "nodes": nodes,
                "links": links
            },
            "cypher_equivalent": """MATCH path = (u1:User)-[:SHARES_DEVICE*1..3]-(u2:User)
WHERE u1.id = 'U-0001'
WITH u1, u2, COUNT(*) AS shared_signals
WHERE shared_signals >= 2
RETURN u1.id, u2.id, shared_signals
ORDER BY shared_signals DESC;"""
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lab2/generate-report", methods=["POST"])
def api_generate_report():
    try:
        mongo_results, measured = lab02.get_mongo_benchmark()
        report_md = lab02.build_report(mongo_results, measured)

        os.makedirs(REPORTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_filename = f"comparative_analysis_{timestamp}.md"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        # Also write latest copy
        latest_path = os.path.join(REPORTS_DIR, "latest_comparative_analysis.md")
        with open(latest_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        return jsonify({
            "success": True,
            "measured": measured,
            "filename": report_filename,
            "markdown": report_md,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/lab2/latest-report")
def api_get_latest_report():
    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        md_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "comparative_analysis_*.md")), reverse=True)
        if md_files:
            latest_file = md_files[0]
            with open(latest_file, "r", encoding="utf-8") as f:
                content = f.read()
            return jsonify({
                "success": True,
                "filename": os.path.basename(latest_file),
                "markdown": content
            })
        else:
            # Generate one on the fly
            mongo_results, measured = lab02.get_mongo_benchmark()
            report_md = lab02.build_report(mongo_results, measured)
            latest_file = os.path.join(REPORTS_DIR, f"comparative_analysis_{datetime.now().strftime('%Y%m%d-%H%M%S')}.md")
            with open(latest_file, "w", encoding="utf-8") as f:
                f.write(report_md)
            return jsonify({
                "success": True,
                "filename": os.path.basename(latest_file),
                "markdown": report_md
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/download/report-md")
def download_report_md():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "comparative_analysis_*.md")), reverse=True)
    if md_files:
        return send_file(md_files[0], as_attachment=True, download_name="Comparative_Analysis_Report.md")
    else:
        mongo_results, measured = lab02.get_mongo_benchmark()
        report_md = lab02.build_report(mongo_results, measured)
        return Response(report_md, mimetype="text/markdown", headers={"Content-Disposition": "attachment;filename=Comparative_Analysis_Report.md"})


@app.route("/api/download/report-pdf")
def download_report_pdf():
    pdf_path = os.path.join(_root, "Lab_18_Report.pdf")
    if not os.path.exists(pdf_path):
        import generate_pdf_direct
        generate_pdf_direct.build_pdf()
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name="NoSQL_Lab18_Report.pdf")
    return jsonify({"error": "PDF not yet generated"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting NoSQL Lab 18 Web UI on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
