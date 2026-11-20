"""Lab 1.2 - Try It Yourself: Map Real-World Applications to NoSQL Families

Interactive domain mapping with self-evaluation reasoning vs architectural rationale
for E-Commerce and Healthcare applications.
"""

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [parent_dir, current_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config.connection import get_db, reset_collection, banner, export_collection_to_json
from rich.table import Table
from rich.console import Console

console = Console(width=115)


def main():
    banner("Lab 1.2 'Try It Yourself': Architectural Mapping & Self-Evaluation")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "app_domain_mapping_try_it_yourself")

    # --- Application 1: E-Commerce & Retail Platform ---
    ecommerce_domains = [
        {
            "app": "E-Commerce Platform",
            "domain": "product_catalog",
            "description": "Hierarchical catalog with variable attributes across categories (e.g., clothing sizes vs. laptop RAM), rich descriptions, and reviews",
            "read_write_pattern": "Read-heavy (browsing/search), low-frequency updates by merchants",
            "student_reasoning": "Polymorphic/schema-free requirements make Document family ideal because each product category has different attributes without needing sparse SQL tables or complex joins.",
            "recommended_family": "Document",
            "recommended_db": "MongoDB",
            "rationale": "Flexible JSON/BSON schema natively models polymorphic product specs; secondary indexes and full-text search optimize multi-attribute filtering.",
            "alignment": "Full Match (Identified document schema flexibility for polymorphic products)"
        },
        {
            "app": "E-Commerce Platform",
            "domain": "cart_and_active_sessions",
            "description": "Active shopping cart items, temporary inventory locks during checkout, and session authentication tokens",
            "read_write_pattern": "Extreme read + write throughput, sub-millisecond latency SLA, TTL expiration",
            "student_reasoning": "Sub-millisecond latency is essential to avoid checkout abandonment; simple key lookup by session_id and automated TTL expiration points directly to an in-memory Key-Value store.",
            "recommended_family": "Key-Value",
            "recommended_db": "Redis",
            "rationale": "In-memory key-value data structures provide sub-millisecond responses; built-in TTL auto-purges abandoned carts; atomic operations handle flash sale inventory locks.",
            "alignment": "Full Match (Prioritized sub-millisecond latency and automatic TTL expiry)"
        },
        {
            "app": "E-Commerce Platform",
            "domain": "clickstream_and_order_events",
            "description": "User click events, browsing telemetry, order status transitions, and audit logs recorded sequentially",
            "read_write_pattern": "Massive append-only write throughput, sequential time-ordered queries, analytical range scans",
            "student_reasoning": "Massive stream of append-only time-stamped events requires a database optimized for linear write scalability without write locks, matching Wide-Column stores.",
            "recommended_family": "Wide-Column",
            "recommended_db": "Apache Cassandra",
            "rationale": "Masterless ring architecture ensures zero write bottlenecks; time-partitioned column families deliver fast time-range queries and infinite horizontal scalability.",
            "alignment": "Full Match (Recognized write throughput and time-ordered range scans)"
        },
        {
            "app": "E-Commerce Platform",
            "domain": "recommendation_and_fraud_network",
            "description": "Customer co-purchase graphs ('bought together'), product affinity networks, and shared credit card/device fraud rings",
            "read_write_pattern": "Multi-hop graph traversals, associative queries, relationship pattern matching",
            "student_reasoning": "Traversing multi-hop relationships (user -> item -> user -> item or user -> device -> fraud ring) causes catastrophic join overhead in relational DBs, making Graph stores optimal.",
            "recommended_family": "Graph",
            "recommended_db": "Neo4j",
            "rationale": "Native index-free adjacency enables sub-second multi-hop graph traversals; Cypher queries identify circular fraud rings and recommendation pathways efficiently.",
            "alignment": "Full Match (Identified multi-hop traversal and index-free adjacency benefits)"
        }
    ]

    # --- Application 2: Smart Healthcare & Telemedicine Platform ---
    healthcare_domains = [
        {
            "app": "Healthcare & Telemedicine",
            "domain": "patient_health_records",
            "description": "Electronic Medical Records (EMR/EHR) containing clinical diagnostic notes, lab reports, allergies, and treatment histories",
            "read_write_pattern": "Read-heavy during consultations, append-only clinical encounter logs, strict audit trails",
            "student_reasoning": "Patient records are hierarchical and vary significantly between medical specialties, making a Document database with nested structures the most natural fit.",
            "recommended_family": "Document",
            "recommended_db": "MongoDB",
            "rationale": "Nested BSON documents naturally map to FHIR/HL7 healthcare standards; field-level encryption secures sensitive PHI (Protected Health Information).",
            "alignment": "Full Match (Recognized nested hierarchical nature of clinical data and schema flexibility)"
        },
        {
            "app": "Healthcare & Telemedicine",
            "domain": "live_biometric_telemetry",
            "description": "Continuous vital signs streams from wearable IoT monitors (heart rate, ECG, SpO2, blood pressure) updated every second",
            "read_write_pattern": "Continuous high-frequency writes, rolling time-window anomaly detection, TTL downsampling",
            "student_reasoning": "High-frequency streaming sensor data requires an in-memory buffer with lightning-fast ingestion and pub/sub alerting for emergency biometric threshold breaches.",
            "recommended_family": "Key-Value / In-Memory",
            "recommended_db": "Redis",
            "rationale": "Redis Streams handles high-throughput ingestion with microsecond latency; pub/sub instantly triggers clinical alarms when patient vitals cross safe thresholds.",
            "alignment": "Full Match (Prioritized streaming throughput and instant threshold alerting)"
        },
        {
            "app": "Healthcare & Telemedicine",
            "domain": "billing_and_claims_ledger",
            "description": "Patient insurance billing, copay payments, pharmacy claim disbursements, and financial reconciliation ledgers",
            "read_write_pattern": "Write-once, strong ACID transactional consistency required, strict regulatory compliance",
            "student_reasoning": "Financial ledgers require absolute zero tolerance for inconsistency or partial commits; needs ACID transactional guarantees combined with flexible claim detail structures.",
            "recommended_family": "Document (with ACID)",
            "recommended_db": "MongoDB (ACID Transactions)",
            "rationale": "Multi-document ACID transactions ensure all-or-nothing execution across copays and insurance claims, with document model capturing complex claim breakdown hierarchies.",
            "alignment": "Full Match (Recognized necessity of ACID transactions for financial ledger integrity)"
        },
        {
            "app": "Healthcare & Telemedicine",
            "domain": "drug_interaction_knowledge_graph",
            "description": "Ontology of pharmaceutical drugs, active ingredients, contraindications, and adverse drug-drug interaction pathways",
            "read_write_pattern": "Recursive relationship traversals, conflict detection at prescription time",
            "student_reasoning": "Checking whether a new drug conflicts with any existing patient medications across multiple metabolic pathways requires traversing a network of relationships, which is a textbook Graph database use case.",
            "recommended_family": "Graph",
            "recommended_db": "Neo4j",
            "rationale": "Graph model represents drugs, enzymes, and side effects as nodes and edges; graph algorithms traverse conflict paths instantly to prevent fatal adverse interactions.",
            "alignment": "Full Match (Identified relationship-centric path traversal for conflict detection)"
        }
    ]

    all_domains = ecommerce_domains + healthcare_domains
    col.insert_many(all_domains)
    print(f"[OK] Inserted {len(all_domains)} architectural domain mappings with self-evaluation into MongoDB.\n")

    # Interactive Step-by-Step Self-Evaluation Walkthrough
    print("=" * 80)
    print("STEP-BY-STEP ARCHITECTURAL EVALUATION & REASONING COMPARISON")
    print("=" * 80)
    for app_name in ["E-Commerce Platform", "Healthcare & Telemedicine"]:
        print(f"\n>>> Application: {app_name}")
        for d in col.find({"app": app_name}):
            print(f"\n  [Domain]: {d['domain'].upper()}")
            print(f"  - Description       : {d['description']}")
            print(f"  - Read/Write Pattern: {d['read_write_pattern']}")
            print(f"  - Student Reasoning : {d['student_reasoning']}")
            print(f"  - Recommended Family: {d['recommended_family']} ({d['recommended_db']})")
            print(f"  - Script Rationale  : {d['rationale']}")
            print(f"  - Alignment Status  : {d['alignment']}")

    # Render clean summary tables per application
    print("\n")
    for app_name in ["E-Commerce Platform", "Healthcare & Telemedicine"]:
        table = Table(title=f"{app_name} - Data Domain Mapping & Evaluation", show_lines=True)
        table.add_column("Domain", style="cyan", width=22)
        table.add_column("NoSQL Family", style="magenta", width=16)
        table.add_column("Recommended DB", style="green", width=18)
        table.add_column("Student Reasoning", style="yellow", width=30)
        table.add_column("Architectural Rationale", width=32)

        for d in col.find({"app": app_name}):
            table.add_row(
                d["domain"],
                d["recommended_family"],
                d["recommended_db"],
                d["student_reasoning"],
                d["rationale"]
            )
        console.print(table)
        print()

    # Aggregation: Family Distribution across both new applications
    print("--- Family Distribution across Applications ---")
    pipeline = [
        {"$group": {"_id": "$recommended_family", "count": {"$sum": 1}, "domains": {"$push": "$domain"}}},
        {"$sort": {"count": -1}}
    ]
    for g in col.aggregate(pipeline):
        print(f"  * {g['_id']:24} : {g['count']} domain(s) -> {', '.join(g['domains'])}")

    # Export to respective MongoDB JSON file
    json_path = os.path.join(current_dir, "app_domain_mapping_try_it_yourself.json")
    export_collection_to_json("nosql_labs", "app_domain_mapping_try_it_yourself", json_path)

    banner("Lab 1.2 'Try It Yourself' Complete")


if __name__ == "__main__":
    main()
