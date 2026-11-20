"""Generates the comprehensive technical laboratory report and submission PDF for NoSQL Lab 14:
MongoDB Monitoring, Automated Backup & Restore Verification.
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

# Title & Metadata Header Block
header_table = doc.add_table(rows=1, cols=1)
header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
header_table.autofit = False
header_table.columns[0].width = Inches(6.8)

cell = header_table.cell(0, 0)
set_cell_background(cell, "001E2B")
set_cell_margins(cell, top=200, bottom=200, left=250, right=250)

p1 = cell.paragraphs[0]
p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
r1 = p1.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
r1.font.name = "Arial"
r1.font.size = Pt(10)
r1.font.bold = True
r1.font.color.rgb = RGBColor(0, 237, 100)

p2 = cell.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = p2.add_run("NoSQL Database Laboratory — Lab 14\nProduction Monitoring, Automated Backup & Restore Verification")
r2.font.name = "Arial"
r2.font.size = Pt(16)
r2.font.bold = True
r2.font.color.rgb = RGBColor(255, 255, 255)

p3 = cell.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
r3 = p3.add_run("Student: M Gouthami  |  Roll No: 24BTRCL130  |  Academic Year: 2026-2027")
r3.font.name = "Arial"
r3.font.size = Pt(10.5)
r3.font.color.rgb = RGBColor(200, 210, 220)

doc.add_paragraph()

# ── Submission & Docker Hub Verification Callout ───────────────────────────
callout_table = doc.add_table(rows=1, cols=1)
callout_table.alignment = WD_TABLE_ALIGNMENT.CENTER
callout_table.columns[0].width = Inches(6.8)
c_cell = callout_table.cell(0, 0)
set_cell_background(c_cell, "E6F7EF")
set_cell_margins(c_cell, top=140, bottom=140, left=200, right=200)

cp = c_cell.paragraphs[0]
cr1 = cp.add_run("★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION & GRADING ★\n")
cr1.font.name = "Arial"
cr1.font.size = Pt(11)
cr1.font.bold = True
cr1.font.color.rgb = COLOR_PRIMARY

cr2 = cp.add_run("Docker Hub Repository: ")
cr2.font.name = "Arial"
cr2.font.size = Pt(10.5)
cr2.font.bold = True

cr3 = cp.add_run("https://hub.docker.com/r/gouthudocker/nosql-lab14\n")
cr3.font.name = "Consolas"
cr3.font.size = Pt(11)
cr3.font.bold = True
cr3.font.color.rgb = COLOR_SECONDARY

cr4 = cp.add_run("Docker Pull Command: ")
cr4.font.name = "Arial"
cr4.font.size = Pt(10.5)
cr4.font.bold = True

cr5 = cp.add_run("docker pull gouthudocker/nosql-lab14:latest\n")
cr5.font.name = "Consolas"
cr5.font.size = Pt(10)
cr5.font.color.rgb = COLOR_DARK

cr6 = cp.add_run("Digest: ")
cr6.font.name = "Arial"
cr6.font.size = Pt(9.5)
cr7 = cp.add_run("sha256:ba055c753bd41f30b8dd2ce92feb1a006bc6c40223e7b04caf2e9d3c725c0c92\n")
cr7.font.name = "Consolas"
cr7.font.size = Pt(9)
cr7.font.color.rgb = COLOR_GRAY

cr8 = cp.add_run("Web Dashboard Port: ")
cr8.font.name = "Arial"
cr8.font.size = Pt(10)
cr8.font.bold = True
cr9 = cp.add_run("http://localhost:5004  (or http://localhost:5000 inside container)")
cr9.font.name = "Consolas"
cr9.font.size = Pt(10)
cr9.font.bold = True
cr9.font.color.rgb = COLOR_PRIMARY

doc.add_paragraph()

# ── Section 1: Note for Grading & Demonstration Instructions ───────────────
h1 = doc.add_heading(level=1)
hr1 = h1.add_run("1. Demonstration & Grading Instructions")
hr1.font.name = "Arial"
hr1.font.size = Pt(13)
hr1.font.bold = True
hr1.font.color.rgb = COLOR_PRIMARY

p_demo = doc.add_paragraph()
p_demo.add_run("The uploaded Docker image encapsulates the complete laboratory solution including MongoDB Database Tools (").font.size = Pt(10)
p_demo.add_run("mongodump").font.bold = True
p_demo.add_run(", ").font.size = Pt(10)
p_demo.add_run("mongorestore").font.bold = True
p_demo.add_run("), monitoring daemon, Rich terminal UI, and interactive Flask web dashboard. Use the following commands to demonstrate:")

# Table of demonstration steps
demo_table = doc.add_table(rows=4, cols=2)
demo_table.alignment = WD_TABLE_ALIGNMENT.CENTER
demo_table.columns[0].width = Inches(2.2)
demo_table.columns[1].width = Inches(4.6)

steps = [
    ("1. Pull Docker Image", "docker pull gouthudocker/nosql-lab14:latest"),
    ("2. Run Interactive Web Container",
     "docker run -d --name nosql_lab14_web -p 5004:5000 \\\n"
     "  --network nosqllab13_default \\\n"
     "  -e MONGO_URI=\"mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin\" \\\n"
     "  gouthudocker/nosql-lab14:latest\n\n"
     "Access web UI: http://localhost:5004"),
    ("3. Run Activity 1 (Monitoring CLI)",
     "docker exec -it nosql_lab14_web python lab_01_monitoring_dashboard.py"),
    ("4. Run Activity 2 (Backup & Verification)",
     "docker exec -it nosql_lab14_web python lab_02_backup_restore.py")
]

for idx, (title, cmd) in enumerate(steps):
    c0 = demo_table.cell(idx, 0)
    c1 = demo_table.cell(idx, 1)
    set_cell_background(c0, "F8FAFC")
    set_cell_background(c1, "0F172A")
    set_cell_margins(c0, 80, 80, 100, 100)
    set_cell_margins(c1, 80, 80, 100, 100)
    
    p0 = c0.paragraphs[0]
    r_t = p0.add_run(title)
    r_t.font.name = "Arial"
    r_t.font.bold = True
    r_t.font.size = Pt(9.5)
    r_t.font.color.rgb = COLOR_DARK
    
    p1 = c1.paragraphs[0]
    r_c = p1.add_run(cmd)
    r_c.font.name = "Consolas"
    r_c.font.size = Pt(8.5)
    r_c.font.color.rgb = RGBColor(163, 230, 53)

doc.add_paragraph()

# ── Section 2: Activity 1 — Monitoring Dashboard Deep Dive ─────────────────
h2 = doc.add_heading(level=1)
hr2 = h2.add_run("2. Activity 1: Production Monitoring Dashboard (lab_01_monitoring_dashboard.py)")
hr2.font.name = "Arial"
hr2.font.size = Pt(13)
hr2.font.bold = True
hr2.font.color.rgb = COLOR_PRIMARY

p_act1 = doc.add_paragraph()
p_act1.add_run(
    "Activity 1 inspects MongoDB's internal metrics via the serverStatus administrative endpoint. "
    "Rather than treating metrics as standalone numbers, production observability requires threshold alerting "
    "and dual logging to separate immediate human inspection from retrospective incident investigation."
).font.size = Pt(10)

act1_table = doc.add_table(rows=5, cols=3)
act1_table.alignment = WD_TABLE_ALIGNMENT.CENTER
act1_table.columns[0].width = Inches(1.8)
act1_table.columns[1].width = Inches(2.2)
act1_table.columns[2].width = Inches(2.8)

headers = ["Metric Category", "Inspected Fields", "Alert Threshold & Rationale"]
for c_idx, h in enumerate(headers):
    c = act1_table.cell(0, c_idx)
    set_cell_background(c, "001E2B")
    set_cell_margins(c, 90, 90, 110, 110)
    pr = c.paragraphs[0].add_run(h)
    pr.font.name = "Arial"
    pr.font.bold = True
    pr.font.size = Pt(9.5)
    pr.font.color.rgb = RGBColor(255, 255, 255)

m_rows = [
    ("Connection Pool", "connections.current\nconnections.available\nconnections.totalCreated",
     "Alert when current > 80% of max incoming limit. Prevents connection exhaustion outages before cascading failure occurs."),
    ("WiredTiger Cache", "bytes currently in cache\nmaximum bytes configured\ntracked dirty bytes\npages read into cache",
     "Alert when cache usage > 80%. High cache fill triggers eviction worker threads, drastically increasing storage I/O latency."),
    ("Operation Counters", "opcounters.insert\nopcounters.query\nopcounters.update\nopcounters.delete\nopcounters.command",
     "Cumulative counters since boot. Monitored continuously to derive QPS/throughput spikes during traffic bursts."),
    ("Replication Lag", "replSetGetStatus\nmembers[].optimeDate\nmembers[].stateStr",
     "Alert when secondary lag > 10,000ms. Guarantees read consistency when routing queries with ReadPreference.secondaryPreferred.")
]

for r_idx, (cat, fields, thresh) in enumerate(m_rows, start=1):
    c0 = act1_table.cell(r_idx, 0)
    c1 = act1_table.cell(r_idx, 1)
    c2 = act1_table.cell(r_idx, 2)
    bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
    for c in (c0, c1, c2):
        set_cell_background(c, bg)
        set_cell_margins(c, 70, 70, 90, 90)
    
    p = c0.paragraphs[0].add_run(cat)
    p.font.name = "Arial"
    p.font.bold = True
    p.font.size = Pt(9)
    
    p = c1.paragraphs[0].add_run(fields)
    p.font.name = "Consolas"
    p.font.size = Pt(8.5)
    
    p = c2.paragraphs[0].add_run(thresh)
    p.font.name = "Arial"
    p.font.size = Pt(8.5)

doc.add_paragraph()

# ── Section 3: Activity 2 — Backup & Restore Verification ──────────────────
h3 = doc.add_heading(level=1)
hr3 = h3.add_run("3. Activity 2: Automated Backup & Restore Verification (lab_02_backup_restore.py)")
hr3.font.name = "Arial"
hr3.font.size = Pt(13)
hr3.font.bold = True
hr3.font.color.rgb = COLOR_PRIMARY

p_act2 = doc.add_paragraph()
p_act2.add_run(
    "A backup that has never been restored is not a backup—it is merely a hope. "
    "Activity 2 implements an end-to-end automated disaster recovery test loop with dual-check verification:\n"
).font.size = Pt(10)

# Verification Steps
steps_data = [
    ("Step 1: Deterministic Seeding & Baseline Checksum",
     "500 order documents (ORD-0000 to ORD-0499) are inserted into nosql_labs.backup_demo. "
     "A deterministic SHA-256 checksum is computed over sorted document values (7eacb1b11dce0ed9...)."),
    ("Step 2: mongodump Snapshot Generation",
     "mongodump connects to the replica set and streams a complete binary dump into backups/YYYYMMDD-HHMMSS/ "
     "with metadata and BSON documents intact. RTO benchmark start timestamp recorded."),
    ("Step 3: Simulated Complete Data Loss",
     "The collection is intentionally dropped via col.drop(), verifying document count drops to 0."),
    ("Step 4: mongorestore Reconstitution",
     "mongorestore reconstitutes the namespace nosql_labs.backup_demo from the timestamped BSON archive. "
     "Execution completes in ~0.06 seconds."),
    ("Step 5: Dual Verification (Count + SHA-256 Checksum)",
     "The restored collection is verified across two independent axes: total document count (500 == 500) "
     "AND content hash match (7eacb1b11dce0ed9... == 7eacb1b11dce0ed9...). Both checks PASS [OK].")
]

for title, desc in steps_data:
    p = doc.add_paragraph()
    r_t = p.add_run(f"• {title}: ")
    r_t.font.name = "Arial"
    r_t.font.bold = True
    r_t.font.size = Pt(9.5)
    r_d = p.add_run(desc)
    r_d.font.name = "Arial"
    r_d.font.size = Pt(9.5)

doc.add_paragraph()

# Callout: Why Count Alone is Insufficient
why_table = doc.add_table(rows=1, cols=1)
why_table.alignment = WD_TABLE_ALIGNMENT.CENTER
why_table.columns[0].width = Inches(6.8)
w_cell = why_table.cell(0, 0)
set_cell_background(w_cell, "FFFBEB")
set_cell_margins(w_cell, 120, 120, 160, 160)

wp = w_cell.paragraphs[0]
wr1 = wp.add_run("CRITICAL INSIGHT: WHY DUAL VERIFICATION (COUNT + CHECKSUM) IS ESSENTIAL\n")
wr1.font.name = "Arial"
wr1.font.bold = True
wr1.font.size = Pt(10)
wr1.font.color.rgb = COLOR_ORANGE

wr2 = wp.add_run(
    "A document count check is necessary but strictly WEAK on its own. For example, if mongorestore "
    "silently dropped one customer order but accidentally duplicated another, count_documents() would still return 500, "
    "falsely reporting success while permanent data loss occurred. "
    "Furthermore, mongorestore may regenerate ObjectIds or insert documents in non-sequential order. "
    "The script's custom checksum function queries documents excluding _id and sorts deterministically by order_id, "
    "computing a SHA-256 digest over the raw JSON payload. This catches silent bit rot, truncated fields, dropped records, "
    "and duplicate corruptions that count checks completely overlook."
)
wr2.font.name = "Arial"
wr2.font.size = Pt(9)
wr2.font.color.rgb = COLOR_DARK

doc.add_paragraph()

# RPO vs RTO Explanatory Block
h_rpo = doc.add_heading(level=2)
hr_rpo = h_rpo.add_run("Business Continuity: Recovery Point Objective (RPO) & Recovery Time Objective (RTO)")
hr_rpo.font.name = "Arial"
hr_rpo.font.size = Pt(11)
hr_rpo.font.bold = True
hr_rpo.font.color.rgb = COLOR_DARK

p_rpo = doc.add_paragraph()
p_rpo.add_run(
    "Backup verification bridges technical operations with enterprise SLAs:\n"
    "• Recovery Point Objective (RPO): The maximum acceptable volume of data loss measured in time. "
    "Determined by backup frequency and oplog retention. For hourly backups, RPO is 60 minutes.\n"
    "• Recovery Time Objective (RTO): The maximum allowable downtime to restore service. "
    "In this laboratory benchmark, mongodump took 0.03 seconds and mongorestore completed in 0.06 seconds, "
    "providing empirical RTO data to calibrate disaster recovery plans."
).font.size = Pt(9.5)

doc.add_paragraph()

# ── Section 4: Web Application Integration ────────────────────────────────
h4 = doc.add_heading(level=1)
hr4 = h4.add_run("4. Web Application Integration (Flask + SSE + Bootstrap 5)")
hr4.font.name = "Arial"
hr4.font.size = Pt(13)
hr4.font.bold = True
hr4.font.color.rgb = COLOR_PRIMARY

p_web = doc.add_paragraph()
p_web.add_run(
    "To provide an enterprise-grade demonstration experience, both laboratory tasks have been integrated "
    "into a responsive web application running on port 5004:\n"
    "• Overview Dashboard (/): Real-time host info, MongoDB version, tool availability, and navigation.\n"
    "• Activity 1 Dashboard (/lab1): Live SSE metrics stream updating every 3 seconds, dynamic connection gauges, "
    "WiredTiger cache utilization bars, and threshold alert badges.\n"
    "• Activity 2 Drill Dashboard (/lab2): Interactive web trigger to execute the 5-stage automated backup "
    "and restore pipeline with real-time log output, RTO timers, document count diffs, and SHA-256 checksum status."
).font.size = Pt(9.5)

doc.add_paragraph()

# ── Section 5: Actual Execution Evidence ──────────────────────────────────
h5 = doc.add_heading(level=1)
hr5 = h5.add_run("5. Actual Execution Evidence & Verification Logs")
hr5.font.name = "Arial"
hr5.font.size = Pt(13)
hr5.font.bold = True
hr5.font.color.rgb = COLOR_PRIMARY

# Code block for lab_02 output
ev_table = doc.add_table(rows=1, cols=1)
ev_table.alignment = WD_TABLE_ALIGNMENT.CENTER
ev_table.columns[0].width = Inches(6.8)
ev_cell = ev_table.cell(0, 0)
set_cell_background(ev_cell, "0F172A")
set_cell_margins(ev_cell, 100, 100, 120, 120)

ev_p = ev_cell.paragraphs[0]
ev_r = ev_p.add_run(
    "=== [LAB 14.2: Automated Backup and Restore Verification Output] ===\n\n"
    "=== Step 1: Seed collection and record baseline checksum ===\n"
    "  [OK] Seeded 500 documents.\n"
    "  Baseline checksum: 7eacb1b11dce0ed9...\n\n"
    "=== Step 2: Backup to /app/backups/20261118-093618 ===\n"
    "  $ mongodump --uri=mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/?replicaSet=rs0&authSource=admin --db=nosql_labs --collection=backup_demo --out=/app/backups/20261118-093618\n"
    "  [OK] Backup complete in 0.03s.\n\n"
    "=== Step 3: Simulate data loss (drop the collection) ===\n"
    "  [OK] Collection dropped. Document count is now: 0\n\n"
    "=== Step 4: Restore with mongorestore ===\n"
    "  $ mongorestore --uri=mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/?replicaSet=rs0&authSource=admin --nsInclude=nosql_labs.backup_demo /app/backups/20261118-093618\n"
    "  [OK] Restore complete in 0.06s.\n\n"
    "=== Step 5: Verify restore integrity ===\n"
    "  Document count:   original=500  restored=500  [OK]\n"
    "  Content checksum: MATCH (7eacb1b11dce0ed9...)\n\n"
    "  [OK] Restore verified: document count AND content checksum match.\n"
    "  This backup is trustworthy for a real disaster-recovery drill.\n"
    "==========================================================="
)
ev_r.font.name = "Consolas"
ev_r.font.size = Pt(8)
ev_r.font.color.rgb = RGBColor(163, 230, 53)

# Save DOCX
docx_path = os.path.join(base_dir, "Lab_14_Report.docx")
doc.save(docx_path)
print(f"[OK] Generated Word report: {docx_path}")

# Convert to PDF
pdf_path = os.path.join(base_dir, "Lab_14_Report.pdf")
sub_pdf_path = os.path.join(base_dir, "NoSQL_Lab14_Submission.pdf")
desktop_sub_pdf = os.path.join(desktop_dir, "NoSQL_Lab14_Submission.pdf")

try:
    from docx2pdf import convert
    convert(docx_path, pdf_path)
    shutil.copyfile(pdf_path, sub_pdf_path)
    shutil.copyfile(pdf_path, desktop_sub_pdf)
    print(f"[OK] Converted to PDF: {pdf_path}")
    print(f"[OK] Created Submission PDF: {sub_pdf_path}")
    print(f"[OK] Copied Submission PDF to Desktop: {desktop_sub_pdf}")
except Exception as ex:
    print(f"[ERROR] PDF conversion failed: {ex}")
