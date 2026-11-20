"""Generates the comprehensive technical laboratory report for NoSQL Lab 15:
Multi-Tenant API Architecture & Tenant Migration Strategies.
Author: M Gouthami (24BTRCL130)
"""

import os
import sys
import shutil
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

base_dir = os.path.dirname(os.path.abspath(__file__))
desktop_dir = os.path.dirname(base_dir)

doc = Document()

# Page Margins
for section in doc.sections:
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

# Color Palette
COLOR_PRIMARY = RGBColor(0, 104, 74)     # Emerald Green #00684A
COLOR_SECONDARY = RGBColor(9, 105, 218)  # Blue #0969DA
COLOR_DARK = RGBColor(31, 35, 40)        # Dark Charcoal #1F2328
COLOR_GRAY = RGBColor(87, 96, 106)       # Muted Gray #57606A
COLOR_RED = RGBColor(207, 34, 46)        # Danger Red #CF222E
COLOR_ORANGE = RGBColor(194, 85, 0)      # Amber / Orange

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

def add_header(title, subtitle):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, "001E2B")
    set_cell_margins(cell, top=200, bottom=200, left=250, right=250)

    p1 = cell.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n")
    r1.font.name = "Arial"
    r1.font.size = Pt(9.5)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0, 237, 100)

    r2 = p1.add_run(f"{title}\n")
    r2.font.name = "Arial"
    r2.font.size = Pt(14)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(255, 255, 255)

    r3 = p1.add_run(subtitle)
    r3.font.name = "Arial"
    r3.font.size = Pt(10)
    r3.font.italic = True
    r3.font.color.rgb = RGBColor(209, 213, 219)

def add_docker_box(docker_url):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, "E6F7EF")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

    p = cell.paragraphs[0]
    r_hdr = p.add_run("★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION & GRADING ★\n")
    r_hdr.font.name = "Arial"
    r_hdr.font.size = Pt(11)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = COLOR_PRIMARY

    p.add_run("Docker Hub Repository: ").font.bold = True
    r_url = p.add_run(f"{docker_url}\n")
    r_url.font.bold = True
    r_url.font.color.rgb = COLOR_SECONDARY

    p.add_run("Docker Pull Command: ").font.bold = True
    r_cmd = p.add_run(f"docker pull gouthudocker/nosql-lab15:latest\n")
    r_cmd.font.name = "Consolas"
    r_cmd.font.size = Pt(9.5)

    p.add_run("Interactive Web Dashboard: ").font.bold = True
    r_port = p.add_run("http://localhost:5005 (or container port 5000)\n")
    r_port.font.bold = True
    r_port.font.color.rgb = COLOR_PRIMARY

    p.add_run("Submission Note: ").font.bold = True
    p.add_run("The uploaded Docker container has been verified and includes all completed lab activities, REST API, interactive BOLA security testbed, and data migration studio.")

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = COLOR_PRIMARY

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_SECONDARY

def add_body(text, bold_prefix=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(9.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_DARK
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(9.5)
    r.font.italic = italic
    r.font.color.rgb = COLOR_DARK
    return p

def add_code_block(code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, "0F172A")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(163, 230, 53)

# ── Build Document ─────────────────────────────────────────────────────────────

add_header(
    "NoSQL Database Laboratory — Lab 15\nMulti-Tenant API Architecture & Tenant Migration Strategies",
    "Student: M Gouthami | Register No: 24BTRCL130 | Course: NoSQL Database Systems"
)
doc.add_paragraph()

add_docker_box("https://hub.docker.com/r/gouthudocker/nosql-lab15")
doc.add_paragraph()

# Section 1
add_heading_1("1. Executive Summary & Lab Objectives")
add_body(
    "In cloud software-as-a-service (SaaS) architectures, multi-tenancy dictates how infrastructure and data are "
    "partitioned among diverse organizational customers. MongoDB offers three primary isolation models: "
    "(1) Shared Collection with tenant_id discriminant, (2) Collection-per-Tenant, and (3) Database-per-Tenant. "
    "This laboratory explores the design, security, and migration mechanics between these isolation tiers through two core activities:\n"
    "• Activity 1 (lab_01_multitenant_api.py): Implements a tenant-scoped CRUD API and a database-native rate limiter in MongoDB, "
    "proving why compound query filtering ({_id: task_id, tenant_id: tenant_id}) is the fundamental security boundary stopping BOLA.\n"
    "• Activity 2 (lab_02_tenant_migration.py): Implements an enterprise data migration pipeline moving a specific tenant from a "
    "shared collection (saas_app.tasks) into a dedicated database (tenant_acme.tasks) with dry-run planning, upsert-based idempotency proofs, "
    "SHA-256 cryptographic verification, and lossless zero-risk rollback."
)

# Section 2
add_heading_1("2. Activity 1: Design a Multi-Tenant API (lab_01_multitenant_api.py)")
add_heading_2("2.1 Shared-Collection Isolation & The Crux of Tenant Scoping")
add_body(
    "Shared-collection isolation places all documents across all tenants into a single collection (saas_app.tasks). "
    "Because MongoDB does not inherently possess tenant awareness, every read, write, update, and delete operation must "
    "explicitly incorporate {'tenant_id': tenant_id} in its filter. Without this, operations cross tenant boundaries."
)

add_heading_2("2.2 Pre-Activity Analysis: Concretely Identifying the Flaw in Unscoped Updates")
add_body(
    "Question Posed: Before reading update_task's implementation: write down what would go wrong -- concretely, with an example -- "
    "if its filter only checked {'_id': task_id} without also checking tenant_id. Then confirm that scenario is exactly what the actual filter prevents."
)
add_body(
    "Concrete Vulnerability Scenario (Broken Object Level Authorization / BOLA / IDOR):\n"
    "1. Suppose tenant-acme creates a critical task with ObjectID '655a1b2c3d4e5f0011223344' titled 'Setup ML Pipeline'.\n"
    "2. Tenant-globex (a hostile or curious tenant) discovers or guesses this ObjectID via sequential enumeration, shared logs, or public references.\n"
    "3. Tenant-globex submits an update request: PUT /api/tasks/655a1b2c3d4e5f0011223344 with payload {'status': 'deleted'}.\n"
    "4. If the database update filter was merely col.update_one({'_id': task_id}, {'$set': updates}), MongoDB locates the document by ID and applies the update, "
    "unaware that the request originated from Globex.\n"
    "5. Consequence: Globex successfully closes, alters, or destroys Acme's private enterprise tasks without authorization.\n\n"
    "Prevention in Lab 15.1:\n"
    "The secure implementation specifies col.update_one({'_id': task_id, 'tenant_id': tenant_id}, {'$set': updates}). "
    "When Globex attempts to update Acme's task, MongoDB searches for a document where _id matches AND tenant_id equals 'tenant-globex'. "
    "Because the document's tenant_id is 'tenant-acme', 0 documents match. matched_count is 0, modified_count is 0, and the operation is completely thwarted."
)

add_heading_2("2.3 Database-Native Rate Limiting Pattern")
add_body(
    "Rather than deploying an external Redis caching layer, check_rate_limit leverages MongoDB directly by logging request timestamps in "
    "saas_app.rate_limits. When a request arrives, it computes cutoff = time.time() - window_secs and counts documents for that tenant within "
    "the sliding window. If count >= limit (e.g. 10 requests in 60s), the request is rejected with False (HTTP 429). Otherwise, the timestamp is recorded."
)

add_heading_2("2.4 Activity 1 Terminal Execution Output")
add_code_block("""=======================================
  [LAB 15] Lab 15.1: Multi-Tenant SaaS API
=======================================
=== Creating Tasks ===
  Created 4 tasks across 2 tenants.

=== tenant-acme Tasks ===
  [high  ] Setup ML Pipeline              (open) -> arjun
  [medium] Data Validation                (open) -> sneha

=== tenant-globex Tasks ===
  [high  ] API Integration                (open) -> rahul
  [low   ] User Testing                   (open) -> None

=== Update: Close ML Pipeline task ===
  Update success: True

=== Cross-Tenant Access Attempt (should fail) ===
  Globex trying to update Acme's task: False (False = blocked!)

=== Rate Limiting (10 req/60s) ===
  Request  1: ALLOWED
  Request  2: ALLOWED
  Request  3: ALLOWED
  Request  4: ALLOWED
  Request  5: ALLOWED
  Request  6: ALLOWED
  Request  7: ALLOWED
  Request  8: ALLOWED
  Request  9: ALLOWED
  Request 10: ALLOWED
  Request 11: RATE LIMITED
  Request 12: RATE LIMITED

=== Multi-Tenant Architecture Comparison ===
┌──────────────────────┬───────────┬──────────────────────────────┬───────────────────────────────┐
│ Approach             │ Isolation │ Pros                         │ Cons                          │
├──────────────────────┼───────────┼──────────────────────────────┼───────────────────────────────┤
│ Collection-per-tenant│ Strong    │ Simple RBAC, easy backup     │ Many collections at scale     │
│ Document tenant_id   │ Medium    │ Single collection, flexible  │ Query must include tenant_id  │
│ Database-per-tenant  │ Strongest │ Full isolation               │ Resource overhead, conn mgmt  │
└──────────────────────┴───────────┴──────────────────────────────┴───────────────────────────────┘
=========================
  [LAB 15] Lab 15.1 Complete
=========================""")

# Section 3
add_heading_1("3. Activity 2: Data Migration Between Isolation Strategies (lab_02_tenant_migration.py)")
add_heading_2("3.1 Architectural Context & Need for Tier Transitions")
add_body(
    "A standard SaaS startup typically launches on shared collections (Document tenant_id) to optimize infrastructure costs. "
    "However, acquiring enterprise accounts introduces stringent regulatory (HIPAA, GDPR, SOC2) and physical partitioning requirements. "
    "Activity 2 implements an online migration pipeline that moves tenant-acme from saas_app.tasks into a dedicated database tenant_acme.tasks."
)

add_heading_2("3.2 Pre-Activity Analysis: Idempotency & Document Count Prediction")
add_body(
    "Question Posed: Before running the second (repeat) migration: predict whether the tenant's document count in the new database will double, "
    "stay the same, or something else. Then run it and confirm against the printed target_count."
)
add_body(
    "Prediction & Technical Proof:\n"
    "• Prediction: The tenant's document count in the target database will STAY EXACTLY THE SAME (2 documents).\n"
    "• Detailed Reason: If the migration utilized standard insert_one() or insert_many(), re-running the migration would append documents "
    "with new MongoDB ObjectIDs, doubling the count from 2 to 4.\n"
    "• However, the migration utilizes an idempotent upsert keyed on natural business identity:\n"
    "  target_col.update_one({'tenant_id': doc['tenant_id'], 'title': doc['title']}, {'$set': doc}, upsert=True)\n"
    "• On the first pass, MongoDB finds no matching document and inserts the record.\n"
    "• On the repeat pass, MongoDB matches the existing document by (tenant_id, title) and performs an in-place update with $set. "
    "No new documents are inserted. The target count remains exactly 2."
)

add_heading_2("3.3 Verification & Lossless Rollback Pattern")
add_body(
    "Operational Safety Pillars in Lab 15.2:\n"
    "1. Dry-Run Mode (--dry-run): Calculates document volume and valid target database name without performing any database writes.\n"
    "2. Cryptographic Checksums: Computes SHA-256 hash of sorted serialized documents for both source and target to verify data integrity down to the byte.\n"
    "3. Copy-First Semantics: Documents in saas_app.tasks are copied, NEVER deleted during migration.\n"
    "4. Safe Rollback (--rollback): Dropping tenant_acme drops solely the replica. The original shared collection remains 100% intact with zero data loss."
)

add_heading_2("3.4 Activity 2 Terminal Execution Output")
add_code_block("""====================================================================
  [LAB 15] Lab 15.2: Data Migration Between Tenant Isolation Strategies
====================================================================
=== Step 1: Seed shared-collection baseline (from Lab 15.1) ===
  [OK] Seeded shared collection 'saas_app.tasks' for tenant-acme and tenant-globex.

=== Step 2: Migrate 'tenant-acme' (LIVE) ===
                       Tenant Migration Summary                       
┌─────────────┬──────────┬─────────────┬──────────────┬──────────────┐
│ Tenant      │ Status   │ Target DB   │ Source Count │ Target Count │
├─────────────┼──────────┼─────────────┼──────────────┼──────────────┤
│ tenant-acme │ MIGRATED │ tenant_acme │            2 │            2 │
└─────────────┴──────────┴─────────────┴──────────────┴──────────────┘

=== Step 3: Re-run migration to prove it's idempotent ===
                       Tenant Migration Summary                       
┌─────────────┬──────────┬─────────────┬──────────────┬──────────────┐
│ Tenant      │ Status   │ Target DB   │ Source Count │ Target Count │
├─────────────┼──────────┼─────────────┼──────────────┼──────────────┤
│ tenant-acme │ MIGRATED │ tenant_acme │            2 │            2 │
└─────────────┴──────────┴─────────────┴──────────────┴──────────────┘
  [OK] Re-running did not create duplicates -- migration is idempotent.

  Shared collection still has the original documents (migration copies, it doesn't move-and-delete, until you
  explicitly clean up the source after confirming the new tier is stable).

  To undo this migration: python chapter-15/lab_02_tenant_migration.py --tenant tenant-acme --rollback
=========================
  [LAB 15] Lab 15.2 Complete
=========================""")

# Section 4
add_heading_1("4. Web Application Integration & Demonstration Platform")
add_body(
    "To provide an enterprise-grade demonstration experience, all laboratory tasks were integrated into a unified Flask web application "
    "hosted on port 5005 (container port 5000):\n"
    "• Dashboard Overview (index.html): Live cluster status, active tenants, shared collection metrics, and dedicated database monitor.\n"
    "• Activity 1 Console (lab1.html): Tenant context switcher, real-time CRUD task manager, interactive BOLA exploit simulator comparing "
    "vulnerable vs secure query filters, and a sliding-window rate limit tester with 12-request burst generator.\n"
    "• Activity 2 Migration Studio (lab2.html): 4-step migration lifecycle controls (Dry-Run, Live Migration, Idempotency Test, Rollback) with "
    "a side-by-side live document viewer and real-time SHA-256 cryptographic checksum matching.\n"
    "• Architecture & REST API Docs (architecture.html): Full technical documentation of API endpoints with cURL testing snippets."
)

# Section 5
add_heading_1("5. Docker Containerization & Demonstration Guide")
add_body(
    "The application was packaged into a production-grade multi-architecture Docker container and pushed to Docker Hub for grading demonstration.\n"
    "• Docker Hub Repository URL: https://hub.docker.com/r/gouthudocker/nosql-lab15\n"
    "• Docker Image Tags: gouthudocker/nosql-lab15:latest, gouthudocker/nosql-lab15:v1.0\n"
    "• Host Port: 5005 (maps to 5000 in container)"
)

add_heading_2("5.1 How to Pull and Run the Docker Demonstration")
add_code_block("""# 1. Pull the verified Docker image from Docker Hub
docker pull gouthudocker/nosql-lab15:latest

# 2. Run the container connected to MongoDB (or standalone with local host network)
docker run -d --name nosql_lab15_demo -p 5005:5000 \\
  -e MONGO_URI="mongodb://localhost:27017/" \\
  gouthudocker/nosql-lab15:latest

# 3. Access the interactive web dashboard in your browser
http://localhost:5005/

# 4. Or execute the lab scripts directly inside the running container:
docker exec -it nosql_lab15_demo python lab_01_multitenant_api.py
docker exec -it nosql_lab15_demo python lab_02_tenant_migration.py --dry-run
docker exec -it nosql_lab15_demo python lab_02_tenant_migration.py
docker exec -it nosql_lab15_demo python lab_02_tenant_migration.py --rollback""")

# Section 6
add_heading_1("6. Conclusion & Key Learning Outcomes")
add_body(
    "1. Application-Level vs Physical Isolation: Shared collections provide high density and low cost but require strict query discipline. "
    "Compound filtering on {_id: id, tenant_id: tenant} is indispensable to eliminate BOLA / IDOR vulnerabilities.\n"
    "2. Database-Native Observability & Rate Limiting: High-performance rate limiting can be implemented directly within MongoDB using "
    "sliding window timestamp queries, avoiding external cache dependencies for moderate scale.\n"
    "3. Migration Idempotency: Designing migrations around natural composite keys and upserts ensures resilience against network partitions "
    "and failed retry attempts without duplicating state.\n"
    "4. Safe Operations via Non-Destructive Copy: Maintaining the original shared data until physical verification guarantees zero-risk rollback."
)

# Save document
docx_path = os.path.join(base_dir, "Lab_15_Report.docx")
desktop_docx = os.path.join(desktop_dir, "Lab_15_Report.docx")
doc.save(docx_path)
shutil.copy(docx_path, desktop_docx)
print(f"Report saved to {docx_path} and {desktop_docx}")
