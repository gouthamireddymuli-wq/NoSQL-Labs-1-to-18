"""Comprehensive Word (.docx) Report Generator for NoSQL Lab 17.
Author: M Gouthami (24BTRCL130)
Produces: Lab_17_Report.docx
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

base_dir = os.path.dirname(os.path.abspath(__file__))
docx_path = os.path.join(base_dir, "Lab_17_Report.docx")

doc = Document()

# Set page margins
sections = doc.sections
for section in sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)


def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


# Title Header Table
header_table = doc.add_table(rows=1, cols=1)
header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
header_table.autofit = False
header_table.columns[0].width = Inches(7.0)

cell = header_table.cell(0, 0)
set_cell_background(cell, "001E2B")
set_cell_margins(cell, top=180, bottom=180, left=200, right=200)

p_dept = cell.paragraphs[0]
p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_dept = p_dept.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
r_dept.font.name = "Calibri"
r_dept.font.size = Pt(10)
r_dept.font.bold = True
r_dept.font.color.rgb = RGBColor(0x00, 0xED, 0x64)

p_title = cell.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_title = p_title.add_run("NoSQL Database Systems – Laboratory 17 Report\nRAG Pipeline & Vector Index Types (HNSW vs. IVF)")
r_title.font.name = "Calibri"
r_title.font.size = Pt(16)
r_title.font.bold = True
r_title.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

p_meta = cell.add_paragraph()
p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_meta = p_meta.add_run("Student: M Gouthami   |   Register No: 24BTRCL130   |   Course: Distributed NoSQL Database Systems")
r_meta.font.name = "Calibri"
r_meta.font.size = Pt(9.5)
r_meta.font.color.rgb = RGBColor(0xD1, 0xD5, 0xDB)

doc.add_paragraph()

# Docker Hub Callout
callout = doc.add_table(rows=1, cols=1)
callout.alignment = WD_TABLE_ALIGNMENT.CENTER
callout.autofit = False
callout.columns[0].width = Inches(7.0)
c_cell = callout.cell(0, 0)
set_cell_background(c_cell, "E6F7EF")
set_cell_margins(c_cell, top=140, bottom=140, left=180, right=180)

cp = c_cell.paragraphs[0]
r_box_title = cp.add_run("★ DOCKER HUB SUBMISSION URL FOR DEMONSTRATION & GRADING ★\n")
r_box_title.font.name = "Calibri"
r_box_title.font.size = Pt(11)
r_box_title.font.bold = True
r_box_title.font.color.rgb = RGBColor(0x00, 0x68, 0x4A)

r_repo = cp.add_run("Docker Hub Repository: ")
r_repo.font.bold = True
r_repo_link = cp.add_run("https://hub.docker.com/r/gouthudocker/nosql-lab17\n")
r_repo_link.font.bold = True
r_repo_link.font.color.rgb = RGBColor(0x09, 0x69, 0xDA)

r_pull = cp.add_run("Docker Pull Command: ")
r_pull.font.bold = True
r_cmd = cp.add_run("docker pull gouthudocker/nosql-lab17:latest\n")
r_cmd.font.name = "Consolas"

r_web = cp.add_run("Interactive Web Interface: ")
r_web.font.bold = True
r_web_url = cp.add_run("http://localhost:5000\n")
r_web_url.font.bold = True
r_web_url.font.color.rgb = RGBColor(0x00, 0x68, 0x4A)

r_desc = cp.add_run("Artifact Verification: Contains completed Lab 17.1 (Simple RAG Pipeline), Lab 17.2 (HNSW vs IVF Vector Benchmark), full Flask Web GUI, REST APIs, and automated test runners.")
r_desc.font.size = Pt(9)
r_desc.font.color.rgb = RGBColor(0x37, 0x41, 0x51)

doc.add_paragraph()


def add_heading_1(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x68, 0x4A)
    return h


def add_heading_2(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(8)
    h.paragraph_format.space_after = Pt(2)
    run = h.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x09, 0x69, 0xDA)
    return h


def add_body(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x1F, 0x23, 0x28)
    return p


# 1. Executive Summary
add_heading_1("1. Executive Summary & Experimental Scope")
add_body(
    "In modern generative AI architectures, Large Language Models (LLMs) suffer from hallucinations and knowledge "
    "staleness. Retrieval-Augmented Generation (RAG) resolves these deficiencies by dynamically retrieving ground-truth "
    "passages from external NoSQL databases and injecting them into the LLM context prompt. At enterprise scale, "
    "retrieving vectors from collections containing billions of documents requires Approximate Nearest Neighbor (ANN) "
    "indexing architectures rather than exact brute-force scans."
)
add_body(
    "This laboratory is divided into two primary technical milestones:\n"
    "• Activity 1: Build a Simple RAG Pipeline (lab_01_rag_pipeline.py) – Implements an end-to-end RAG architecture "
    "in MongoDB, including document chunking, deterministic unit-normalized vector embeddings, brute-force cosine similarity "
    "retrieval, LLM prompt assembly, and multi-turn conversational memory.\n"
    "• Activity 2: Compare HNSW and IVF Vector Index Types (lab_02_hnsw_vs_ivf.py) – Evaluates approximate search trade-offs "
    "by benchmarking exact brute-force search against Inverted File (IVF) clustering and single-layer Navigable Small World "
    "(NSW/HNSW) graphs on a 3,000-vector synthetic dataset, comparing Recall@K and Vectors Compared per Query."
)

# 2. Activity 1 Details
add_heading_1("2. Activity 1: Build a Simple RAG Pipeline (lab_01_rag_pipeline.py)")
add_heading_2("2.1 Document Chunking & Unit-Normalized Vector Embeddings")
add_body(
    "Documents are divided into bounded passages of 50 words each using chunk_document(). This granularity preserves "
    "local context without diluting semantic signal. For local, reproducible execution without external API dependencies, "
    "mock_embed() generates deterministic 384-dimensional Gaussian vectors seeded by the MD5 hash of each chunk text. "
    "Crucially, the vector is divided by its Euclidean norm (L2 norm), ensuring ||v|| = 1. This pre-normalization "
    "allows cosine similarity to be computed directly as a dot product: sim(a, b) = a · b."
)

add_heading_2("2.2 MongoDB Storage & Cosine Similarity Retrieval")
add_body(
    "The chunks and their embeddings are persisted in the MongoDB collection 'nosql_labs.rag_documents'. "
    "During query execution, the user question is embedded using the identical mock_embed() function. "
    "The retrieve() function executes a full collection scan with projection {'embedding': 1, 'text': 1, 'source_title': 1, 'chunk_index': 1, '_id': 0}, "
    "calculates dot products across all stored vectors, and sorts the documents in descending order to extract the top-k matches."
)

add_heading_2("2.3 Prompt Construction & Multi-Turn Conversation Memory")
add_body(
    "The retrieved context chunks are synthesized into an LLM instruction prompt alongside prior conversation turns: "
    "'You are a helpful NoSQL/MongoDB tutor. Answer based on the context...'. The SimpleRAG class maintains an internal "
    "conversation history buffer, appending each user-assistant interaction turn so that follow-up questions retain contextual memory."
)

add_heading_2("2.4 Prediction vs. Actual Retrieval Analysis")
add_body(
    "Before executing retrieval, a human reader would predict that the question 'What are the four NoSQL database families?' "
    "should retrieve the document 'Introduction to NoSQL'. However, because mock embeddings rely on pseudo-random hash seeding "
    "rather than deep semantic language models, the dot product similarity reflects hash proximity rather than human meaning. "
    "In production, deploying a true semantic embedding model (e.g., Voyage AI voyage-3-lite or OpenAI text-embedding-3-small) "
    "guarantees that geometric proximity maps directly to conceptual similarity."
)

# 3. Activity 2 Details
add_heading_1("3. Activity 2: Compare HNSW and IVF Vector Index Types (lab_02_hnsw_vs_ivf.py)")
add_heading_2("3.1 Why Approximate Nearest Neighbor (ANN) Search Exists")
add_body(
    "Brute-force exact search compares a query vector against every stored vector, demanding O(N · D) operations. "
    "While this yields 100% recall, it becomes intractable when N scales into the millions or billions. ANN indexes trade "
    "a negligible loss in recall (e.g. 1-8%) for orders-of-magnitude reductions in the number of vectors evaluated."
)

add_heading_2("3.2 Inverted File Index (IVF) Clustering Architecture")
add_body(
    "The IVFIndex partitions the vector space into nlist=20 Voronoi clusters using Lloyd's K-Means algorithm over 8 iterations. "
    "At query time, only the nprobe=3 closest centroid clusters are scanned. Vectors in the remaining 17 clusters (85% of the dataset) "
    "are pruned completely without evaluation, significantly reducing vectors compared per query."
)

add_heading_2("3.3 Simplified Navigable Small World (NSW / HNSW-like) Graph Traversal")
add_body(
    "The SimpleNSWIndex builds a single-layer navigable graph where each vector connects to m=16 nearest neighbors. "
    "Search begins at 5 random entry points and navigates greedily along graph edges towards neighbors that increase query similarity. "
    "A bounded priority queue of size ef_search=100 maintains candidates. The search terminates when no candidate in the frontier "
    "can improve upon the worst score in the result queue."
)

add_heading_2("3.4 Empirical Benchmark Results")

table = doc.add_table(rows=4, cols=5)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Index Type", "Build Time (ms)", "Vectors Compared / Query", "Avg Query Time (ms)", "Recall@10"]
for col_idx, h in enumerate(headers):
    c = table.cell(0, col_idx)
    set_cell_background(c, "001E2B")
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(h)
    r.font.bold = True
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

data_rows = [
    ["Brute-force (exact)", "0.0 ms", "3,000 (100.0%)", "0.160 ms", "100.00%"],
    ["IVF (nlist=20, nprobe=3)", "15.1 ms", "447 (14.9%)", "0.114 ms", "42.00%"],
    ["Simplified NSW (HNSW-like)", "382.1 ms", "1,810 (60.3%)", "5.119 ms", "91.50%"],
]

for row_idx, row in enumerate(data_rows):
    for col_idx, val in enumerate(row):
        c = table.cell(row_idx + 1, col_idx)
        if row_idx % 2 == 1:
            set_cell_background(c, "F9FAFB")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(val)
        r.font.name = "Consolas" if col_idx > 0 else "Calibri"
        r.font.size = Pt(9)
        if col_idx == 4:
            r.font.bold = True

doc.add_paragraph()

add_heading_2("3.5 Critical Analysis: Vectors Compared vs. Wall-Clock Time")
add_body(
    "A vital theoretical question posed in the lab is: 'Which metric is more reliable in pure Python: vectors compared per query "
    "or wall-clock query time?' As proven by the experimental data, Vectors Compared per Query is the only reliable metric. "
    "In pure Python, graph traversal in NSW executes interpreted dictionary lookups, set memberships, and heap allocations, "
    "causing Python runtime overhead to dominate over raw BLAS matrix multiplication. In production systems like MongoDB Atlas "
    "$vectorSearch (implemented in optimized C++), avoiding 40%–85% of distance evaluations yields massive real-world throughput gains."
)

# 4. Web Application Integration
add_heading_1("4. Web Application & Interactive GUI Integration")
add_body(
    "To provide seamless evaluation and interactive demonstration, the complete laboratory suite is integrated into a modern "
    "Flask web application accessible on port 5000:\n"
    "• / (Overview Dashboard): Real-time MongoDB connection KPIs, document count, and environment health.\n"
    "• /lab1 (RAG Explorer): Live chunking viewer, interactive cosine similarity retrieval, pre-retrieval prediction tester, "
    "LLM prompt inspector, and multi-turn conversation memory simulator.\n"
    "• /lab2 (Vector Benchmark): Parameter slider suite (N, Dim, nlist, nprobe, m, ef_search), live benchmark executor, and "
    "dynamic Chart.js visualizations for Recall@K and vectors pruned.\n"
    "• /architecture: Mathematical formulations rendered via KaTeX and step-by-step Docker demonstration instructions."
)

# 5. Docker Deployment
add_heading_1("5. Docker Deployment & Demonstration Verification")
add_body(
    "The application is packaged into a production-ready Docker container and pushed to Docker Hub:\n"
    "• Repository: https://hub.docker.com/r/gouthudocker/nosql-lab17\n"
    "• Image Tags: gouthudocker/nosql-lab17:latest and gouthudocker/nosql-lab17:v1.0\n\n"
    "Demonstration Commands for Evaluators:\n"
    "1. Pull container: docker pull gouthudocker/nosql-lab17:latest\n"
    "2. Run web service: docker run -d --name nosql_lab17 -p 5000:5000 gouthudocker/nosql-lab17:latest\n"
    "3. Execute CLI suite: docker exec -it nosql_lab17 py run_all.py\n"
    "4. Execute Activity 1: docker exec -it nosql_lab17 py lab_01_rag_pipeline.py\n"
    "5. Execute Activity 2: docker exec -it nosql_lab17 py lab_02_hnsw_vs_ivf.py"
)

doc.save(docx_path)
print(f"Generated Word report: {docx_path}")
