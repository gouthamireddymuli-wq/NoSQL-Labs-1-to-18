"""Lab 1.1 - Try It Yourself: Advanced Database Classification & Mystery Products

Comprehensive NoSQL family classification for mystery products and next-generation databases.
"""

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [parent_dir, current_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config.connection import get_db, reset_collection, banner, print_json, export_collection_to_json
from rich.table import Table
from rich.console import Console

console = Console(width=115)


def main():
    banner("Lab 1.1 'Try It Yourself': Advanced NoSQL Product Classification")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "database_products_try_it_yourself")

    # Mystery products and modern industry-leading NoSQL architectures
    classified_products = [
        {
            "name": "DynamoDB",
            "family": "Key-Value / Document",
            "data_model": "Partition Key + Sort Key (Item/Attributes)",
            "vendor": "Amazon Web Services (AWS)",
            "cap_theorem": "Configurable (Default AP / Eventual, Optional CP / Strong)",
            "query_language": "PartiQL / DynamoDB API",
            "use_case": "High-scale shopping carts, user sessions, gaming state, IoT ingest",
            "rationale": "Stores JSON-like items indexed by hash keys; provides predictable single-digit ms SLA at any scale"
        },
        {
            "name": "InfluxDB",
            "family": "Wide-Column / Time-Series",
            "data_model": "Time-Series (Timestamp, Tag set, Field set)",
            "vendor": "InfluxData",
            "cap_theorem": "AP (High availability, fast ingestion)",
            "query_language": "InfluxQL / Flux / SQL",
            "use_case": "DevOps monitoring, IoT telemetry, financial ticker feeds, sensor analytics",
            "rationale": "Optimized for append-only timestamped metrics with downsampling, retention policies, and time range aggregations"
        },
        {
            "name": "OrientDB",
            "family": "Multi-Model (Document + Graph)",
            "data_model": "Hybrid Document & Property Graph",
            "vendor": "CallidusCloud (SAP)",
            "cap_theorem": "CP (Consistency prioritized)",
            "query_language": "Extended SQL",
            "use_case": "Master data management, fraud detection with nested document properties",
            "rationale": "Combines document storage (schema-free JSON records) with native direct pointer vertex-edge graph traversals"
        },
        {
            "name": "ScyllaDB",
            "family": "Wide-Column",
            "data_model": "Column-Family (C++ asynchronous architecture)",
            "vendor": "ScyllaDB Inc.",
            "cap_theorem": "AP (Highly available, tunable consistency)",
            "query_language": "CQL (Cassandra Query Language)",
            "use_case": "Ultra-low-latency ad-tech bidding, real-time messaging, IoT platforms",
            "rationale": "Drop-in Cassandra replacement re-engineered in C++ with shared-nothing architecture for 10x throughput and sub-ms P99 latency"
        },
        {
            "name": "ArangoDB",
            "family": "Multi-Model (Document + Graph + Search)",
            "data_model": "JSON Documents with Vertices & Edges",
            "vendor": "ArangoDB GmbH",
            "cap_theorem": "CP / Configurable Cluster",
            "query_language": "AQL (ArangoDB Query Language)",
            "use_case": "Complex recommendation graphs with rich item descriptions, knowledge bases",
            "rationale": "Unified query engine allowing document joins, graph traversals, and full-text search in a single declarative query"
        },
        {
            "name": "CockroachDB",
            "family": "Distributed SQL / NewSQL",
            "data_model": "Relational Tables backed by Distributed Key-Value (Pebble/RocksDB)",
            "vendor": "Cockroach Labs",
            "cap_theorem": "CP (Strict serializable ACID consistency via Raft consensus)",
            "query_language": "PostgreSQL-compatible SQL",
            "use_case": "Multi-region cloud banking, global ledger balances, regulatory compliance",
            "rationale": "Provides horizontal scalability of NoSQL with full ANSI SQL and serializable ACID transactions across geographically distributed nodes"
        },
        {
            "name": "ClickHouse",
            "family": "Column-Oriented (OLAP)",
            "data_model": "Columnar Storage with vectorized query execution",
            "vendor": "ClickHouse Inc.",
            "cap_theorem": "AP / Eventual consistency for distributed replicas",
            "query_language": "Dialect of SQL",
            "use_case": "Real-time web analytics, clickstream aggregations, security event monitoring",
            "rationale": "Columns stored contiguously on disk allowing multi-gigabyte/sec aggregations and high data compression ratios for billions of rows"
        },
        {
            "name": "FaunaDB",
            "family": "Multi-Model / Serverless Document",
            "data_model": "Document-Relational with temporal versioning",
            "vendor": "Fauna Inc.",
            "cap_theorem": "Strictly Consistent (Calvin consensus protocol)",
            "query_language": "FQL (Fauna Query Language)",
            "use_case": "JAMstack applications, serverless microservices, globally distributed SaaS",
            "rationale": "Serverless transactional database offering GraphQL native APIs, ACID consistency without master bottlenecks, and point-in-time temporal queries"
        }
    ]

    col.insert_many(classified_products)
    print(f"[OK] Inserted {len(classified_products)} classified database products into MongoDB.\n")

    # Render survey table
    table = Table(title="Activity 1.1 'Try It Yourself' - Advanced NoSQL Database Classification", show_lines=True)
    table.add_column("Product", style="cyan", width=14)
    table.add_column("NoSQL Family", style="magenta", width=22)
    table.add_column("Data Model", width=28)
    table.add_column("CAP Category", style="yellow", width=14)
    table.add_column("Architectural Rationale", width=33)

    for p in col.find().sort("family"):
        table.add_row(
            p["name"],
            p["family"],
            p["data_model"],
            p["cap_theorem"].split("(")[0].strip(),
            p["rationale"]
        )

    console.print(table)

    # Aggregation 1: Grouped by Family
    print("\n--- Aggregation: Product Distribution by NoSQL Family ---")
    pipeline_family = [
        {"$group": {"_id": "$family", "count": {"$sum": 1}, "databases": {"$push": "$name"}}},
        {"$sort": {"count": -1}}
    ]
    for g in col.aggregate(pipeline_family):
        print(f"  * {g['_id']:28} ({g['count']} DBs) -> {', '.join(g['databases'])}")

    # Aggregation 2: CAP Theorem breakdown
    print("\n--- Aggregation: CAP Theorem Distribution ---")
    pipeline_cap = [
        {"$project": {
            "name": "$name",
            "cap_type": {
                "$cond": [
                    {"$regexMatch": {"input": "$cap_theorem", "regex": "CP"}},
                    "CP (Consistency / Partition Tolerance)",
                    "AP (Availability / Partition Tolerance)"
                ]
            }
        }},
        {"$group": {"_id": "$cap_type", "count": {"$sum": 1}, "products": {"$push": "$name"}}},
        {"$sort": {"count": -1}}
    ]
    for g in col.aggregate(pipeline_cap):
        print(f"  * {g['_id']:42} ({g['count']}) -> {', '.join(g['products'])}")

    # Export to MongoDB JSON
    json_path = os.path.join(current_dir, "database_products_try_it_yourself.json")
    export_collection_to_json("nosql_labs", "database_products_try_it_yourself", json_path)

    banner("Lab 1.1 'Try It Yourself' Complete")


if __name__ == "__main__":
    main()
