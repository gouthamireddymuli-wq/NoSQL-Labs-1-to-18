"""Generate comprehensive, beautifully styled Lab 01 report in DOCX format.
"""

import os
import sys
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_DOCX = os.path.join(BASE_DIR, "NoSQL_Lab_01_Report.docx")


def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner cell padding in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_code_block(doc, code_text):
    """Add a syntax-highlighted code block in a shaded container table."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)

    cell = table.cell(0, 0)
    set_cell_background(cell, "F2F4F7")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

    # Add code lines
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05

    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(36, 41, 47)

    # Empty paragraph after table for spacing
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(6)


def read_file_content(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_docx():
    doc = Document()

    # Set page margins (0.75 in)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Colors
    NAVY = RGBColor(27, 54, 93)
    SLATE = RGBColor(74, 85, 104)
    TEXT_DARK = RGBColor(45, 55, 72)

    # Configure default style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = TEXT_DARK

    # --- TITLE / HEADER SECTION ---
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_course = p_title.add_run("NOSQL DATABASES LABORATORY\n")
    run_course.font.name = "Calibri"
    run_course.font.size = Pt(13)
    run_course.font.bold = True
    run_course.font.color.rgb = SLATE

    run_title = p_title.add_run("LAB 01 REPORT: DATABASE CLASSIFICATION &\nAPPLICATION DATA DOMAIN MAPPING")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY

    # Meta Table (Student details)
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(3.25)
    meta_table.columns[1].width = Inches(3.25)

    cell_00 = meta_table.cell(0, 0)
    cell_00.paragraphs[0].add_run("Student Name: ").bold = True
    cell_00.paragraphs[0].add_run("M. Gouthami")

    cell_01 = meta_table.cell(0, 1)
    cell_01.paragraphs[0].add_run("Register / Roll No: ").bold = True
    cell_01.paragraphs[0].add_run("24BTRCL130")

    cell_10 = meta_table.cell(1, 0)
    cell_10.paragraphs[0].add_run("Course: ").bold = True
    cell_10.paragraphs[0].add_run("NoSQL Databases")

    cell_11 = meta_table.cell(1, 1)
    cell_11.paragraphs[0].add_run("Date: ").bold = True
    cell_11.paragraphs[0].add_run("November 2026")

    for row in meta_table.rows:
        for c in row.cells:
            set_cell_background(c, "EBF3FA")
            set_cell_margins(c, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- EXECUTIVE SUMMARY ---
    h1 = doc.add_paragraph()
    r = h1.add_run("1. Executive Summary & Laboratory Objectives")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    p_summary = doc.add_paragraph(
        "Modern cloud-scale architectures increasingly move away from monolithic single-database models toward "
        "Polyglot Persistence — the strategic deployment of multiple database engines tailored to distinct data models "
        "and read/write workloads within an enterprise ecosystem. The objectives of this laboratory are twofold:\n\n"
        "1. Activity 1.1: Survey and systematically classify real-world database products into canonical NoSQL families "
        "(Document, Key-Value, Wide-Column, Graph, and Search/Object stores), examining their storage architectures, "
        "query capabilities, and enterprise use cases. In the 'Try It Yourself' segment, classify 8 next-generation "
        "and mystery engines (DynamoDB, InfluxDB, OrientDB, ScyllaDB, ArangoDB, CockroachDB, ClickHouse, and FaunaDB) "
        "while analyzing CAP theorem trade-offs.\n\n"
        "2. Activity 1.2: Deconstruct complex multi-tier applications into functional data domains. In the core lab, "
        "map data domains for a Ride-Sharing Application and a Social Media Analytics Platform. In the 'Try It Yourself' "
        "segment, perform self-evaluation and architectural mapping for an E-Commerce & Retail Marketplace (Amazon/Flipkart) "
        "and a Smart Healthcare & Telemedicine Ecosystem (Practo/Teladoc), comparing initial personal reasoning "
        "against industry best practices."
    )
    p_summary.paragraph_format.line_spacing = 1.15
    p_summary.paragraph_format.space_after = Pt(12)

    # --- SECTION 2: ACTIVITY 1.1 ---
    h2 = doc.add_paragraph()
    r = h2.add_run("2. Activity 1.1: Classify Database Products")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "Activity 1.1 conducts a survey of 10 established database products across key NoSQL categories: "
        "Amazon S3, Couchbase, Apache HBase, Amazon Neptune, Memcached, Redis, MongoDB, Apache Cassandra, "
        "Neo4j, and Elasticsearch. Each product's primary data model, vendor, and target use case are stored in "
        "MongoDB and displayed via an aggregated survey."
    )

    doc.add_heading("2.1 Python Script Implementation (lab_01_classify_databases.py)", level=2)
    script_1_code = read_file_content(os.path.join(BASE_DIR, "Activity_1.1", "lab_01_classify_databases.py"))
    add_code_block(doc, script_1_code)

    doc.add_heading("2.2 Respective MongoDB JSON Export (database_products.json)", level=2)
    doc.add_paragraph(
        "Upon execution, the script resets collection 'database_products' in the 'nosql_labs' database, inserts all 10 "
        "product definitions, and automatically exports the persistent records to 'database_products.json'. A snippet of "
        "the exported MongoDB documents is displayed below:"
    )
    json_1_path = os.path.join(BASE_DIR, "Activity_1.1", "database_products.json")
    json_1_sample = json.dumps(json.loads(read_file_content(json_1_path))[:3], indent=2)
    add_code_block(doc, json_1_sample + "\n// ... [7 more documents exported in database_products.json]")

    doc.add_heading("2.3 Execution Output & Screenshot", level=2)
    doc.add_paragraph("The screenshot below captures the complete terminal execution of Activity 1.1:")
    img_1 = os.path.join(SCREENSHOTS_DIR, "activity_1_1_output.png")
    if os.path.exists(img_1):
        doc.add_picture(img_1, width=Inches(6.5))
        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 3: ACTIVITY 1.1 TRY IT YOURSELF ---
    h3 = doc.add_paragraph()
    r = h3.add_run("3. Activity 1.1 'Try It Yourself': Advanced Classification & Mystery Products")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "The 'Try It Yourself' segment tackles mystery products and modern hybrid engines that span traditional family boundaries. "
        "Eight products were rigorously evaluated:\n"
        "• DynamoDB: Key-Value / Document with single-digit millisecond latency at any scale.\n"
        "• InfluxDB: Purpose-built Time-Series engine optimized for append-only timestamped sensor/DevOps metrics.\n"
        "• OrientDB: Multi-Model engine seamlessly combining schema-free JSON documents with native pointer graph vertices/edges.\n"
        "• ScyllaDB: Wide-Column engine written in C++ providing 10x throughput over Cassandra with ultra-low tail latency.\n"
        "• ArangoDB: Multi-Model supporting Documents, Graphs, and Full-Text Search within a single declarative query (AQL).\n"
        "• CockroachDB: Distributed SQL / NewSQL delivering horizontal scalability with serializable ACID transactions via Raft.\n"
        "• ClickHouse: Column-Oriented OLAP store achieving multi-gigabyte/sec vectorized query execution for clickstream data.\n"
        "• FaunaDB: Serverless multi-model document store with global Calvin ACID consensus."
    )

    doc.add_heading("3.1 Python Script Implementation (lab_01_try_it_yourself.py)", level=2)
    script_1_try_code = read_file_content(os.path.join(BASE_DIR, "Activity_1.1_Try_It_Yourself", "lab_01_try_it_yourself.py"))
    add_code_block(doc, script_1_try_code)

    doc.add_heading("3.2 Respective MongoDB JSON Export (database_products_try_it_yourself.json)", level=2)
    doc.add_paragraph(
        "The script populates collection 'database_products_try_it_yourself' in MongoDB and exports all documents to JSON. "
        "Below is a sample showing the rich CAP classification and architectural rationale stored in MongoDB:"
    )
    json_1_try_path = os.path.join(BASE_DIR, "Activity_1.1_Try_It_Yourself", "database_products_try_it_yourself.json")
    json_1_try_sample = json.dumps(json.loads(read_file_content(json_1_try_path))[:3], indent=2)
    add_code_block(doc, json_1_try_sample + "\n// ... [5 more documents exported in database_products_try_it_yourself.json]")

    doc.add_heading("3.3 Execution Output & Screenshot", level=2)
    doc.add_paragraph("The screenshot below captures the complete terminal execution of Activity 1.1 'Try It Yourself':")
    img_1_try = os.path.join(SCREENSHOTS_DIR, "activity_1_1_try_it_yourself_output.png")
    if os.path.exists(img_1_try):
        doc.add_picture(img_1_try, width=Inches(6.5))
        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 4: ACTIVITY 1.2 ---
    h4 = doc.add_paragraph()
    r = h4.add_run("4. Activity 1.2: Map Real-World Application Data Domains to NoSQL Families")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "Activity 1.2 breaks two major application architectures into four distinct data domains each:\n\n"
        "A. Ride-Sharing Application (e.g., Uber, Lyft):\n"
        "  1. user_profiles: Rider/driver profiles with preferences and payment methods -> Document (MongoDB)\n"
        "  2. ride_history: Completed ride receipts with routes, fares, and timestamps -> Wide-Column (Apache Cassandra)\n"
        "  3. real_time_tracking: Live GPS driver coordinates updated every 1-3 seconds -> Key-Value (Redis with TTL)\n"
        "  4. payment_transactions: Payment ledger, driver payouts, and fare splits -> Document with ACID (MongoDB)\n\n"
        "B. Social Media Analytics Platform (e.g., Brandwatch, Sprout Social):\n"
        "  1. content_feed: Posts, media metadata, and dynamic engagement counters -> Document (MongoDB)\n"
        "  2. social_graph: Follower networks, influence propagation, and community detection -> Graph (Neo4j)\n"
        "  3. sentiment_timeseries: Hourly brand sentiment scores and trend metrics -> Wide-Column (Apache Cassandra)\n"
        "  4. media_assets: High-resolution images and videos served via CDN -> Object / Key-Value (Amazon S3)"
    )

    doc.add_heading("4.1 Python Script Implementation (lab_02_map_application.py)", level=2)
    script_2_code = read_file_content(os.path.join(BASE_DIR, "Activity_1.2", "lab_02_map_application.py"))
    add_code_block(doc, script_2_code)

    doc.add_heading("4.2 Respective MongoDB JSON Export (app_domain_mapping.json)", level=2)
    doc.add_paragraph(
        "The mappings are inserted into MongoDB collection 'app_domain_mapping' and exported to 'app_domain_mapping.json'. "
        "A sample of the exported records is displayed below:"
    )
    json_2_path = os.path.join(BASE_DIR, "Activity_1.2", "app_domain_mapping.json")
    json_2_sample = json.dumps(json.loads(read_file_content(json_2_path))[:3], indent=2)
    add_code_block(doc, json_2_sample + "\n// ... [5 more documents exported in app_domain_mapping.json]")

    doc.add_heading("4.3 Execution Output & Screenshot", level=2)
    doc.add_paragraph("The screenshot below captures the complete terminal execution of Activity 1.2:")
    img_2 = os.path.join(SCREENSHOTS_DIR, "activity_1_2_output.png")
    if os.path.exists(img_2):
        doc.add_picture(img_2, width=Inches(6.5))
        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 5: ACTIVITY 1.2 TRY IT YOURSELF ---
    h5 = doc.add_paragraph()
    r = h5.add_run("5. Activity 1.2 'Try It Yourself': Architectural Mapping & Self-Evaluation")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "In accordance with the lab instructions, this activity evaluates two complex production applications before viewing "
        "the recommended database choices: an E-Commerce Platform (Amazon/Flipkart) and a Smart Healthcare/Telemedicine "
        "Ecosystem (Practo/Teladoc). For each domain, personal architectural reasoning was formulated based purely on "
        "the domain description and read/write workload, and subsequently compared against the architectural rationale."
    )

    doc.add_heading("5.1 Self-Evaluation Reasoning vs. Architectural Rationale Matrix", level=2)

    eval_table = doc.add_table(rows=1, cols=4)
    eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_table.autofit = False
    eval_table.columns[0].width = Inches(1.3)
    eval_table.columns[1].width = Inches(1.1)
    eval_table.columns[2].width = Inches(2.05)
    eval_table.columns[3].width = Inches(2.05)

    headers = ["Domain", "Selected Family", "Student Reasoning", "Architectural Rationale"]
    hdr_cells = eval_table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].paragraphs[0].add_run(title).bold = True
        set_cell_background(hdr_cells[i], "1F4E79")
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(hdr_cells[i], top=80, bottom=80, left=100, right=100)

    eval_data = [
        ("product_catalog (E-Commerce)", "Document (MongoDB)",
         "Polymorphic/schema-free requirements make Document family ideal because each product category has different attributes without needing sparse SQL tables.",
         "Flexible JSON/BSON schema natively models polymorphic product specs; secondary indexes and full-text search optimize multi-attribute filtering."),

        ("cart_and_active_sessions (E-Commerce)", "Key-Value (Redis)",
         "Sub-millisecond latency is essential to avoid checkout abandonment; simple key lookup by session_id and automated TTL expiration points to in-memory KV.",
         "In-memory key-value data structures provide sub-millisecond responses; built-in TTL auto-purges abandoned carts; atomic operations handle flash sale inventory locks."),

        ("clickstream_and_order_events (E-Commerce)", "Wide-Column (Cassandra)",
         "Massive stream of append-only time-stamped events requires a database optimized for linear write scalability without write locks.",
         "Masterless ring architecture ensures zero write bottlenecks; time-partitioned column families deliver fast time-range queries and infinite horizontal scalability."),

        ("recommendation_and_fraud_network (E-Commerce)", "Graph (Neo4j)",
         "Traversing multi-hop relationships (user -> item -> user -> item or fraud rings) causes catastrophic join overhead in relational DBs, making Graph stores optimal.",
         "Native index-free adjacency enables sub-second multi-hop graph traversals; Cypher queries identify circular fraud rings and recommendation pathways efficiently."),

        ("patient_health_records (Healthcare)", "Document (MongoDB)",
         "Patient records are hierarchical and vary significantly between medical specialties, making a Document database with nested structures the most natural fit.",
         "Nested BSON documents naturally map to FHIR/HL7 healthcare standards; field-level encryption secures sensitive PHI (Protected Health Information)."),

        ("live_biometric_telemetry (Healthcare)", "Key-Value / In-Memory (Redis)",
         "High-frequency streaming sensor data requires an in-memory buffer with lightning-fast ingestion and pub/sub alerting for emergency biometric threshold breaches.",
         "Redis Streams handles high-throughput ingestion with microsecond latency; pub/sub instantly triggers clinical alarms when patient vitals cross safe thresholds."),

        ("billing_and_claims_ledger (Healthcare)", "Document with ACID (MongoDB)",
         "Financial ledgers require absolute zero tolerance for inconsistency or partial commits; needs ACID transactional guarantees combined with flexible claim detail structures.",
         "Multi-document ACID transactions ensure all-or-nothing execution across copays and insurance claims, with document model capturing complex claim breakdown hierarchies."),

        ("drug_interaction_knowledge_graph (Healthcare)", "Graph (Neo4j)",
         "Checking whether a new drug conflicts with existing patient medications across multiple metabolic pathways requires traversing a network of relationships.",
         "Graph model represents drugs, enzymes, and side effects as nodes and edges; graph algorithms traverse conflict paths instantly to prevent fatal adverse interactions.")
    ]

    for row_idx, data in enumerate(eval_data):
        row_cells = eval_table.add_row().cells
        bg_col = "FFFFFF" if row_idx % 2 == 0 else "F7FAFC"
        for c_idx, val in enumerate(data):
            row_cells[c_idx].paragraphs[0].add_run(val)
            row_cells[c_idx].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=60, bottom=60, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.add_heading("5.2 Python Script Implementation (lab_02_try_it_yourself.py)", level=2)
    script_2_try_code = read_file_content(os.path.join(BASE_DIR, "Activity_1.2_Try_It_Yourself", "lab_02_try_it_yourself.py"))
    add_code_block(doc, script_2_try_code)

    doc.add_heading("5.3 Respective MongoDB JSON Export (app_domain_mapping_try_it_yourself.json)", level=2)
    doc.add_paragraph(
        "All 8 domain records containing the detailed student reasoning and architectural rationale were saved into "
        "MongoDB collection 'app_domain_mapping_try_it_yourself' and exported to JSON. A sample document is displayed below:"
    )
    json_2_try_path = os.path.join(BASE_DIR, "Activity_1.2_Try_It_Yourself", "app_domain_mapping_try_it_yourself.json")
    json_2_try_sample = json.dumps(json.loads(read_file_content(json_2_try_path))[:2], indent=2)
    add_code_block(doc, json_2_try_sample + "\n// ... [6 more documents exported in app_domain_mapping_try_it_yourself.json]")

    doc.add_heading("5.4 Execution Output & Screenshot", level=2)
    doc.add_paragraph("The screenshot below captures the complete terminal execution of Activity 1.2 'Try It Yourself':")
    img_2_try = os.path.join(SCREENSHOTS_DIR, "activity_1_2_try_it_yourself_output.png")
    if os.path.exists(img_2_try):
        doc.add_picture(img_2_try, width=Inches(6.5))
        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # --- SECTION 6: SYNTHESIS & COMPARATIVE MATRIX ---
    h6 = doc.add_paragraph()
    r = h6.add_run("6. Synthesis: NoSQL Architectural Decision Matrix")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "Selecting the correct database technology requires balancing data access patterns, consistency requirements, "
        "latency budgets, and horizontal scaling capabilities. The comparative matrix below synthesizes the key trade-offs:"
    )

    matrix_table = doc.add_table(rows=1, cols=5)
    matrix_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    matrix_table.autofit = False
    matrix_table.columns[0].width = Inches(1.1)
    matrix_table.columns[1].width = Inches(1.2)
    matrix_table.columns[2].width = Inches(1.3)
    matrix_table.columns[3].width = Inches(1.1)
    matrix_table.columns[4].width = Inches(1.8)

    m_headers = ["NoSQL Family", "Primary Data Model", "Read/Write Strength", "CAP Tendency", "Canonical Use Cases"]
    m_hdr_cells = matrix_table.rows[0].cells
    for i, title in enumerate(m_headers):
        m_hdr_cells[i].paragraphs[0].add_run(title).bold = True
        set_cell_background(m_hdr_cells[i], "1F4E79")
        m_hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(m_hdr_cells[i], top=80, bottom=80, left=90, right=90)

    matrix_data = [
        ("Key-Value", "Key -> Value (Opaque/Binary/Hashes)", "Sub-ms lookup by Key; high write rate", "AP / CP (Tunable)",
         "User sessions, shopping carts, gaming state, live driver GPS, real-time caching (Redis, Memcached)"),

        ("Document", "Hierarchical JSON / BSON Trees", "Flexible schema, secondary indexing, aggregations", "CP (Mongo), AP (Couch)",
         "Product catalogs, user profiles, clinical EHR records, CMS, polymorphic transactional data (MongoDB, Couchbase)"),

        ("Wide-Column", "Partitioned Rows with Dynamic Columns", "Extreme append write throughput, time-range scans", "AP (Cassandra / Scylla)",
         "Clickstream events, IoT sensor streams, financial tickers, ride history logs (Cassandra, HBase, ScyllaDB)"),

        ("Graph", "Nodes, Edges, Properties (Index-Free)", "Multi-hop traversals, shortest path, pattern matching", "CP (Neo4j / Neptune)",
         "Social networks, fraud detection rings, drug contraindication graphs, recommendation engines (Neo4j, Neptune)"),

        ("Search / Multi-Model", "Inverted Index / Hybrid Stores", "Full-text search, multi-model unified querying", "AP / CP Configurable",
         "Faceted search, observability, knowledge graphs with rich documents (Elasticsearch, ArangoDB, OrientDB)")
    ]

    for row_idx, data in enumerate(matrix_data):
        row_cells = matrix_table.add_row().cells
        bg_col = "FFFFFF" if row_idx % 2 == 0 else "F7FAFC"
        for c_idx, val in enumerate(data):
            row_cells[c_idx].paragraphs[0].add_run(val)
            row_cells[c_idx].paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=60, bottom=60, left=80, right=80)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # --- SECTION 7: CONCLUSION ---
    h7 = doc.add_paragraph()
    r = h7.add_run("7. Conclusion")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = NAVY

    doc.add_paragraph(
        "Through Activities 1.1 and 1.2 and their respective 'Try It Yourself' exercises, we demonstrated that modern "
        "software engineering rarely relies on a single database product. By analyzing data structures (polymorphic documents vs. "
        "interconnected graphs), throughput characteristics (streaming telemetry vs. transactional billing), and consistency "
        "tolerances (strong ACID vs. eventual consistency), developers can design resilient, highly performant polyglot "
        "persistence architectures that scale horizontally while meeting rigorous SLA requirements."
    )

    doc.save(OUTPUT_DOCX)
    print(f"[OK] Report saved successfully to: {OUTPUT_DOCX}")


if __name__ == "__main__":
    build_docx()
