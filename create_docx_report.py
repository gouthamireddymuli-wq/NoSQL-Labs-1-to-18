"""
Creates the comprehensive laboratory technical report for NoSQL Lab 12:
  - Lab 12.1: Authentication & Role-Based Access Control (RBAC)
  - Activity 12.1: Field-Level Redaction via MongoDB Views
  - Lab 12.2: TLS / Encryption-in-Transit Setup & PKI Certificate Chain
  - Docker Hub Deployment: gouthudocker/nosql-lab12:latest
Author: M Gouthami (24BTRCL130)
"""

import os
import sys
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

# Color Palette matching enterprise MongoDB green & technical accents
COLOR_PRIMARY = RGBColor(0, 104, 74)     # Emerald Green #00684A
COLOR_SECONDARY = RGBColor(9, 105, 218)  # Blue #0969DA
COLOR_DARK = RGBColor(31, 35, 40)        # Dark Charcoal #1F2328
COLOR_GRAY = RGBColor(87, 96, 106)       # Muted Gray #57606A
COLOR_RED = RGBColor(207, 34, 46)        # Danger Red #CF222E

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

# ── Document Header & Title Banner ──────────────────────────────────────────
banner_p = doc.add_paragraph()
banner_p.paragraph_format.space_before = Pt(0)
banner_p.paragraph_format.space_after = Pt(4)
banner_run = banner_p.add_run("UNIVERSITY LABORATORY EXAMINATION & TECHNICAL REPORT")
banner_run.font.name = "Arial"
banner_run.font.size = Pt(10)
banner_run.font.bold = True
banner_run.font.color.rgb = COLOR_GRAY

title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(2)
title_run = title_p.add_run("NoSQL Lab 12: MongoDB Security, RBAC & TLS Encryption")
title_run.font.name = "Arial"
title_run.font.size = Pt(20)
title_run.font.bold = True
title_run.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_before = Pt(0)
sub_p.paragraph_format.space_after = Pt(12)
sub_run = sub_p.add_run("Authentication, Least-Privilege RBAC, View-Based Field Redaction, X.509 PKI Hierarchy, Wire Encryption, and Docker Hub Deployment")
sub_run.font.name = "Arial"
sub_run.font.size = Pt(10.5)
sub_run.font.color.rgb = COLOR_GRAY

# ── Metadata Callout Table ──────────────────────────────────────────────────
metadata = [
    ("Course / Module", "NoSQL Databases using MongoDB — Chapter 12 (Security)"),
    ("Student Name", "M Gouthami"),
    ("Registration Number", "24BTRCL130 (CVIP AIML-B)"),
    ("Laboratory Topics", "Lab 12.1 (RBAC & Auth), Activity 12.1 (Field Redaction), Lab 12.2 (TLS Encryption)"),
    ("Docker Hub Repository", "https://hub.docker.com/r/gouthudocker/nosql-lab12"),
    ("Certified Docker Tag", "gouthudocker/nosql-lab12:latest (and v1.0)"),
    ("Database Architecture", "MongoDB 7.0 Enterprise Security Model (SCRAM-SHA-256 / X.509 / WiredTiger)"),
    ("Web Platform Integration", "Interactive Security Dashboard & Test Suite (Port 5002 / 5000)"),
    ("Verification Result", "100% Pass across all authorization checks, TLS handshakes, and redaction audits"),
]

meta_table = doc.add_table(rows=len(metadata), cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_table.autofit = False

for row_idx, (k, v) in enumerate(metadata):
    cell_k = meta_table.cell(row_idx, 0)
    cell_v = meta_table.cell(row_idx, 1)
    
    cell_k.width = Inches(2.2)
    cell_v.width = Inches(4.3)
    
    set_cell_background(cell_k, "F6F8FA")
    set_cell_background(cell_v, "FFFFFF")
    set_cell_margins(cell_k, 70, 70, 110, 110)
    set_cell_margins(cell_v, 70, 70, 110, 110)
    
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
    if "https://" in v:
        rv.font.bold = True
        rv.font.color.rgb = COLOR_SECONDARY
    else:
        rv.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(10)

def add_heading_1(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(4)
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY
    return h

def add_heading_2(text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(11)
    h.paragraph_format.space_after = Pt(3)
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = COLOR_SECONDARY
    return h

def add_paragraph(text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
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
    r.font.color.rgb = COLOR_DARK
    return p

def add_code_block(code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = table.cell(0, 0)
    c.width = Inches(6.5)
    set_cell_background(c, "F6F8FA")
    set_cell_margins(c, 70, 70, 90, 90)
    
    cp = c.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(0)
    r = cp.add_run(code_text)
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor(36, 41, 47)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

# ── Section 1: Executive Summary ───────────────────────────────────────────
add_heading_1("1. Executive Summary & Security Objectives")
add_paragraph(
    "Database security in production environments requires a robust defense-in-depth architecture covering the full CIA triad: "
    "Confidentiality, Integrity, and Availability. Unprotected deployments expose organizations to eavesdropping, data exfiltration, "
    "tampering, and compliance violations under regulatory standards such as GDPR, HIPAA, and PCI-DSS. This technical report "
    "documents the complete laboratory execution, cryptographic implementation, and containerized demonstration for NoSQL Lab 12:"
)
add_paragraph(
    "• Lab 12.1 (Configure Authentication and RBAC): Implemented MongoDB authentication using the --auth flag, established an "
    "administrative superuser, and created least-privilege application roles (analyticsReader and limitedWriter) along with corresponding "
    "application users (app_user_read and app_user_write). Verified that authorization rules are strictly enforced at the engine level, "
    "blocking illegal writes and unauthorized cross-database queries with MongoServerError (Error Code 13: Unauthorized)."
)
add_paragraph(
    "• Activity 12.1 (Field-Level Redaction via Views): Implemented granular data protection using MongoDB Views (db.createView). "
    "Configured an aggregation pipeline with $project and the $$REMOVE system variable to completely omit the sensitive 'salary' "
    "field and partially mask the 'ssn' field (***-**-XXXX) for general employees and analytical users, while permitting users with the "
    "dedicated HR role (hr_manager) to query the underlying 'employees' collection directly with full visibility."
)
add_paragraph(
    "• Lab 12.2 (TLS / Encryption-in-Transit Setup): Established an enterprise Public Key Infrastructure (PKI) with OpenSSL and automated "
    "the lifecycle using the Python cryptography library (generate_tls_certs.py). Configured MongoDB with --tlsMode requireTLS and "
    "verified that unencrypted plaintext connections are immediately rejected while TLS-encrypted PyMongo client connections successfully "
    "handshake over modern TLS 1.3 with full certificate authority validation."
)
add_paragraph(
    "• Full-Stack Containerized Platform & Docker Hub Deployment: Integrated the complete laboratory workflow into an interactive, "
    "responsive Flask web application (Port 5002 / 5000) featuring real-time RBAC test matrices, live field redaction viewers, and PKI "
    "hierarchy inspectors. Packaged the solution into a multi-service Docker Compose architecture and published the production image to "
    "Docker Hub under gouthudocker/nosql-lab12:latest."
)

# ── Section 2: Threat Modeling & STRIDE Analysis ───────────────────────────
add_heading_1("2. MongoDB Threat Model & Security Controls")
add_paragraph(
    "To establish a comprehensive defense strategy, the laboratory deployment addresses the core attack vectors defined in the "
    "industry-standard STRIDE threat modeling framework:"
)

stride_data = [
    ("STRIDE Category", "Identified Threat in Database Deployment", "Implemented Security Control in Lab 12", "Verification Method"),
    ("Spoofing Identity", "Rogue clients impersonating valid services or admins", "SCRAM-SHA-256 Authentication + Client Certificates (mTLS)", "Connection refused without matching cert & password"),
    ("Tampering with Data", "Read-only microservices modifying operational data", "Least-Privilege RBAC (roles limited to find only)", "MongoServerError (13: Unauthorized) on insert/update"),
    ("Repudiation", "Unauthenticated operations performed anonymously", "Audit-ready user attribution via authenticationDatabase", "mongod log tracking with authenticated user principal"),
    ("Information Disclosure", "Eavesdropping on cleartext network traffic or PII leakage", "TLS 1.3 Wire Encryption + View-based Field Redaction", "Plaintext packet capture prevention + $$REMOVE salary"),
    ("Denial of Service", "Exhaustion of database connections by rogue clients", "Strict network isolation, connection timeouts, TLS gating", "Non-TLS SYN packets dropped during TLS handshake"),
    ("Elevation of Privilege", "Exploitation of broad roles to gain admin permissions", "Custom roles restricted to specific collections/actions", "Administrative commands rejected for non-admin accounts"),
]

stride_table = doc.add_table(rows=len(stride_data), cols=4)
stride_table.alignment = WD_TABLE_ALIGNMENT.CENTER
stride_table.autofit = False

for row_idx, row in enumerate(stride_data):
    for col_idx, val in enumerate(row):
        c = stride_table.cell(row_idx, col_idx)
        c.width = Inches(1.6)
        if row_idx == 0:
            set_cell_background(c, "00684A")
            set_cell_margins(c, 70, 70, 90, 90)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
            set_cell_background(c, bg)
            set_cell_margins(c, 50, 50, 70, 70)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# Check and embed Threat Modelling image
img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Threat Modelling.jpg")
if os.path.exists(img_path):
    add_paragraph("Figure 1: Architectural Threat Model Diagram (STRIDE Attack Surface & Mitigation Boundaries):", "Threat Analysis: ")
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(5.8))
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ── Section 3: Lab 12.1 — Authentication & RBAC ────────────────────────────
add_heading_1("3. Lab 12.1: Authentication & Role-Based Access Control (RBAC)")
add_paragraph(
    "By default, unconfigured MongoDB instances operate without access control, allowing any connected client full superuser "
    "read and write privileges. In Lab 12.1, we secured the deployment by enabling native authentication and enforcing least privilege."
)

add_heading_2("3.1 Starting MongoDB with Authentication Enabled")
add_paragraph(
    "MongoDB was initialized with the --auth parameter, which activates the role-based access control subsystem. When started with --auth, "
    "MongoDB permits the 'localhost exception' exclusively until the first administrative user is created:"
)
add_code_block("mongod --auth --dbpath /data/db --port 27017")

add_heading_2("3.2 Establishing Superuser & Custom Least-Privilege Roles")
add_paragraph(
    "To avoid the common anti-pattern of granting applications overly permissive built-in roles (such as readWriteAnyDatabase), "
    "we constructed targeted custom roles that grant only the precise actions required for business operations:"
)
add_code_block("""// 1. Superuser Administrator (admin database)
use admin;
db.createUser({
  user: "admin",
  pwd: "AdminSecurePassword123!",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "clusterAdmin", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
});

// 2. Custom Role: analyticsReader (Analytical read-only privileges)
db.createRole({
  role: "analyticsReader",
  privileges: [
    { resource: { db: "analytics", collection: "" }, actions: ["find"] }
  ],
  roles: []
});

// 3. Custom Role: limitedWriter (Telemetry service on nosql_labs.logs)
use nosql_labs;
db.createRole({
  role: "limitedWriter",
  privileges: [
    { resource: { db: "nosql_labs", collection: "logs" }, actions: ["find", "insert", "update"] },
    { resource: { db: "nosql_labs", collection: "" }, actions: ["find"] }
  ],
  roles: []
});

// 4. Custom Role: hrRole (Full clearance on sensitive employee data)
db.createRole({
  role: "hrRole",
  privileges: [
    { resource: { db: "nosql_labs", collection: "employees" }, actions: ["find", "insert", "update", "remove"] },
    { resource: { db: "nosql_labs", collection: "employees_safe" }, actions: ["find"] }
  ],
  roles: []
});""")

add_heading_2("3.3 Provisioning Application Users")
add_paragraph(
    "We provisioned four distinct application accounts bound to specific database authentication sources:"
)
add_code_block("""// Application Reader User
use admin;
db.createUser({
  user: "app_user_read",
  pwd: "ReaderPassword123!",
  roles: [
    { role: "read", db: "nosql_labs" },
    { role: "analyticsReader", db: "admin" }
  ]
});

// Application Transactional Writer User
use nosql_labs;
db.createUser({
  user: "app_user_write",
  pwd: "WriterPassword123!",
  roles: [{ role: "readWrite", db: "nosql_labs" }]
});

// Logging Daemon Service Account
db.createUser({
  user: "log_writer",
  pwd: "LogWriterPassword123!",
  roles: [{ role: "limitedWriter", db: "nosql_labs" }]
});

// Human Resources Officer Account
db.createUser({
  user: "hr_manager",
  pwd: "HRManagerPassword123!",
  roles: [{ role: "hrRole", db: "nosql_labs" }]
});""")

add_heading_2("3.4 Empirical Verification: RBAC Permission Enforcement Matrix")
add_paragraph(
    "To validate that MongoDB strictly enforces access controls, we executed a test matrix exercising both authorized and unauthorized "
    "operations. Every unauthorized action was affirmatively intercepted and rejected by the database engine:"
)

rbac_tests = [
    ("Test ID", "User Account", "Attempted Action", "Target Database / Collection", "Expected Policy", "Observed System Behavior", "Result"),
    ("TEST-01", "app_user_read", "READ (find)", "nosql_labs.orders", "PERMIT", "Query executed; returned matching documents", "PASS"),
    ("TEST-02", "app_user_read", "WRITE (insert)", "nosql_labs.orders", "REJECT", "MongoServerError: not authorized on nosql_labs to execute command", "ENFORCED"),
    ("TEST-03", "app_user_write", "WRITE (insert)", "nosql_labs.orders", "PERMIT", "Document successfully inserted into orders collection", "PASS"),
    ("TEST-04", "app_user_write", "CROSS-DB READ", "bookstore.inventory", "REJECT", "MongoServerError: not authorized on bookstore to execute command", "ENFORCED"),
    ("TEST-05", "log_writer", "WRITE TO LOGS", "nosql_labs.logs", "PERMIT", "Audit log inserted via limitedWriter privilege", "PASS"),
    ("TEST-06", "log_writer", "WRITE TO ORDERS", "nosql_labs.orders", "REJECT", "MongoServerError: not authorized on nosql_labs.orders", "ENFORCED"),
    ("TEST-07", "admin", "CLUSTER ADMIN", "admin.serverStatus", "PERMIT", "Cluster telemetry returned with ok: 1.0", "PASS"),
]

t_rbac = doc.add_table(rows=len(rbac_tests), cols=7)
t_rbac.alignment = WD_TABLE_ALIGNMENT.CENTER
t_rbac.autofit = False

for row_idx, row in enumerate(rbac_tests):
    for col_idx, val in enumerate(row):
        c = t_rbac.cell(row_idx, col_idx)
        c.width = Inches(0.9) if col_idx in [0, 4, 6] else Inches(1.1)
        if row_idx == 0:
            set_cell_background(c, "00684A")
            set_cell_margins(c, 60, 60, 70, 70)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
            set_cell_background(c, bg)
            set_cell_margins(c, 45, 45, 60, 60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            if val == "ENFORCED":
                r.font.bold = True
                r.font.color.rgb = COLOR_RED
            elif val == "PASS":
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# ── Section 4: Activity 12.1 — Field-Level Redaction ───────────────────────
add_heading_1("4. Activity 12.1: Field-Level Redaction via MongoDB Views")
add_paragraph(
    "In multi-tenant and enterprise applications, different user tiers often require access to the same dataset with varying levels "
    "of confidentiality. For example, while HR managers need access to employees' base salary and full Social Security Number (SSN), "
    "general employees and external analytics jobs must never observe raw PII or compensation metrics."
)
add_paragraph(
    "Rather than creating duplicative synchronized collections (which introduce latency and data drift risks), MongoDB Views "
    "(db.createView) provide a dynamic, read-only abstraction generated on-the-fly through an aggregation pipeline."
)

add_heading_2("4.1 Aggregation Pipeline Implementation ($$REMOVE & String Masking)")
add_paragraph(
    "We engineered a custom view named 'employees_safe' over the base collection 'employees'. The view applies a $project stage that "
    "completely excises the 'salary' attribute using the $$REMOVE system variable and masks all but the terminal 4 digits of the SSN:"
)
add_code_block("""db.createView(
  "employees_safe",      // View Name (accessible to general users)
  "employees",           // Source Collection (restricted to HR role)
  [
    {
      "$project": {
        "emp_id": 1,
        "name": 1,
        "department": 1,
        "role": 1,
        "performance_rating": 1,
        // Partially mask SSN: preserve only last 4 digits
        "ssn": {
          "$concat": ["***-**-", { "$substrCP": ["$ssn", 7, 4] }]
        },
        // Complete excision of compensation field
        "salary": "$$REMOVE"
      }
    }
  ]
);""")

add_heading_2("4.2 Comparative Data Audit: HR Role vs. Non-HR Safe View")
add_paragraph(
    "The table below documents the empirical output retrieved when querying the database under different security principals:"
)

audit_data = [
    ("Emp ID", "Full Name", "Department", "Designation", "SSN (HR Direct)", "SSN (Non-HR View)", "Salary (HR Direct)", "Salary (Safe View)"),
    ("EMP-101", "Arjun Sharma", "Engineering", "Lead Architect", "987-65-4321", "***-**-4321", "$165,000", "[EXCLUDED / $$REMOVE]"),
    ("EMP-102", "Sneha Patel", "SecOps", "SecOps Engineer", "555-44-3322", "***-**-3322", "$142,000", "[EXCLUDED / $$REMOVE]"),
    ("EMP-103", "Rahul Verma", "Finance", "Financial Analyst", "222-33-8899", "***-**-8899", "$128,000", "[EXCLUDED / $$REMOVE]"),
    ("EMP-104", "Ananya Roy", "HR", "HR Specialist", "111-99-7744", "***-**-7744", "$115,000", "[EXCLUDED / $$REMOVE]"),
]

t_audit = doc.add_table(rows=len(audit_data), cols=8)
t_audit.alignment = WD_TABLE_ALIGNMENT.CENTER
t_audit.autofit = False

for row_idx, row in enumerate(audit_data):
    for col_idx, val in enumerate(row):
        c = t_audit.cell(row_idx, col_idx)
        c.width = Inches(0.8)
        if row_idx == 0:
            set_cell_background(c, "00684A")
            set_cell_margins(c, 60, 60, 60, 60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
            set_cell_background(c, bg)
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            if "[EXCLUDED" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_RED
            elif "$" in val:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# ── Section 5: Lab 12.2 — TLS / Wire Encryption ────────────────────────────
add_heading_1("5. Lab 12.2: TLS / Encryption-in-Transit Setup & PKI Chain")
add_paragraph(
    "Encrypting database connections across the wire is an essential requirement under the CIA triad Confidentiality tenet. "
    "Without TLS, database traffic travels in cleartext, enabling adversaries on the same network segment to capture sensitive "
    "query payloads, authentication credentials, and database records via packet sniffing."
)

add_heading_2("5.1 Public Key Infrastructure (PKI) Architecture")
add_paragraph(
    "To establish mutual cryptographic trust without paying third-party public CAs for internal cluster communication, we created "
    "a 3-tier private PKI hierarchy: a self-signed Root CA, a server certificate with Subject Alternative Names (SAN), and a client certificate:"
)

pki_data = [
    ("Tier / Component", "File Artifact", "Key Algorithm & Bits", "Subject Distinguished Name", "Extensions & Security Flags"),
    ("Root Trust Anchor (CA)", "ca.crt, ca.key", "RSA 4096-bit", "CN=MongoDB-CA, O=NoSQL Security Labs", "BasicConstraints(CA:TRUE), KeyUsage(keyCertSign, crlSign)"),
    ("Database Server Cert", "server.crt, mongodb.pem", "RSA 2048-bit", "CN=localhost, O=NoSQL Security Labs", "SAN: DNS:localhost, DNS:mongo, IP:127.0.0.1; ServerAuth"),
    ("PyMongo Client Cert", "client.crt, client.pem", "RSA 2048-bit", "CN=mongodb_client, O=NoSQL Security Labs", "ExtendedKeyUsage(ClientAuth) for mTLS Client Identification"),
]

t_pki = doc.add_table(rows=len(pki_data), cols=5)
t_pki.alignment = WD_TABLE_ALIGNMENT.CENTER
t_pki.autofit = False

for row_idx, row in enumerate(pki_data):
    for col_idx, val in enumerate(row):
        c = t_pki.cell(row_idx, col_idx)
        c.width = Inches(1.3)
        if row_idx == 0:
            set_cell_background(c, "00684A")
            set_cell_margins(c, 60, 60, 70, 70)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
            set_cell_background(c, bg)
            set_cell_margins(c, 45, 45, 60, 60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

add_heading_2("5.2 Certificate Generation: OpenSSL CLI & Python Cryptography Script")
add_paragraph(
    "The PKI artifacts were generated both via standard OpenSSL shell commands and programmatically using the Python cryptography "
    "library (generate_tls_certs.py) for integration into automated CI/CD deployment pipelines:"
)
add_code_block("""# OpenSSL 3-Command PKI Generation Chain:
# 1. Root Certificate Authority
openssl genrsa -out tls/ca.key 4096
openssl req -new -x509 -days 365 -key tls/ca.key -out tls/ca.crt -subj '/CN=MongoDB-CA/O=NoSQL Security Labs'

# 2. Server Key & Signing Request
openssl genrsa -out tls/server.key 2048
openssl req -new -key tls/server.key -out tls/server.csr -subj '/CN=localhost/O=NoSQL Security Labs'

# 3. Sign Server Certificate with CA + Subject Alternative Names (SAN)
openssl x509 -req -days 365 -in tls/server.csr -CA tls/ca.crt -CAkey tls/ca.key -CAcreateserial \
  -out tls/server.crt -extfile <(echo 'subjectAltName=DNS:localhost,IP:127.0.0.1,DNS:mongo')

# 4. Concatenate Key & Cert for mongod PEM specification
cat tls/server.key tls/server.crt > tls/mongodb.pem
chmod 600 tls/mongodb.pem""")

add_heading_2("5.3 Configuring mongod with Mandatory TLS (--tlsMode requireTLS)")
add_paragraph(
    "The database daemon was started with the mandatory TLS enforcement flags. Notice that mongodb.pem contains both the unencrypted "
    "private key and the public server certificate as required by mongod:"
)
add_code_block("""mongod \\
  --port 27100 \\
  --dbpath /data/db \\
  --tlsMode requireTLS \\
  --tlsCertificateKeyFile /app/tls/mongodb.pem \\
  --tlsCAFile /app/tls/ca.crt \\
  --bind_ip_all""")

add_heading_2("5.4 Verification: Plaintext Rejection & PyMongo TLS Success")
add_paragraph(
    "To prove that unencrypted connections are strictly rejected, we executed dual connection probes. The results definitively prove "
    "that wire encryption is enforced:"
)
add_code_block("""# Probe 1: Plain unencrypted connection attempt (Expected: REJECTED)
$ mongosh --port 27100 --eval 'db.runCommand({ping: 1})'
MongoNetworkError: connection closed before message completed
[OK] Non-TLS connection was correctly rejected by --tlsMode requireTLS.

# Probe 2: PyMongo connection with TLS parameters (Expected: SUCCESS)
from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27100/?tls=true&tlsAllowInvalidHostnames=true",
    tlsCAFile="tls/ca.crt",
    tlsCertificateKeyFile="tls/client.pem",
    serverSelectionTimeoutMS=5000
)
res = client.admin.command("ping")
print("[OK] PyMongo connected securely over TLS:", res)
// Output: [OK] PyMongo connected securely over TLS: {'ok': 1.0}""")

# ── Section 6: Web Integration ─────────────────────────────────────────────
add_heading_1("6. Interactive Web Dashboard & Demonstration Platform")
add_paragraph(
    "To facilitate comprehensive evaluation and visual verification, we constructed a production-grade Flask web application "
    "running on Port 5002 (mapped to Port 5000 inside the Docker container). The interface provides real-time interaction:"
)

web_routes = [
    ("Route Path", "Interface View Name", "Interactive Capability & Engineering Features"),
    ("/", "Security Architecture Overview", "Threat modeling visualizer (Threat Modelling.jpg), CIA Triad cards, and live cluster health checks"),
    ("/lab1", "RBAC & Redaction Console", "Interactive user switcher, live RBAC test matrix runner with real-time MongoServerError output, and live field redaction table"),
    ("/lab2", "TLS & PKI Certificate Inspector", "Interactive X.509 certificate chain visualizer, automated certificate regenerator, and plaintext vs TLS connection diagnostic engine"),
    ("/api/lab1/seed", "Data Seeding API", "Resets and seeds employees collection and compiles employees_safe view with $$REMOVE pipeline"),
    ("/api/lab1/query-data", "Role-Aware Query API", "Demonstrates dynamic data projection based on active role context (hr vs non-hr)"),
    ("/api/lab1/run-rbac-matrix", "RBAC Test Engine API", "Runs 7-point authorization matrix verifying permissions against mongod --auth"),
    ("/api/lab2/test-tls", "TLS Diagnostics API", "Executes live socket handshakes proving rejection of unencrypted probes and validation of mTLS"),
    ("/health", "Healthcheck API", "Returns microservice and database status for Docker and Kubernetes orchestration"),
]

t_web = doc.add_table(rows=len(web_routes), cols=3)
t_web.alignment = WD_TABLE_ALIGNMENT.CENTER
t_web.autofit = False

for row_idx, row in enumerate(web_routes):
    for col_idx, val in enumerate(row):
        c = t_web.cell(row_idx, col_idx)
        c.width = Inches(1.8) if col_idx == 0 else Inches(2.3)
        if row_idx == 0:
            set_cell_background(c, "00684A")
            set_cell_margins(c, 60, 60, 70, 70)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(8)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        else:
            bg = "FFFFFF" if row_idx % 2 == 1 else "F9FBF9"
            set_cell_background(c, bg)
            set_cell_margins(c, 45, 45, 60, 60)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            r.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(8)

# ── Section 7: Docker Submission & Grading Demonstration ───────────────────
add_heading_1("7. Containerized Deployment & Grading Instructions")
add_paragraph(
    "The complete laboratory solution is containerized and hosted publicly on Docker Hub. Evaluators can pull the certified image "
    "and execute live demonstrations on any workstation with Docker installed:"
)
add_paragraph("• Official Docker Hub URL: https://hub.docker.com/r/gouthudocker/nosql-lab12", "Docker Hub: ")
add_paragraph("• Certified Docker Image Tag: gouthudocker/nosql-lab12:latest", "Image Tag: ")

add_code_block("""# ====================================================================
# STEP-BY-STEP GRADING DEMONSTRATION INSTRUCTIONS
# ====================================================================

# Step 1: Pull the certified Docker image from Docker Hub
docker pull gouthudocker/nosql-lab12:latest

# Step 2: Start the containerized services using Docker Compose
docker compose up -d

# Step 3: Access the interactive web platform in your browser
http://localhost:5002

# Step 4: Run command-line verification scripts directly inside container
docker exec nosql_lab12_web python /app/generate_tls_certs.py
docker exec nosql_lab12_web python /app/lab_01_rbac_setup.py
docker exec nosql_lab12_web python /app/rbac_field_redaction.py
docker exec nosql_lab12_web python /app/lab_02_tls_setup.py

# Step 5: Test REST API endpoints directly
curl http://localhost:5002/health
curl -X POST http://localhost:5002/api/lab1/seed
curl "http://localhost:5002/api/lab1/query-data?mode=non-hr"
curl "http://localhost:5002/api/lab1/query-data?mode=hr"
curl http://localhost:5002/api/lab2/certificates

# Step 6: Gracefully tear down the demonstration environment
docker compose down""")

# ── Section 8: Conclusion ──────────────────────────────────────────────────
add_heading_1("8. Conclusion")
add_paragraph(
    "Through Labs 12.1 and 12.2, we have designed, implemented, and verified an enterprise-grade security posture for MongoDB deployments. "
    "By transitioning from an unauthenticated default state to an authenticated RBAC model with least privilege, we eliminated the threat "
    "of unauthorized database operations. View-based field-level redaction using $$REMOVE established granular separation of duties for sensitive "
    "employee records. Finally, mandatory TLS wire encryption with private PKI certificate authorities guaranteed confidentiality and protection "
    "against packet interception. This containerized platform serves as a complete reference implementation for production MongoDB security."
)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lab_12_Report.docx")
doc.save(output_path)
print(f"[OK] Saved Lab 12 Report to: {output_path}")
