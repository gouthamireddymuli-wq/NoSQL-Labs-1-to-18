"""Direct ReportLab PDF Generator for NoSQL Lab 15 Submission Report.
Produces Lab_15_Report.pdf and NoSQL_Lab15_Submission.pdf with high fidelity.
Author: M Gouthami (24BTRCL130)
"""

import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.units import inch

base_dir = os.path.dirname(os.path.abspath(__file__))
desktop_dir = os.path.dirname(base_dir)

pdf_path = os.path.join(base_dir, "Lab_15_Report.pdf")
sub_pdf_path = os.path.join(base_dir, "NoSQL_Lab15_Submission.pdf")
desktop_sub_pdf = os.path.join(desktop_dir, "NoSQL_Lab15_Submission.pdf")

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=45, leftMargin=45,
    topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

# Custom styles
header_title_style = ParagraphStyle(
    'HeaderTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=14,
    textColor=colors.white,
    alignment=1, # Center
    spaceAfter=4
)

header_sub_style = ParagraphStyle(
    'HeaderSub',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    textColor=colors.HexColor('#00ED64'),
    alignment=1,
    spaceAfter=2
)

header_meta_style = ParagraphStyle(
    'HeaderMeta',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    textColor=colors.HexColor('#D1D5DB'),
    alignment=1
)

h1_style = ParagraphStyle(
    'H1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=11.5,
    textColor=colors.HexColor('#00684A'),
    spaceBefore=9,
    spaceAfter=3
)

h2_style = ParagraphStyle(
    'H2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=9.5,
    textColor=colors.HexColor('#0969DA'),
    spaceBefore=6,
    spaceAfter=2
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor('#1F2328')
)

bullet_style = ParagraphStyle(
    'Bullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#1F2328')
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=7.2,
    leading=9.5,
    textColor=colors.HexColor('#A3E635')
)

elements = []

# ── Header Box ─────────────────────────────────────────────────────────────────
header_data = [
    [Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", header_sub_style)],
    [Paragraph("NoSQL Database Laboratory — Lab 15<br/>Multi-Tenant API Architecture & Tenant Migration Strategies", header_title_style)],
    [Paragraph("Student: <b>M Gouthami</b> | Register No: <b>24BTRCL130</b> | Academic Year: 2026-2027", header_meta_style)]
]
header_table = Table(header_data, colWidths=[520])
header_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#001E2B')),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 12),
    ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
]))
elements.append(header_table)
elements.append(Spacer(1, 8))

# ── Docker Hub Callout Box ─────────────────────────────────────────────────────
callout_content = """
<b><font color="#00684A" size="9.5">★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION & GRADING ★</font></b><br/>
<b>Docker Hub Repository:</b> <font color="#0969DA"><b>https://hub.docker.com/r/gouthudocker/nosql-lab15</b></font><br/>
<b>Docker Pull Command:</b> <font face="Courier">docker pull gouthudocker/nosql-lab15:latest</font><br/>
<b>Interactive Web UI Port:</b> <font color="#00684A"><b>http://localhost:5005</b></font> (or port 5000 inside container)<br/>
<b>Submission Verification:</b> Pre-built Docker container includes completed Lab 15.1 and 15.2 scripts, interactive BOLA attack simulator, database-native rate limiter, live migration engine, and full REST API.
"""
callout_table = Table([[Paragraph(callout_content, body_style)]], colWidths=[520])
callout_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E6F7EF')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#00ED64')),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
]))
elements.append(callout_table)
elements.append(Spacer(1, 8))

# ── 1. Executive Summary & Lab Objectives ──────────────────────────────────────
elements.append(Paragraph("1. Executive Summary & Lab Objectives", h1_style))
elements.append(Paragraph(
    "Multi-tenancy is the architectural cornerstone of cloud SaaS platforms. This laboratory investigates "
    "the design, security boundaries, and operational lifecycle of multi-tenant NoSQL database systems in MongoDB. "
    "The lab is structured into two complementary activities:",
    body_style
))
elements.append(Paragraph(
    "• <b>Activity 1 (lab_01_multitenant_api.py):</b> Explores Shared-Collection isolation, implementing a tenant-scoped "
    "CRUD task API and a database-native rate limiter directly in MongoDB. It proves mathematically and practically why "
    "compound filtering (<font face='Courier'>{\"_id\": task_id, \"tenant_id\": tenant_id}</font>) is critical to eliminate "
    "Broken Object Level Authorization (BOLA / IDOR).",
    bullet_style
))
elements.append(Paragraph(
    "• <b>Activity 2 (lab_02_tenant_migration.py):</b> Solves the enterprise isolation upgrade problem by migrating a tenant "
    "from a shared collection (<font face='Courier'>saas_app.tasks</font>) to a dedicated physical database "
    "(<font face='Courier'>tenant_acme.tasks</font>) with dry-run planning, upsert-based idempotency proofs, SHA-256 "
    "cryptographic checksum verification, and zero-data-loss rollback.",
    bullet_style
))
elements.append(Spacer(1, 6))

# ── 2. Activity 1: Design a Multi-Tenant API ──────────────────────────────────
elements.append(Paragraph("2. Activity 1: Design a Multi-Tenant API (lab_01_multitenant_api.py)", h1_style))
elements.append(Paragraph("2.1 Shared-Collection Isolation & Scoping Filter", h2_style))
elements.append(Paragraph(
    "Shared-collection isolation represents the lowest-cost operational tier where all tenant records reside in "
    "one collection distinguished by <font face='Courier'>tenant_id</font>. Because MongoDB does not enforce tenant "
    "scoping natively, application queries must explicitly enforce tenant boundaries.",
    body_style
))

elements.append(Paragraph("2.2 Pre-Activity Analysis: Cross-Tenant Vulnerability Concrete Scenario", h2_style))
elements.append(Paragraph(
    "<b>Prompt Question:</b> Write down what would go wrong -- concretely, with an example -- if its filter only checked "
    "{\"_id\": task_id} without also checking tenant_id. Then confirm that scenario is exactly what the actual filter prevents.<br/>"
    "<b>Concrete Vulnerability Scenario (Broken Object Level Authorization / BOLA):</b><br/>"
    "1. <b>Acme Corporation</b> creates task <font face='Courier'>t1</font> ('Setup ML Pipeline') with ObjectID <font face='Courier'>655a1b...</font> in <font face='Courier'>saas_app.tasks</font>.<br/>"
    "2. <b>Globex Corporation</b> (a competing tenant) guesses, snoops, or discovers ObjectID <font face='Courier'>t1</font>.<br/>"
    "3. Globex issues an authenticated request: <font face='Courier'>PUT /api/tasks/655a1b... {'status': 'deleted'}</font>.<br/>"
    "4. <b>Vulnerable Implementation:</b> If the query is <font face='Courier'>col.update_one({\"_id\": task_id}, ...)</font>, MongoDB successfully matches Acme's document and modifies it. Globex successfully modifies Acme's private enterprise data.<br/>"
    "5. <b>Prevention in Lab 15.1:</b> The actual code enforces <font face='Courier'>col.update_one({\"_id\": task_id, \"tenant_id\": tenant_id}, ...)</font>. When Globex calls the API, its tenant context <font face='Courier'>tenant-globex</font> is injected. MongoDB looks for a document with Acme's ID AND tenant Globex. It matches 0 documents (<font face='Courier'>matched_count=0</font>), completely blocking the unauthorized tampering.",
    body_style
))

elements.append(Paragraph("2.3 Database-Native Rate Limiting Pattern", h2_style))
elements.append(Paragraph(
    "Rather than deploying an external Redis cluster, <font face='Courier'>check_rate_limit()</font> implements an upsert-and-count "
    "sliding window in MongoDB <font face='Courier'>saas_app.rate_limits</font>. Requests within <font face='Courier'>cutoff = time.time() - window_secs</font> "
    "are counted. Calls beyond 10 req/60s return <font face='Courier'>False</font> (HTTP 429), maintaining database stability without extra infrastructure.",
    body_style
))

# Activity 1 Output Box
code1_text = """=======================================
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
  Request  1..10: ALLOWED
  Request 11..12: RATE LIMITED (429)"""

c1_table = Table([[Paragraph(code1_text.replace('\n', '<br/>'), code_style)]], colWidths=[520])
c1_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
elements.append(c1_table)
elements.append(Spacer(1, 8))

# ── 3. Activity 2: Data Migration Between Tenant Isolation Strategies ─────────
elements.append(Paragraph("3. Activity 2: Data Migration Between Isolation Strategies (lab_02_tenant_migration.py)", h1_style))
elements.append(Paragraph("3.1 Pre-Activity Analysis: Migration Idempotency & Count Prediction", h2_style))
elements.append(Paragraph(
    "<b>Prompt Question:</b> Before running the second (repeat) migration: predict whether the tenant's document count "
    "in the new database will double, stay the same, or something else. Then run it and confirm against the printed target_count.<br/>"
    "<b>Prediction & Technical Proof:</b><br/>"
    "• <b>Prediction:</b> The tenant's document count in the target database will <b>STAY EXACTLY THE SAME</b> (2 documents).<br/>"
    "• <b>Technical Proof:</b> The migration script avoids blind inserts. Instead, it performs an idempotent upsert keyed on "
    "the natural business identifier: <font face='Courier'>target_col.update_one({\"tenant_id\": doc[\"tenant_id\"], \"title\": doc[\"title\"]}, {\"$set\": doc}, upsert=True)</font>. "
    "On the second run, MongoDB finds the document already present by <font face='Courier'>(tenant_id, title)</font> and updates it in place. "
    "No duplicates are created, and <font face='Courier'>target_count</font> remains exactly 2.",
    body_style
))

elements.append(Paragraph("3.2 Verification, Cryptographic Checksums & Lossless Rollback", h2_style))
elements.append(Paragraph(
    "• <b>Dry-Run Mode (<font face='Courier'>--dry-run</font>):</b> Identifies candidate documents and target database name without performing any writes.<br/>"
    "• <b>Integrity Check:</b> Computes SHA-256 hash of sorted documents. Confirms <font face='Courier'>source_checksum == target_checksum</font>.<br/>"
    "• <b>Lossless Rollback (<font face='Courier'>--rollback</font>):</b> Drops <font face='Courier'>tenant_acme</font> database. Because the migration only copied records, the shared collection remains 100% intact with zero data loss.",
    body_style
))

# Activity 2 Output Box
code2_text = """=== Step 1: Seed shared-collection baseline (from Lab 15.1) ===
  [OK] Seeded shared collection 'saas_app.tasks' for tenant-acme and tenant-globex.

=== Step 2: Migrate 'tenant-acme' (LIVE) ===
  Tenant: tenant-acme | Status: MIGRATED | Target DB: tenant_acme | Source: 2 | Target: 2

=== Step 3: Re-run migration to prove it's idempotent ===
  Tenant: tenant-acme | Status: MIGRATED | Target DB: tenant_acme | Source: 2 | Target: 2
  [OK] Re-running did not create duplicates -- migration is idempotent.

=== Rollback Verification (--rollback) ===
  [OK] Dropped database 'tenant_acme'. Shared collection is untouched."""

c2_table = Table([[Paragraph(code2_text.replace('\n', '<br/>'), code_style)]], colWidths=[520])
c2_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
elements.append(c2_table)
elements.append(Spacer(1, 8))

# ── 4. Web Application & Demonstration Features ───────────────────────────────
elements.append(Paragraph("4. Web Application Integration & Interactive Demonstrations", h1_style))
elements.append(Paragraph(
    "A full-featured Flask web application has been constructed to demonstrate both activities interactively on <b>http://localhost:5005</b>:",
    body_style
))
elements.append(Paragraph(
    "1. <b>Dashboard Overview:</b> Real-time MongoDB health, shared collection metrics, detected tenants, and dedicated databases.<br/>"
    "2. <b>Activity 1 Console:</b> Tenant context switcher, task CRUD table, live BOLA exploit simulator comparing vulnerable vs secure queries, and sliding window rate limit burst tester.<br/>"
    "3. <b>Activity 2 Migration Studio:</b> Interactive buttons for Dry-Run, Live Migration, Idempotency Test, and Rollback, alongside a side-by-side data explorer comparing <font face='Courier'>saas_app.tasks</font> vs <font face='Courier'>tenant_acme.tasks</font> with live SHA-256 checksums.<br/>"
    "4. <b>Architecture & REST API Docs:</b> Complete specification of all endpoints (<font face='Courier'>/api/tasks</font>, <font face='Courier'>/api/security/simulate-attack</font>, <font face='Courier'>/api/migration/*</font>) with cURL commands.",
    bullet_style
))
elements.append(Spacer(1, 6))

# ── 5. Docker Deployment & Demonstration Guide ────────────────────────────────
elements.append(Paragraph("5. Docker Deployment & Demonstration Guide", h1_style))
elements.append(Paragraph(
    "<b>Docker Hub Submission URL:</b> <font color='#0969DA'><b>https://hub.docker.com/r/gouthudocker/nosql-lab15</b></font><br/>"
    "<b>Docker Hub Image:</b> <font face='Courier'>gouthudocker/nosql-lab15:latest</font> (and <font face='Courier'>gouthudocker/nosql-lab15:v1.0</font>)<br/>"
    "<b>Demonstration Commands:</b>",
    body_style
))

code3_text = """# Pull image from Docker Hub
docker pull gouthudocker/nosql-lab15:latest

# Run container exposing port 5005
docker run -d --name nosql_lab15_web -p 5005:5000 \\
  -e MONGO_URI="mongodb://localhost:27017/" \\
  gouthudocker/nosql-lab15:latest

# Access web application
http://localhost:5005/

# Execute CLI scripts inside container for live grading:
docker exec -it nosql_lab15_web python lab_01_multitenant_api.py
docker exec -it nosql_lab15_web python lab_02_tenant_migration.py"""

c3_table = Table([[Paragraph(code3_text.replace('\n', '<br/>'), code_style)]], colWidths=[520])
c3_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
elements.append(c3_table)
elements.append(Spacer(1, 8))

# ── 6. Conclusion ─────────────────────────────────────────────────────────────
elements.append(Paragraph("6. Conclusion", h1_style))
elements.append(Paragraph(
    "This laboratory demonstrated that multi-tenancy in NoSQL databases is not merely an infrastructure choice, "
    "but a fundamental architectural contract. Compound query filtering (<font face='Courier'>{\"_id\": id, \"tenant_id\": tenant}</font>) "
    "is mandatory to prevent Broken Object Level Authorization in shared collections. Furthermore, online migration pipelines "
    "must be designed with natural key upserts to guarantee idempotency and maintain copy-first semantics for lossless rollbacks.",
    body_style
))

doc.build(elements)

# Copy to submission paths
shutil.copy(pdf_path, sub_pdf_path)
shutil.copy(pdf_path, desktop_sub_pdf)
print(f"Generated PDF reports:\n  {pdf_path}\n  {sub_pdf_path}\n  {desktop_sub_pdf}")
