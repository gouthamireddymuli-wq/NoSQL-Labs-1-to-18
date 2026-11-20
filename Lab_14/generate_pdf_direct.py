"""Direct ReportLab PDF Generator for NoSQL Lab 14 Submission Report.
Produces Lab_14_Report.pdf and NoSQL_Lab14_Submission.pdf with high fidelity.
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

pdf_path = os.path.join(base_dir, "Lab_14_Report.pdf")
sub_pdf_path = os.path.join(base_dir, "NoSQL_Lab14_Submission.pdf")
desktop_sub_pdf = os.path.join(desktop_dir, "NoSQL_Lab14_Submission.pdf")

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
    fontSize=15,
    textColor=colors.white,
    alignment=1, # Center
    spaceAfter=4
)

header_sub_style = ParagraphStyle(
    'HeaderSub',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    textColor=colors.HexColor('#00ED64'),
    alignment=1,
    spaceAfter=2
)

header_meta_style = ParagraphStyle(
    'HeaderMeta',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    textColor=colors.HexColor('#D1D5DB'),
    alignment=1
)

h1_style = ParagraphStyle(
    'H1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=12,
    textColor=colors.HexColor('#00684A'),
    spaceBefore=10,
    spaceAfter=4
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#1F2328')
)

bullet_style = ParagraphStyle(
    'Bullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#1F2328')
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor('#A3E635')
)

elements = []

# Header Box
header_data = [
    [Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", header_sub_style)],
    [Paragraph("NoSQL Database Laboratory — Lab 14<br/>Production Monitoring, Automated Backup & Restore Verification", header_title_style)],
    [Paragraph("Student: <b>M Gouthami</b> | Roll No: <b>24BTRCL130</b> | Academic Year: 2026-2027", header_meta_style)]
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
elements.append(Spacer(1, 10))

# Docker Hub Callout Box
callout_content = """
<b><font color="#00684A" size="10">★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION & GRADING ★</font></b><br/>
<b>Docker Hub Repository:</b> <font color="#0969DA"><b>https://hub.docker.com/r/gouthudocker/nosql-lab14</b></font><br/>
<b>Docker Pull Command:</b> <font face="Courier">docker pull gouthudocker/nosql-lab14:latest</font><br/>
<b>Image Digest:</b> <font face="Courier" size="7.5" color="#57606A">sha256:ba055c753bd41f30b8dd2ce92feb1a006bc6c40223e7b04caf2e9d3c725c0c92</font><br/>
<b>Interactive Web UI Port:</b> <font color="#00684A"><b>http://localhost:5004</b></font> (or port 5000 inside container)
"""
callout_table = Table([[Paragraph(callout_content, body_style)]], colWidths=[520])
callout_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E6F7EF')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#00ED64')),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 12),
    ('RIGHTPADDING', (0,0), (-1,-1), 12),
]))
elements.append(callout_table)
elements.append(Spacer(1, 8))

# 1. Demonstration Instructions
elements.append(Paragraph("1. Demonstration & Grading Instructions", h1_style))
elements.append(Paragraph(
    "The uploaded Docker image encapsulates the complete laboratory solution including MongoDB Database Tools "
    "(<b>mongodump</b>, <b>mongorestore</b>), monitoring daemon, Rich terminal UI, and interactive Flask web dashboard.",
    body_style
))
elements.append(Spacer(1, 4))

demo_steps = [
    [Paragraph("<b>Step 1: Pull Image</b>", body_style),
     Paragraph("docker pull gouthudocker/nosql-lab14:latest", code_style)],
    [Paragraph("<b>Step 2: Run Web Container</b><br/><font size='7' color='#57606A'>Demonstration dashboard</font>", body_style),
     Paragraph("docker run -d --name nosql_lab14_web -p 5004:5000 \<br/>  --network nosqllab13_default \<br/>  -e MONGO_URI=\"mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin\" \<br/>  gouthudocker/nosql-lab14:latest<br/><font color='#A3E635'># Open browser at: http://localhost:5004</font>", code_style)],
    [Paragraph("<b>Step 3: Run Monitoring (Lab 1)</b>", body_style),
     Paragraph("docker exec -it nosql_lab14_web python lab_01_monitoring_dashboard.py", code_style)],
    [Paragraph("<b>Step 4: Run Backup Drill (Lab 2)</b>", body_style),
     Paragraph("docker exec -it nosql_lab14_web python lab_02_backup_restore.py", code_style)]
]
demo_table = Table(demo_steps, colWidths=[150, 370])
demo_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8FAFC')),
    ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#0F172A')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
]))
elements.append(demo_table)
elements.append(Spacer(1, 8))

# 2. Activity 1
elements.append(Paragraph("2. Activity 1: Production Monitoring Dashboard (lab_01_monitoring_dashboard.py)", h1_style))
elements.append(Paragraph(
    "Pulls live internal metrics from the <b>serverStatus</b> administrative command. "
    "Applies contextual threshold alerting and writes dual output (live terminal display + persistent logs in <i>logs/metrics.log</i>).",
    body_style
))
elements.append(Spacer(1, 4))

act1_data = [
    [Paragraph("<b>Metric Category</b>", body_style), Paragraph("<b>Key Fields Inspected</b>", body_style), Paragraph("<b>Threshold Alert Rationale</b>", body_style)],
    [Paragraph("<b>Connection Pool</b>", bullet_style), Paragraph("connections.current, available, totalCreated", bullet_style), Paragraph("Alert when current &gt; 80% of max available. Prevents connection exhaustion outages.", bullet_style)],
    [Paragraph("<b>WiredTiger Cache</b>", bullet_style), Paragraph("bytes in cache, maximum configured, dirty bytes", bullet_style), Paragraph("Alert when cache &gt; 80%. High cache fill triggers eviction worker latency spikes.", bullet_style)],
    [Paragraph("<b>Op Counters</b>", bullet_style), Paragraph("opcounters.insert, query, update, delete, command", bullet_style), Paragraph("Cumulative throughput counters used to track real-time QPS shifts.", bullet_style)],
    [Paragraph("<b>Replication Lag</b>", bullet_style), Paragraph("replSetGetStatus members[].optimeDate", bullet_style), Paragraph("Alert when lag &gt; 10,000ms to guarantee replica read consistency.", bullet_style)]
]
act1_table = Table(act1_data, colWidths=[100, 180, 240])
act1_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001E2B')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
]))
for r in range(len(act1_data)):
    if r > 0 and r % 2 == 0:
        act1_table.setStyle(TableStyle([('BACKGROUND', (0, r), (-1, r), colors.HexColor('#F8FAFC'))]))
elements.append(act1_table)
elements.append(Spacer(1, 8))

# 3. Activity 2
elements.append(Paragraph("3. Activity 2: Automated Backup & Restore Verification (lab_02_backup_restore.py)", h1_style))
elements.append(Paragraph(
    "<b>A backup you have never restored is a hope, not a guarantee.</b> "
    "Executes an automated disaster recovery loop: seeds known data &rarr; mongodump &rarr; drops collection &rarr; mongorestore &rarr; dual verification.",
    body_style
))
elements.append(Spacer(1, 3))

p_why = """
<b>Why Count Alone Fails:</b> If mongorestore silently dropped one document but duplicated another, 
a count check (500 == 500) would falsely PASS despite permanent data loss. 
Our script computes an order-independent <b>SHA-256 content checksum</b> across all fields (excluding generated <i>_id</i>), 
catching silent corruption that count checks completely overlook.<br/>
<b>RPO &amp; RTO:</b> Recovery Point Objective defines allowable data loss; Recovery Time Objective defines allowable downtime. 
Empirical timings measured: Dump = <b>0.03s</b>, Restore = <b>0.06s</b>.
"""
why_table = Table([[Paragraph(p_why, bullet_style)]], colWidths=[520])
why_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#F59E0B')),
    ('TOPPADDING', (0,0), (-1,-1), 5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
elements.append(why_table)
elements.append(Spacer(1, 8))

# 4. Actual Verification Evidence
elements.append(Paragraph("4. Actual Execution Evidence & Verification Logs", h1_style))
ev_log = """=== [LAB 14.2: Automated Backup and Restore Verification Output] ===
=== Step 1: Seed collection and record baseline checksum ===
  [OK] Seeded 500 documents.
  Baseline checksum: 7eacb1b11dce0ed9...

=== Step 2: Backup to /app/backups/20261118-093618 ===
  $ mongodump --uri=mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/?replicaSet=rs0&authSource=admin --db=nosql_labs --collection=backup_demo --out=/app/backups/20261118-093618
  [OK] Backup complete in 0.03s.

=== Step 3: Simulate data loss (drop the collection) ===
  [OK] Collection dropped. Document count is now: 0

=== Step 4: Restore with mongorestore ===
  $ mongorestore --uri=mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/?replicaSet=rs0&authSource=admin --nsInclude=nosql_labs.backup_demo /app/backups/20261118-093618
  [OK] Restore complete in 0.06s.

=== Step 5: Verify restore integrity ===
  Document count:   original=500  restored=500  [OK]
  Content checksum: MATCH (7eacb1b11dce0ed9...)

  [OK] Restore verified: document count AND content checksum match.
  This backup is trustworthy for a real disaster-recovery drill.
==========================================================="""

ev_table = Table([[Paragraph(ev_log.replace('\n', '<br/>'), code_style)]], colWidths=[520])
ev_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
]))
elements.append(ev_table)

doc.build(elements)
print(f"[OK] Generated ReportLab PDF: {pdf_path}")

shutil.copyfile(pdf_path, sub_pdf_path)
shutil.copyfile(pdf_path, desktop_sub_pdf)
print(f"[OK] Created Submission PDF: {sub_pdf_path}")
print(f"[OK] Copied Submission PDF to Desktop: {desktop_sub_pdf}")
