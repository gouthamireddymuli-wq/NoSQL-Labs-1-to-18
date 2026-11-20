"""Direct ReportLab PDF Generator for NoSQL Lab 17 Submission Report.
Produces Lab_17_Report.pdf, NoSQL_Lab17_Submission.pdf, and Desktop copy.
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

pdf_path = os.path.join(base_dir, "Lab_17_Report.pdf")
sub_pdf_path = os.path.join(base_dir, "NoSQL_Lab17_Submission.pdf")
desktop_sub_pdf = os.path.join(desktop_dir, "NoSQL_Lab17_Submission.pdf")

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
    [Paragraph("NoSQL Database Systems &mdash; Laboratory 17 Report<br/>Build a Simple RAG Pipeline &amp; Compare HNSW vs. IVF Vector Indexes", header_title_style)],
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
<b>Docker Hub Repository:</b> <font color="#0969DA"><b>https://hub.docker.com/r/gouthudocker/nosql-lab17</b></font><br/>
<b>Docker Pull Command:</b> <font face="Courier">docker pull gouthudocker/nosql-lab17:latest</font><br/>
<b>Interactive Web UI Port:</b> <font color="#00684A"><b>http://localhost:5000</b></font><br/>
<b>Grading Verification:</b> Pre-built Docker image includes completed Activity 1 (RAG Pipeline), Activity 2 (HNSW vs IVF Benchmark), full Flask Web GUI, REST APIs, and automated test suite.
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

# 1. Executive Summary & Lab Objectives
elements.append(Paragraph("1. Executive Summary &amp; Lab Objectives", h1_style))
elements.append(Paragraph(
    "Retrieval-Augmented Generation (RAG) and Approximate Nearest Neighbor (ANN) vector indexing represent "
    "the core technological backbone of modern AI-driven database systems. This laboratory investigates both "
    "dimensions across two comprehensive technical activities:",
    body_style
))
elements.append(Paragraph(
    "&bull; <b>Activity 1 (lab_01_rag_pipeline.py):</b> Constructs an end-to-end RAG pipeline using MongoDB. Documents "
    "are divided into bounded 50-word passages, embedded into 384-dimensional unit-normalized vectors, indexed in MongoDB, "
    "and queried using brute-force cosine similarity (dot product) to construct LLM contextual prompts with conversational memory.",
    bullet_style
))
elements.append(Paragraph(
    "&bull; <b>Activity 2 (lab_02_hnsw_vs_ivf.py):</b> Explores high-dimensional vector search algorithms by benchmarking "
    "exact brute-force search against Inverted File (IVF) clustering and single-layer Navigable Small World (NSW / HNSW-like) "
    "graphs on a synthetic 3,000-vector dataset, analyzing Recall@10 and proving why 'Vectors Compared per Query' is the fundamental scalability metric.",
    bullet_style
))
elements.append(Spacer(1, 6))

# 2. Activity 1 Details
elements.append(Paragraph("2. Activity 1: Build a Simple RAG Pipeline (lab_01_rag_pipeline.py)", h1_style))
elements.append(Paragraph("2.1 Document Chunking &amp; Unit-Normalized Mock Embeddings", h2_style))
elements.append(Paragraph(
    "Raw technical documents regarding NoSQL architectures, MongoDB Aggregations, Vector Search, and Replica Sets "
    "are split into 50-word bounded passages. The <font face='Courier'>mock_embed()</font> function generates deterministic "
    "384-dimensional Gaussian vectors seeded by MD5 string hashes. Because each vector is pre-normalized to unit length "
    "(<font face='Courier'>||v|| = 1</font>), cosine similarity simplifies directly to the algebraic dot product:",
    body_style
))
elements.append(Paragraph(
    "<font face='Courier'>sim(u, v) = u &bull; v = &sum; u_i &bull; v_i &nbsp;&nbsp;(where ||u|| = ||v|| = 1)</font>",
    code_style
))

elements.append(Paragraph("2.2 MongoDB Retrieval &amp; Projection Query", h2_style))
elements.append(Paragraph(
    "Chunks and embeddings are stored in <font face='Courier'>nosql_labs.rag_documents</font>. During retrieval, "
    "a query embedding is computed and compared against all stored documents via MongoDB collection scan with projection "
    "<font face='Courier'>col.find({}, {'embedding': 1, 'text': 1, 'source_title': 1, '_id': 0})</font>. "
    "The scored chunks are sorted descending to return top-k matches.",
    body_style
))

elements.append(Paragraph("2.3 Contextual Prompt Synthesis &amp; Multi-Turn Memory", h2_style))
elements.append(Paragraph(
    "Retrieved chunks are assembled into a structured tutor prompt alongside prior conversation turns. "
    "The <font face='Courier'>SimpleRAG</font> class records conversation history in memory, ensuring that consecutive "
    "turns maintain dialogue context across 4 user queries.",
    body_style
))

elements.append(Paragraph("2.4 Prediction vs. Actual Retrieval Evaluation", h2_style))
elements.append(Paragraph(
    "A human reader predicts that a query regarding 'four NoSQL database families' will retrieve the 'Introduction to NoSQL' chunk. "
    "However, because mock embeddings hash strings without semantic comprehension, hash collisions place vectors at arbitrary angles. "
    "In production, real embedding models (VoyageAI / OpenAI) ensure that semantic similarity governs geometric proximity.",
    body_style
))
elements.append(Spacer(1, 6))

# 3. Activity 2 Details
elements.append(Paragraph("3. Activity 2: Compare HNSW and IVF Vector Index Types (lab_02_hnsw_vs_ivf.py)", h1_style))
elements.append(Paragraph("3.1 Exact Brute-Force vs. Approximate Nearest Neighbor Search", h2_style))
elements.append(Paragraph(
    "Exact brute-force search computes distances across all N=3,000 vectors, ensuring 100% recall but scaling at O(N &bull; D). "
    "Approximate Nearest Neighbor (ANN) search trades a small accuracy margin to evaluate only a fraction of stored vectors.",
    body_style
))

elements.append(Paragraph("3.2 Inverted File Index (IVF) Clustering", h2_style))
elements.append(Paragraph(
    "The <font face='Courier'>IVFIndex</font> partitions the dataset into nlist=20 Voronoi clusters using Lloyd's K-Means. "
    "At search time, only nprobe=3 closest centroids are inspected, pruning 85% of clusters and reducing vectors compared per query to ~447.",
    body_style
))

elements.append(Paragraph("3.3 Simplified Navigable Small World (NSW / HNSW-like) Graph", h2_style))
elements.append(Paragraph(
    "The <font face='Courier'>SimpleNSWIndex</font> connects each vector to m=16 nearest neighbors. "
    "Greedy graph search navigates from 5 entry points along edges maximizing cosine similarity, maintaining an ef_search=100 priority queue.",
    body_style
))

elements.append(Paragraph("3.4 Empirical Benchmark Results (N=3,000, Dim=64, K=10, 20 Queries)", h2_style))

# Results Table
results_data = [
    [Paragraph("<b>Index Type / Family</b>", table_header_style),
     Paragraph("<b>Build Time (ms)</b>", table_header_style),
     Paragraph("<b>Vectors Compared / Query</b>", table_header_style),
     Paragraph("<b>Avg Query Time (ms)</b>", table_header_style),
     Paragraph("<b>Recall@10</b>", table_header_style)],
    [Paragraph("Brute-force (exact)", table_cell_style),
     Paragraph("0.0 ms", table_cell_code),
     Paragraph("3,000 (100.0%)", table_cell_code),
     Paragraph("0.160 ms", table_cell_code),
     Paragraph("<b>100.00%</b>", table_cell_code)],
    [Paragraph("IVF (nlist=20, nprobe=3)", table_cell_style),
     Paragraph("15.1 ms", table_cell_code),
     Paragraph("447 (14.9%)", table_cell_code),
     Paragraph("0.114 ms", table_cell_code),
     Paragraph("<b>42.00%</b>", table_cell_code)],
    [Paragraph("Simplified NSW (HNSW-like)", table_cell_style),
     Paragraph("382.1 ms", table_cell_code),
     Paragraph("1,810 (60.3%)", table_cell_code),
     Paragraph("5.119 ms", table_cell_code),
     Paragraph("<font color='#00684A'><b>91.50%</b></font>", table_cell_code)]
]
res_table = Table(results_data, colWidths=[160, 80, 130, 80, 70])
res_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#001E2B')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
    ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
    ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F8FAFC')),
    ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#EBFBF3')),
]))
elements.append(res_table)
elements.append(Spacer(1, 6))

elements.append(Paragraph("3.5 Key Scalability Takeaway: Vectors Compared vs. Wall-Clock Time", h2_style))
elements.append(Paragraph(
    "<b>Vectors Compared per Query</b> is the true architectural metric of scalability. In pure Python, NSW graph navigation "
    "suffers from interpreter dictionary and heap overhead. In production C++ engines (such as MongoDB Atlas <font face='Courier'>$vectorSearch</font>), "
    "reducing distance evaluations by 40%–85% produces dramatic orders-of-magnitude wall-clock speedups.",
    body_style
))
elements.append(Spacer(1, 6))

# 4. Web Application Integration
elements.append(Paragraph("4. Web Application &amp; Interactive UI Integration", h1_style))
elements.append(Paragraph(
    "The lab tasks are integrated into an interactive Flask web application featuring live KPI cards, interactive "
    "RAG chunking and retrieval explorers, real-time prompt inspectors, multi-turn chat simulators, parameter sliders "
    "(N, Dim, nlist, nprobe, m, ef_search), and Chart.js dynamic benchmarks.",
    body_style
))
elements.append(Spacer(1, 6))

# 5. Docker Demonstration Guide
elements.append(Paragraph("5. Docker Containerization &amp; Demonstration Guide", h1_style))
demo_data = [
    [Paragraph("<b>Step</b>", table_header_style), Paragraph("<b>Demonstration Command</b>", table_header_style), Paragraph("<b>Outcome / Verification</b>", table_header_style)],
    [Paragraph("1. Pull Image", table_cell_style), Paragraph("docker pull gouthudocker/nosql-lab17:latest", table_cell_code), Paragraph("Pulls verified container from Docker Hub", table_cell_style)],
    [Paragraph("2. Run Web UI", table_cell_style), Paragraph("docker run -d --name nosql_lab17 -p 5000:5000 gouthudocker/nosql-lab17:latest", table_cell_code), Paragraph("Serves interactive UI at http://localhost:5000", table_cell_style)],
    [Paragraph("3. Execute CLI", table_cell_style), Paragraph("docker exec -it nosql_lab17 py run_all.py", table_cell_code), Paragraph("Runs Activity 1 &amp; Activity 2 sequentially", table_cell_style)],
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
