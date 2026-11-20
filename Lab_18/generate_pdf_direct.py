"""Direct ReportLab PDF Generator for NoSQL Lab 18 Submission Report.
Produces Lab_18_Report.pdf, NoSQL_Lab18_Submission.pdf, and Desktop copy.
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

pdf_path = os.path.join(base_dir, "Lab_18_Report.pdf")
sub_pdf_path = os.path.join(base_dir, "NoSQL_Lab18_Submission.pdf")
desktop_sub_pdf = os.path.join(desktop_dir, "NoSQL_Lab18_Submission.pdf")


def build_pdf():
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
        fontSize=13.5,
        textColor=colors.white,
        alignment=1,
        spaceAfter=4
    )

    header_sub_style = ParagraphStyle(
        'HeaderSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
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
        fontSize=11,
        textColor=colors.HexColor('#00684A'),
        spaceBefore=8,
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
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1F2328')
    )

    table_cell_code = ParagraphStyle(
        'TableCellCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )

    elements = []

    # Header Table
    header_data = [
        [Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", header_sub_style)],
        [Paragraph("NoSQL Database Systems &mdash; Laboratory 18 Capstone Report<br/>Comparative Capstone Lab &amp; Technical Analysis Report: Fraud Detection Data Platform", header_title_style)],
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

    # Docker Hub Submission Callout Box
    callout_content = """
<b><font color="#00684A" size="9.5">★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION &amp; GRADING ★</font></b><br/>
<b>Docker Hub Repository:</b> <font color="#0969DA"><b>https://hub.docker.com/r/gouthudocker/nosql-lab18</b></font><br/>
<b>Docker Pull Command:</b> <font face="Courier">docker pull gouthudocker/nosql-lab18:latest</font><br/>
<b>Interactive Web UI Port:</b> <font color="#00684A"><b>http://localhost:5000</b></font><br/>
<b>Grading Verification:</b> The Docker image includes completed Activity 1 (Comparative Capstone Benchmark), Activity 2 (Markdown Comparative Analysis Report), live Flask Web Dashboard, REST APIs, and automated test runners.
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

    # 1. Executive Summary & Benchmark Methodology
    elements.append(Paragraph("1. Executive Summary &amp; Benchmark Methodology", h1_style))
    elements.append(Paragraph(
        "Modern fraud-detection platforms confront four divergent database access patterns simultaneously: "
        "ultra-fast point lookups (customer velocity checking), multi-attribute range filtering (risk-score triage), "
        "analytical aggregations (category spend anomalies), and deep relationship traversals (fraud rings sharing devices). "
        "No single database architecture optimizes all four patterns. This capstone performs an end-to-end empirical benchmark "
        "evaluating <b>MongoDB</b> (document store) against architectural capabilities of <b>Apache Cassandra</b> (wide-column store) "
        "and <b>Neo4j</b> (graph database).",
        body_style
    ))
    elements.append(Paragraph(
        "&bull; <b>Activity 1 (lab_01_comparative_capstone.py):</b> Ingests 10,000 synthetic financial transactions (~2% fraud rate), "
        "establishes compound and single-field B-Tree indexes, and runs four timed benchmark queries against a live MongoDB database.",
        bullet_style
    ))
    elements.append(Paragraph(
        "&bull; <b>Activity 2 (lab_02_comparative_report.py):</b> Synthesizes live measured MongoDB numbers with grounded architectural estimates "
        "for Cassandra and Neo4j, generating a production-grade comparative analysis report with a clear polyglot persistence recommendation.",
        bullet_style
    ))
    elements.append(Spacer(1, 6))

    # 2. Activity 1 Details
    elements.append(Paragraph("2. Activity 1: Comparative Capstone Benchmark (lab_01_comparative_capstone.py)", h1_style))
    elements.append(Paragraph("2.1 Synthetic Dataset &amp; Indexing Strategy", h2_style))
    elements.append(Paragraph(
        "A synthetic dataset of 10,000 transactions was generated with realistic fields (<font face='Courier'>user_id</font>, "
        "<font face='Courier'>merchant_id</font>, <font face='Courier'>category</font>, <font face='Courier'>amount</font>, "
        "<font face='Courier'>timestamp</font>, <font face='Courier'>is_fraud</font>, <font face='Courier'>risk_score</font>, "
        "<font face='Courier'>device_id</font>). To guarantee a fair benchmark, the following indexes were created:",
        body_style
    ))
    elements.append(Paragraph(
        "&bull; <font face='Courier'>idx_user_time: [('user_id', 1), ('timestamp', -1)]</font> &mdash; Compound index covering point lookups and chronological sorting.<br/>"
        "&bull; <font face='Courier'>idx_risk: [('risk_score', -1)]</font> &mdash; B-Tree index for selective high-risk range filtering.<br/>"
        "&bull; <font face='Courier'>idx_category: [('category', 1)]</font> &mdash; Index optimizing category grouping pipeline stages.",
        bullet_style
    ))

    elements.append(Paragraph("2.2 Empirical Benchmark Results (10,000 Transactions Dataset)", h2_style))

    # Results Table
    results_data = [
        [Paragraph("<b>Query Type</b>", table_header_style),
         Paragraph("<b>MongoDB (Measured)</b>", table_header_style),
         Paragraph("<b>Cassandra (Estimated)</b>", table_header_style),
         Paragraph("<b>Neo4j (Estimated)</b>", table_header_style),
         Paragraph("<b>Architectural Comparison</b>", table_header_style)],
        [Paragraph("<b>Q1: User History</b><br/>user_id lookup + sort", table_cell_style),
         Paragraph("<b>14.3 ms</b> (11 docs)", table_cell_code),
         Paragraph("~2 &ndash; 5 ms", table_cell_code),
         Paragraph("~5 &ndash; 15 ms", table_cell_code),
         Paragraph("Cassandra fastest with partition key. MongoDB close with compound B-Tree index.", table_cell_style)],
        [Paragraph("<b>Q2: High-Risk</b><br/>risk_score &gt; 0.8", table_cell_style),
         Paragraph("<b>19.4 ms</b> (130 docs)", table_cell_code),
         Paragraph("~50 &ndash; 200+ ms", table_cell_code),
         Paragraph("~10 &ndash; 50 ms", table_cell_code),
         Paragraph("MongoDB excels via bounded index scan. Cassandra requires ALLOW FILTERING.", table_cell_style)],
        [Paragraph("<b>Q3: Analytics</b><br/>$group by category", table_cell_style),
         Paragraph("<b>10.4 ms</b> (6 categories)", table_cell_code),
         Paragraph("N/A (needs Spark)", table_cell_code),
         Paragraph("Weak Fit (&gt;100 ms)", table_cell_code),
         Paragraph("MongoDB native aggregation pipeline groups in memory. Cassandra lacks aggregation.", table_cell_style)],
        [Paragraph("<b>Q4: Write Throughput</b><br/>1,000 bulk inserts", table_cell_style),
         Paragraph("<b>51.9 ms</b> (19,270 ops/s)", table_cell_code),
         Paragraph("Excellent (linear)", table_cell_code),
         Paragraph("Moderate (~95 ms)", table_cell_code),
         Paragraph("Cassandra scales writes linearly. MongoDB insert_many achieves 19k+ ops/sec.", table_cell_style)]
    ]
    res_table = Table(results_data, colWidths=[110, 105, 95, 90, 120])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001E2B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (1,1), (3,-1), 'CENTER'),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#EBFBF3')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#FFFFFF')),
    ]))
    elements.append(res_table)
    elements.append(Spacer(1, 6))

    # 3. Activity 2 Details
    elements.append(Paragraph("3. Activity 2: Comparative Analysis Technical Report (lab_02_comparative_report.py)", h1_style))
    elements.append(Paragraph("3.1 Measured vs. Estimated Separation Principle", h2_style))
    elements.append(Paragraph(
        "A critical engineering discipline when delivering architecture documents is rigorously distinguishing between "
        "<b>empirically measured</b> metrics (run against live instances) and <b>architectural estimates</b> (derived from storage engine mechanics). "
        "The generated report strictly tags MongoDB latencies as MEASURED, while Cassandra and Neo4j estimates are clearly footnoted.",
        body_style
    ))

    elements.append(Paragraph("3.2 Scalability Assessment (1M vs. 10M vs. 100M Transactions)", h2_style))
    scale_data = [
        [Paragraph("<b>Scale Tier</b>", table_header_style), Paragraph("<b>MongoDB</b>", table_header_style), Paragraph("<b>Cassandra</b>", table_header_style), Paragraph("<b>Neo4j</b>", table_header_style)],
        [Paragraph("<b>1 Million</b>", table_cell_style),
         Paragraph("Comfortable on single replica set with standard B-Tree RAM caching.", table_cell_style),
         Paragraph("Comfortable on 3-node cluster.", table_cell_style),
         Paragraph("Comfortable on single instance.", table_cell_style)],
        [Paragraph("<b>10 Million</b>", table_cell_style),
         Paragraph("Sharding advised if write-heavy; read replicas absorb read volume.", table_cell_style),
         Paragraph("Near-linear scale out by adding nodes.", table_cell_style),
         Paragraph("Fine for lookups; fraud ring queries require strict hop limits.", table_cell_style)],
        [Paragraph("<b>100 Million</b>", table_cell_style),
         Paragraph("Sharded cluster required (Ch. 11); compound shard key essential.", table_cell_style),
         Paragraph("Cassandra's primary domain; linear write scale-out excels.", table_cell_style),
         Paragraph("Requires relationship pruning and Neo4j Fabric cluster sharding.", table_cell_style)],
    ]
    scale_table = Table(scale_data, colWidths=[70, 150, 150, 150])
    scale_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001E2B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFFFFF')),
    ]))
    elements.append(scale_table)
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("3.3 Final Polyglot Persistence Recommendation", h2_style))
    elements.append(Paragraph(
        "<b>Recommendation:</b> Deploy a <b>polyglot persistence architecture</b>: start with <b>MongoDB alone</b> as the primary operational store. "
        "MongoDB comfortably handles transaction ingestion, user history retrieval via compound indexes, risk score filtering, and analytical aggregations "
        "with low operational overhead. <b>Add Neo4j</b> as a specialized sidecar only when deep fraud-ring detection (e.g. 3-hop shared-device networks) "
        "becomes a mandatory requirement, routing graph queries via Neo4j's Cypher engine while keeping transactions in MongoDB. "
        "<b>Cassandra is excluded</b> because its lack of native ad-hoc range scans and aggregations cripples fraud investigation workflows.",
        body_style
    ))
    elements.append(Spacer(1, 6))

    # 4. Web Application Integration
    elements.append(Paragraph("4. Web Application &amp; Interactive UI Integration", h1_style))
    elements.append(Paragraph(
        "All lab capabilities are integrated into a modern Flask Web Application (featuring dark slate theme, Chart.js benchmarks, and Tailwind CSS):<br/>"
        "&bull; <b>Executive Dashboard:</b> Real-time KPI cards, interactive architecture SVG visualizer, and database decision scorecard.<br/>"
        "&bull; <b>Activity 1 Benchmark Studio:</b> One-click data generation, index verification, real-time query execution, and explain plan analyzer.<br/>"
        "&bull; <b>Activity 2 Report Viewer:</b> Dynamic Markdown generation, raw/rendered toggles, and direct Markdown/PDF export.<br/>"
        "&bull; <b>Fraud Ring Studio:</b> Identifies devices shared across multiple accounts and demonstrates the Cypher graph traversal equivalent.",
        body_style
    ))
    elements.append(Spacer(1, 6))

    # 5. Docker Demonstration Guide
    elements.append(Paragraph("5. Docker Containerization &amp; Demonstration Guide", h1_style))
    demo_data = [
        [Paragraph("<b>Step</b>", table_header_style), Paragraph("<b>Demonstration Command</b>", table_header_style), Paragraph("<b>Outcome / Verification</b>", table_header_style)],
        [Paragraph("1. Pull Image", table_cell_style), Paragraph("docker pull gouthudocker/nosql-lab18:latest", table_cell_code), Paragraph("Pulls verified container from Docker Hub", table_cell_style)],
        [Paragraph("2. Run Web UI", table_cell_style), Paragraph("docker run -d --name nosql_lab18 -p 5000:5000 gouthudocker/nosql-lab18:latest", table_cell_code), Paragraph("Serves interactive UI at http://localhost:5000", table_cell_style)],
        [Paragraph("3. Execute CLI", table_cell_style), Paragraph("docker exec -it nosql_lab18 py run_all.py", table_cell_code), Paragraph("Runs Activity 1 &amp; Activity 2 sequentially", table_cell_style)],
    ]
    demo_table = Table(demo_data, colWidths=[80, 270, 170])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001E2B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFFFFF')),
    ]))
    elements.append(demo_table)

    doc.build(elements)
    print(f"Generated PDF: {pdf_path}")

    # Copy to submission paths
    shutil.copy(pdf_path, sub_pdf_path)
    print(f"Copied to: {sub_pdf_path}")
    shutil.copy(pdf_path, desktop_sub_pdf)
    print(f"Copied to: {desktop_sub_pdf}")


if __name__ == "__main__":
    build_pdf()
