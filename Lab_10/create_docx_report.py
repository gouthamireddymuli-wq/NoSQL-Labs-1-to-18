import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

doc = Document()

# Set standard margins (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

# Color Palette
COLOR_PRIMARY = RGBColor(0, 104, 74)     # Emerald Green #00684A
COLOR_SECONDARY = RGBColor(9, 105, 218)  # Blue #0969DA
COLOR_DARK = RGBColor(31, 35, 40)        # Dark Charcoal
COLOR_GRAY = RGBColor(87, 96, 106)       # Muted Gray

def set_cell_background(cell, fill_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

# Banner
banner_p = doc.add_paragraph()
banner_p.paragraph_format.space_before = Pt(0)
banner_p.paragraph_format.space_after = Pt(4)
banner_run = banner_p.add_run("UNIVERSITY LABORATORY EXAMINATION & TECHNICAL REPORT")
banner_run.font.name = "Arial"
banner_run.font.size = Pt(10)
banner_run.font.bold = True
banner_run.font.color.rgb = COLOR_GRAY

# Title
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(2)
title_run = title_p.add_run("NoSQL Lab 10: Multi-Document Transactions & Concurrency Handling")
title_run.font.name = "Arial"
title_run.font.size = Pt(20)
title_run.font.bold = True
title_run.font.color.rgb = COLOR_PRIMARY

# Subtitle
sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_before = Pt(0)
sub_p.paragraph_format.space_after = Pt(12)
sub_run = sub_p.add_run("Empirical Implementation of ACID Transactions, Rollback Mechanics, Optimistic Concurrency Control, and Full-Stack Platform Integration")
sub_run.font.name = "Arial"
sub_run.font.size = Pt(11)
sub_run.font.color.rgb = COLOR_GRAY

# Metadata Callout Table
metadata = [
    ("Course / Module", "NoSQL Databases using MongoDB — Chapter 10"),
    ("Student Name", "M Gouthami"),
    ("Registration Number", "24BTRCL130 (CVIP AIML-B)"),
    ("Lab Topics", "Lab 10.1 (Bank Transfer) & Lab 10.2 (Inventory Reservation)"),
    ("Docker Hub Repository", "https://hub.docker.com/r/gouthudocker/nosql-lab10"),
    ("Docker Image Tag", "gouthudocker/nosql-lab10:latest"),
    ("Database Engine", "MongoDB 7.0 Replica Set (rs0, WiredTiger)"),
    ("Web Platform Integration", "Interactive Flask Dashboard (Port 5000)"),
]

meta_table = doc.add_table(rows=len(metadata), cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_table.autofit = False

for row_idx, (k, v) in enumerate(metadata):
    cell_k = meta_table.cell(row_idx, 0)
    cell_v = meta_table.cell(row_idx, 1)
    
    cell_k.width = Inches(2.0)
    cell_v.width = Inches(4.5)
    
    set_cell_background(cell_k, "F6F8FA")
    set_cell_background(cell_v, "FFFFFF")
    set_cell_margins(cell_k, 80, 80, 120, 120)
    set_cell_margins(cell_v, 80, 80, 120, 120)
    
    pk = cell_k.paragraphs[0]
    pk.paragraph_format.space_before = Pt(0)
    pk.paragraph_format.space_after = Pt(0)
    rk = pk.add_run(k)
    rk.font.name = "Arial"
    rk.font.size = Pt(9.5)
    rk.font.bold = True
    rk.font.color.rgb = COLOR_DARK
    
    pv = cell_v.paragraphs[0]
    pv.paragraph_format.space_before = Pt(0)
    pv.paragraph_format.space_after = Pt(0)
    rv = pv.add_run(v)
    rv.font.name = "Arial"
    rv.font.size = Pt(9.5)
    rv.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

def add_heading_1(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(4)
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY
    return h

def add_heading_2(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(3)
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = COLOR_SECONDARY
    return h

def add_paragraph(text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = "Arial"
        rb.font.size = Pt(10)
        rb.font.bold = True
        rb.font.color.rgb = COLOR_DARK
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(10)
    r.font.color.rgb = COLOR_DARK
    return p

def add_code_block(code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F6F8FA")
    set_cell_margins(cell, 100, 100, 140, 140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(36, 41, 47)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ── Section 1: Executive Summary & Objectives ──────────────────────────────
add_heading_1("1. Executive Summary & Lab Objectives")
add_paragraph(
    "MongoDB introduced multi-document ACID transactions starting in version 4.0 using the WiredTiger storage engine. "
    "Unlike relational databases where transactions span arbitrary tables by default, MongoDB requires multi-document "
    "transactions to execute within an explicit replica set (or sharded cluster) using PyMongo ClientSessions."
)
add_paragraph("The core objectives executed and evaluated in this laboratory comprise:")
add_paragraph(" Building an atomic bank transfer system across accounts, validating fund sufficiency, enforcing automatic rollback on overdrafts, and adding exponential-backoff retry logic for transient conflicts.", bold_prefix="• Lab 10.1: ")
add_paragraph(" Designing an e-commerce stock reservation system across inventory and orders collections using optimistic concurrency control (document versioning) and benchmarking throughput under concurrent thread loads.", bold_prefix="• Lab 10.2: ")
add_paragraph(" Deploying a full-stack interactive web application running in Docker to demonstrate both transaction workflows in real time for grading.", bold_prefix="• Interactive Web System: ")

# ── Section 2: Environment & Architecture ──────────────────────────────────
add_heading_1("2. Containerized Architecture & Environment")
add_paragraph(
    "Because MongoDB multi-document transactions require a replica set, a multi-container Docker Compose "
    "environment was engineered to orchestrate the database and web demonstration:"
)

arch_table = doc.add_table(rows=4, cols=4)
arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Container", "Base Image", "Role", "Ports / Network"]
for i, h in enumerate(headers):
    c = arch_table.cell(0, i)
    set_cell_background(c, "00684A")
    set_cell_margins(c, 80, 80, 100, 100)
    p = c.paragraphs[0]
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(9.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

services = [
    ("mongo_rs0", "mongo:7.0", "MongoDB Primary running with --replSet rs0 --bind_ip_all", "27017:27017"),
    ("rs_init", "mongo:7.0", "Ephemeral container running mongosh to initiate rs0 and wait for primary", "Internal"),
    ("nosql_lab10_web", "nosql-lab10:latest", "Python 3.11 web app container running Flask REST API and UI", "5000:5000"),
]

for row_idx, s in enumerate(services, start=1):
    for col_idx, text in enumerate(s):
        c = arch_table.cell(row_idx, col_idx)
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
        set_cell_background(c, bg)
        set_cell_margins(c, 60, 60, 100, 100)
        p = c.paragraphs[0]
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9)
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ── Section 3: Lab 10.1 ────────────────────────────────────────────────────
add_heading_1("3. Lab 10.1: Bank Transfer Transaction System")
add_heading_2("3.1 Data Modeling")
add_paragraph("The bank database maintains two collections: accounts and transactions.")
add_code_block("""// accounts document schema
{
  "account_id": "ACC-001",
  "holder": "Arjun",
  "balance": 5000.00,
  "version": 0
}

// transactions document schema (Audit Trail)
{
  "from": "ACC-001",
  "to": "ACC-002",
  "amount": 1500.00,
  "description": "Salary payment",
  "timestamp": 1731848445.12
}""")

add_heading_2("3.2 Implementation & Rollback Mechanics")
add_paragraph(
    "The transaction operates inside a PyMongo ClientSession configured with snapshot read concern and "
    "majority write concern. The debit operation applies a conditional query filter {'balance': {'$gte': amount}}."
)
add_code_block("""def transfer_funds(col, from_id, to_id, amount, description=""):
    client = col.database.client
    for attempt in range(MAX_RETRIES):
        session = client.start_session()
        try:
            with session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority"),
            ):
                # 1. Debit sender conditionally
                result = col.update_one(
                    {"account_id": from_id, "balance": {"$gte": amount}},
                    {"$inc": {"balance": -amount, "version": 1}},
                    session=session
                )
                if result.matched_count == 0:
                    raise ValueError(f"Insufficient funds in {from_id} (need ${amount:.2f})")

                # 2. Credit receiver
                col.update_one(
                    {"account_id": to_id},
                    {"$inc": {"balance": amount, "version": 1}},
                    session=session
                )

                # 3. Insert transaction audit log
                col.database["transactions"].insert_one({
                    "from": from_id, "to": to_id, "amount": amount,
                    "description": description, "timestamp": time.time()
                }, session=session)

            return True

        except ValueError as e:
            # Business logic failure: triggers automatic transaction rollback
            print(f"  [ROLLBACK] {e}")
            return False

        except (OperationFailure, PyMongoError) as e:
            labels = getattr(e, "error_labels", []) or []
            if "TransientTransactionError" in labels and attempt < MAX_RETRIES - 1:
                delay = 0.1 * (2 ** attempt) + random.uniform(0, 0.05)
                time.sleep(delay)
            else:
                return False
        finally:
            session.end_session()""")

add_heading_2("3.3 Activity: Exponential Backoff Retry")
add_paragraph(
    "To handle transient write locks and cluster leadership re-elections, the transaction wrapper inspects "
    "the error_labels attribute on OperationFailure. If labeled TransientTransactionError, the operation backs off "
    "exponentially using delay = 0.1 * 2^attempt + jitter, avoiding thundering-herd lock contention."
)

add_heading_2("3.4 Execution Results (Lab 10.1)")
add_code_block("""=======================================
  Lab 10.1: Bank Transfer Transaction
=======================================
  [OK] Created 3 accounts.
  Current Balances:
    ACC-001: Arjun        $  5,000.00
    ACC-002: Sneha        $  3,000.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $1500: ACC-001 -> ACC-002 ===
  [OK] Transferred $1500.00: ACC-001 -> ACC-002  (attempt 1)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,500.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $5000: ACC-003 -> ACC-001 (should ROLLBACK) ===
  [ROLLBACK] Insufficient funds in ACC-003 (need $5000.00)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,500.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $500: ACC-002 -> ACC-003 ===
  [OK] Transferred $500.00: ACC-002 -> ACC-003  (attempt 1)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,000.00
    ACC-003: Rahul        $  1,500.00

=== Transaction Audit Log ===
  ACC-001 -> ACC-002  $1500.00  (Salary payment)
  ACC-002 -> ACC-003  $500.00   (Expense reimbursement)
=====================
  Lab 10.1 Complete
=====================""")

# ── Section 4: Lab 10.2 ────────────────────────────────────────────────────
add_heading_1("4. Lab 10.2: Inventory Reservation with Deadlock Handling")
add_heading_2("4.1 Optimistic Concurrency Control (OCC)")
add_paragraph(
    "In high-traffic e-commerce systems, inventory reservations span two distinct collections: products and orders. "
    "Using transactions alone can suffer from race conditions unless version checking is applied. We employ Optimistic "
    "Concurrency Control (OCC) by reading the document's version and performing a conditional increment."
)
add_code_block("""def _do_reserve(db, product_id, customer_id, qty, session):
    item = db.products.find_one({"product_id": product_id}, session=session)
    if item["stock"] < qty:
        raise ValueError(f"Insufficient stock: have {item['stock']}, need {qty}")

    # Optimistic concurrency check: match version
    result = db.products.update_one(
        {"product_id": product_id, "version": item["version"]},
        {"$inc": {"stock": -qty, "version": 1}},
        session=session
    )
    if result.matched_count == 0:
        raise WriteConflict("Version mismatch - concurrent modification")

    # Insert order atomically within the same transaction
    order_id = str(uuid.uuid4())
    db.orders.insert_one({
        "order_id": order_id,
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "qty": qty, "price": item["price"]}],
        "status": "pending",
        "total": item["price"] * qty,
        "created_at": time.time()
    }, session=session)
    return order_id""")

add_heading_2("4.2 Concurrency Benchmark & Throughput Sweep")
add_paragraph(
    "Simultaneous threads competed for an initial stock of 5 units using Python's ThreadPoolExecutor. "
    "The retry loop catches WriteConflict and TransientTransactionError, retrying with exponential backoff."
)

sweep_table = doc.add_table(rows=5, cols=7)
sweep_table.alignment = WD_TABLE_ALIGNMENT.CENTER
sweep_headers = ["Threads", "Successes", "Failures", "Remaining Stock", "Orders", "Elapsed (s)", "Throughput (TPS)"]
for i, h in enumerate(sweep_headers):
    c = sweep_table.cell(0, i)
    set_cell_background(c, "0969DA")
    set_cell_margins(c, 70, 70, 80, 80)
    p = c.paragraphs[0]
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(8.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

bench_data = [
    ("1", "1", "0", "4", "1", "0.025", "39.29"),
    ("4", "4", "0", "1", "4", "0.401", "9.98"),
    ("8", "5", "3", "0", "5", "0.416", "12.02"),
    ("16", "5", "11", "0", "5", "0.195", "25.66"),
]

for row_idx, d in enumerate(bench_data, start=1):
    for col_idx, val in enumerate(d):
        c = sweep_table.cell(row_idx, col_idx)
        bg = "FFFFFF" if row_idx % 2 == 1 else "F6F8FA"
        set_cell_background(c, bg)
        set_cell_margins(c, 50, 50, 80, 80)
        p = c.paragraphs[0]
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(6)

add_heading_2("4.3 Analysis: Multi-Document Transactions vs. findAndModify")
add_paragraph(
    "• Multi-Document Transactions (Implemented): Ensure that inventory is decremented if and only if "
    "an order document is successfully created. In the event of system failure, network abort, or duplicate key conflict, "
    "the inventory decrement rolls back completely, preventing inventory leakage."
)
add_paragraph(
    "• Single-Document findAndModify: Provides higher raw single-document throughput by avoiding global transaction "
    "locks, but cannot guarantee multi-collection atomicity. If a crash occurs between stock decrement and order creation, "
    "stock is permanently lost with no order record."
)

# ── Section 5: Web Integration ─────────────────────────────────────────────
add_heading_1("5. Web Application Integration & Demonstration")
add_paragraph(
    "A responsive Flask web dashboard is integrated at http://localhost:5000, allowing live interactive demonstration "
    "of both transactions without needing terminal access:"
)

web_table = doc.add_table(rows=5, cols=3)
web_table.alignment = WD_TABLE_ALIGNMENT.CENTER
web_headers = ["Endpoint", "UI View", "Features & Functionality"]
for i, h in enumerate(web_headers):
    c = web_table.cell(0, i)
    set_cell_background(c, "00684A")
    set_cell_margins(c, 70, 70, 90, 90)
    p = c.paragraphs[0]
    r = p.add_run(h)
    r.font.name = "Arial"
    r.font.size = Pt(9)
    r.font.bold = True
    r.font.color.rgb = RGBColor(255, 255, 255)

routes = [
    ("/", "System Dashboard", "Architecture overview, system status, navigation cards"),
    ("/lab1", "Bank Transfer Portal", "Account cards, transfer form, one-click rollback test button, live audit ledger"),
    ("/lab2", "Inventory Portal", "Visual stock progress bars, single order form, concurrent stress tester (4-16 threads)"),
    ("/health", "Health API", "MongoDB replica set ping check (returns {'status': 'ok', 'mongo': 'connected'})"),
]

for row_idx, d in enumerate(routes, start=1):
    for col_idx, val in enumerate(d):
        c = web_table.cell(row_idx, col_idx)
        bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
        set_cell_background(c, bg)
        set_cell_margins(c, 50, 50, 90, 90)
        p = c.paragraphs[0]
        r = p.add_run(val)
        r.font.name = "Arial"
        r.font.size = Pt(8.5)
        r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ── Section 6: Instructions for Demonstration ──────────────────────────────
add_heading_1("6. Grading Demonstration Instructions")
add_paragraph("To run the project on any grading computer:")
add_code_block("""# 1. Start the entire replica set & web app
docker compose up --build -d

# 2. Open the web interface in a browser
http://localhost:5000

# 3. (Optional) Run CLI test scripts inside the container
docker exec nosql_lab10_web python /app/lab_01_bank_transfer.py
docker exec nosql_lab10_web python /app/lab_02_inventory_reservation.py

# 4. Stop environment when finished
docker compose down""")

# ── Section 7: Conclusion ──────────────────────────────────────────────────
add_heading_1("7. Conclusion")
add_paragraph(
    "Through this lab, we successfully demonstrated that MongoDB 7.0 multi-document transactions deliver robust ACID "
    "guarantees across distributed collections. By pairing ClientSession snapshot transactions with Optimistic Concurrency "
    "Control and exponential-backoff retry loops, applications can eliminate race conditions, prevent phantom stock reservations, "
    "and maintain absolute data integrity under heavy concurrent write loads."
)

output_path = "/app/Lab_10_Report.docx"
doc.save(output_path)
print(f"Report saved to {output_path}")
