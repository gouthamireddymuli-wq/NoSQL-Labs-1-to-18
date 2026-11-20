from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT = "Lab9_DockerSubmission.pdf"
W, H = A4

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2*cm
)

# ── Styles ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
NAVY   = colors.HexColor('#1a1a2e')
BLUE   = colors.HexColor('#4a4a8a')
LINK   = colors.HexColor('#0066cc')
GREY   = colors.HexColor('#333333')
MID    = colors.HexColor('#555555')
GREEN  = colors.HexColor('#2d6a4f')
ORANGE = colors.HexColor('#c05000')
PURPLE = colors.HexColor('#5e35b1')

def sty(name, **kw):
    base = kw.pop('parent', styles['Normal'])
    return ParagraphStyle(name, parent=base, **kw)

title_sty    = sty('T', parent=styles['Title'], fontSize=20, spaceAfter=4,
                   textColor=NAVY, alignment=TA_CENTER, fontName='Helvetica-Bold')
sub_sty      = sty('S', fontSize=11, textColor=BLUE, alignment=TA_CENTER, spaceAfter=3)
h1_sty       = sty('H1', fontSize=15, textColor=NAVY, spaceBefore=18, spaceAfter=6,
                   fontName='Helvetica-Bold')
h2_sty       = sty('H2', fontSize=12, textColor=BLUE, spaceBefore=10, spaceAfter=4,
                   fontName='Helvetica-Bold')
body_sty     = sty('B', fontSize=10.5, textColor=GREY, spaceAfter=5, leading=16,
                   alignment=TA_JUSTIFY)
bullet_sty   = sty('BL', fontSize=10.5, textColor=GREY, spaceAfter=4, leading=15,
                   leftIndent=18, firstLineIndent=-14)
url_sty      = sty('URL', fontSize=12, textColor=LINK, fontName='Helvetica-Bold',
                   alignment=TA_CENTER, spaceAfter=4, leading=18)
info_sty     = sty('INF', fontSize=10, textColor=MID, spaceAfter=3)
caption_sty  = sty('CAP', fontSize=9, textColor=MID, alignment=TA_CENTER,
                   spaceAfter=6, fontName='Helvetica-Oblique')
code_sty     = sty('CODE', fontSize=9.5, textColor=GREEN, fontName='Courier',
                   spaceAfter=3, leading=14)
highlight_sty= sty('HL', fontSize=10.5, textColor=ORANGE, fontName='Helvetica-Bold',
                   spaceAfter=4)

COL = 16.5*cm  # full usable width

def hr(c=BLUE, t=0.8): return HRFlowable(width="100%", thickness=t, color=c)

def box(content_para, bg, border):
    t = Table([[content_para]], colWidths=[COL])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('BOX',        (0,0), (-1,-1), 1.2, border),
        ('LEFTPADDING',  (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
    ]))
    return t

def kv_table(rows, col1=4.5*cm, col2=12*cm):
    data = [[Paragraph(f'<b>{k}</b>', info_sty), Paragraph(v, info_sty)] for k,v in rows]
    t = Table(data, colWidths=[col1, col2])
    t.setStyle(TableStyle([
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#f5f5ff'), colors.white]),
        ('BOTTOMPADDING', (0,0),(-1,-1), 7),
        ('TOPPADDING',    (0,0),(-1,-1), 7),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#ddddee')),
    ]))
    return t

# ════════════════════════════════════════════════════════════════════════════
story = []

# ── PAGE 1: Cover / Submission Info ─────────────────────────────────────────
story += [
    Spacer(1, 0.4*cm),
    Paragraph("NoSQL Lab 9 — Docker Submission", title_sty),
    Paragraph("MongoDB Write Concerns &amp; Network Partition Simulation", sub_sty),
    Spacer(1, 0.3*cm),
    hr(NAVY, 2),
    Spacer(1, 0.5*cm),
]

story.append(kv_table([
    ("Student Name:", "M Gouthami"),
    ("Student ID:",   "24BTRCL130"),
    ("Course:",       "NoSQL Database Systems"),
    ("Lab:",          "Lab 09 — Chapter 9"),
    ("Submission:",   "Docker Hub Image + PDF"),
    ("Date:",         "November 2026"),
]))

story += [Spacer(1, 0.6*cm), Paragraph("🐳  Docker Hub URL", h1_sty), hr()]
story.append(Spacer(1, 0.3*cm))

DOCKER_URL  = "https://hub.docker.com/r/gouthudocker/nosql-lab-9"
DOCKER_PULL = "docker pull gouthudocker/nosql-lab-9:latest"

story.append(box(
    Paragraph(f'<link href="{DOCKER_URL}">{DOCKER_URL}</link>', url_sty),
    colors.HexColor('#eef4ff'), LINK
))
story += [Spacer(1, 0.3*cm), Paragraph("Pull &amp; Run Commands:", h2_sty)]
for cmd in [DOCKER_PULL,
            "docker compose up",
            "# Then open:  http://localhost:5000"]:
    story.append(Paragraph(cmd, code_sty))

story += [Spacer(1, 0.5*cm), Paragraph("📋  Lab Contents", h1_sty), hr()]
story.append(Spacer(1, 0.3*cm))
contents = [
    ("Activity 9.1",         "Write Concern Latency Benchmark — 1,000 inserts across w:1 / w:majority / w:all"),
    ("Activity 9.1 TIY",     "Try-It-Yourself: Custom write concern experiments & analysis"),
    ("Activity 9.2",         "Network Partition Simulation — isolate a secondary, observe CAP behaviour"),
    ("Activity 9.2 TIY",     "Try-It-Yourself: Partition tolerance deep-dive & oplog catch-up"),
    ("Web Dashboard",        "Flask app on port 5000 — interactive results, charts & live demo"),
    ("Lab Report (PDF/DOCX)","Full written report with screenshots, data tables and conclusions"),
]
c_data = [[Paragraph(f'<b>{r}</b>',info_sty), Paragraph(d,info_sty)] for r,d in contents]
ct = Table(c_data, colWidths=[4.2*cm, 12.3*cm])
ct.setStyle(TableStyle([
    ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#f9f9ff'), colors.white]),
    ('BOTTOMPADDING',(0,0),(-1,-1), 7),
    ('TOPPADDING',   (0,0),(-1,-1), 7),
    ('LEFTPADDING',  (0,0),(-1,-1), 10),
    ('GRID',         (0,0),(-1,-1), 0.5, colors.HexColor('#e0e0ee')),
]))
story.append(ct)

story.append(PageBreak())

# ── PAGE 2: Activity 9.1 Explanation ────────────────────────────────────────
story += [
    Paragraph("Activity 9.1 — Write Concern Latency Benchmark", h1_sty),
    hr(NAVY, 1.5),
    Spacer(1, 0.3*cm),
]

story += [
    Paragraph("<b>Objective</b>", h2_sty),
    Paragraph(
        "Measure how different MongoDB write concern levels affect write latency and throughput "
        "on a 3-node replica set (rs0). The experiment inserted <b>1,000 documents</b> per "
        "configuration and recorded per-operation wall-clock latency using high-resolution timers.",
        body_sty),
]

story += [Spacer(1,0.2*cm), Paragraph("<b>Write Concern Levels Tested</b>", h2_sty)]
wc_rows = [
    ["w:1\n(Primary Only)",       "MongoDB returns success as soon as the <b>primary node</b> writes the document to its in-memory buffer. No replication wait. Fastest possible path.",
     "0.323 ms avg", "3,029 ops/s"],
    ["w:majority\n(Quorum 2/3)",  "MongoDB waits until at least <b>2 out of 3 nodes</b> (the majority) acknowledge the write. Guarantees the write survives a primary crash.",
     "2.014 ms avg", "4,540 ops/s"],
    ["w:all / w:3\n(All Nodes)",  "MongoDB waits until <b>all 3 nodes</b> confirm the write. Maximum durability — but latency is dictated by the slowest node.",
     "3.618 ms avg", "4,458 ops/s"],
]
wc_data = [[
    Paragraph('<b>Level</b>',   info_sty),
    Paragraph('<b>How it works</b>', info_sty),
    Paragraph('<b>Avg Latency</b>', info_sty),
    Paragraph('<b>Throughput</b>',  info_sty),
]] + [[Paragraph(r,info_sty), Paragraph(d,info_sty),
       Paragraph(f'<b>{l}</b>', highlight_sty), Paragraph(t, info_sty)]
      for r,d,l,t in wc_rows]
wct = Table(wc_data, colWidths=[2.8*cm, 7.5*cm, 2.8*cm, 3.4*cm])
wct.setStyle(TableStyle([
    ('BACKGROUND',   (0,0),(-1,0),  BLUE),
    ('TEXTCOLOR',    (0,0),(-1,0),  colors.white),
    ('FONTNAME',     (0,0),(-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',     (0,0),(-1,-1), 9.5),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f5f5ff'), colors.white]),
    ('GRID',         (0,0),(-1,-1), 0.5, colors.HexColor('#ccccdd')),
    ('VALIGN',       (0,0),(-1,-1), 'TOP'),
    ('BOTTOMPADDING',(0,0),(-1,-1), 8),
    ('TOPPADDING',   (0,0),(-1,-1), 8),
    ('LEFTPADDING',  (0,0),(-1,-1), 8),
]))
story.append(wct)

story += [Spacer(1,0.4*cm), Paragraph("<b>Key Observations</b>", h2_sty)]
obs = [
    "• <b>w:1</b> is the fastest (0.323 ms) — ideal for high-throughput, loss-tolerant workloads such as "
    "analytics event logs or time-series telemetry where occasional write loss is acceptable.",
    "• <b>w:majority</b> adds only ~1.7 ms of overhead compared to w:1, while providing strong durability "
    "guarantees. This is MongoDB's recommended default for production systems. Any write acknowledged at "
    "majority cannot be rolled back, even if the primary crashes immediately after.",
    "• <b>w:all</b> has the highest latency (3.618 ms) and is bound by the <i>slowest</i> secondary node "
    "(tail-latency sensitivity). It offers maximum durability but trades availability — if any secondary "
    "becomes unreachable, writes will block or fail.",
    "• The P99 latency for w:1 (1.149 ms) stays well below the P50 of w:all (3.548 ms), showing that "
    "the latency distributions do not overlap significantly — each tier is architecturally distinct.",
]
for o in obs:
    story.append(Paragraph(o, bullet_sty))

story += [Spacer(1,0.3*cm), Paragraph("<b>CAP Theorem Context</b>", h2_sty),
    Paragraph(
        "MongoDB replica sets are a <b>CP system</b> (Consistency + Partition Tolerance). "
        "Write concerns let the developer tune exactly where on the C–A spectrum each operation sits: "
        "w:1 leans toward <b>Availability</b> (always fast, slight consistency risk), while w:majority "
        "and w:all lean toward <b>Consistency</b> (guaranteed durability at the cost of latency).",
        body_sty),
]

story.append(PageBreak())

# ── PAGE 3: Activity 9.2 Explanation ────────────────────────────────────────
story += [
    Paragraph("Activity 9.2 — Network Partition Simulation", h1_sty),
    hr(NAVY, 1.5),
    Spacer(1, 0.3*cm),
]

story += [
    Paragraph("<b>Objective</b>", h2_sty),
    Paragraph(
        "Simulate a real network partition by disconnecting one secondary node "
        "(<b>mongo-rs0-2:27018</b>) from the Docker network, observe how the replica set "
        "maintains quorum, test write concern behaviour during the partition, and verify "
        "automatic oplog catch-up once the partition is healed.",
        body_sty),
]

story += [Spacer(1,0.2*cm), Paragraph("<b>Experiment Steps &amp; Results</b>", h2_sty)]

steps = [
    ("Step 1 — Healthy Baseline",
     "All 3 nodes healthy (1 PRIMARY + 2 SECONDARY). Baseline writes confirmed:\n"
     "w:1 = 16.01 ms, w:majority = 14.19 ms. Quorum threshold: ≥ 2 votes.",
     colors.HexColor('#e8f5e9'), GREEN),

    ("Step 2 — Inject Partition",
     "Command issued: docker network disconnect mongo-cluster-net mongo-rs0-2\n"
     "mongo-rs0-2:27018 isolated. Heartbeat failure detected. Health → 0.\n"
     "Remaining quorum: mongo-rs0-1 (PRIMARY) + mongo-rs0-3 = 2/3 nodes = 66.7% > 50% threshold.\n"
     "Result: Primary RETAINS its role. No election triggered.",
     colors.HexColor('#fff3e0'), ORANGE),

    ("Step 3 — Writes During Partition",
     "w:1  → SUCCESS (1.70 ms) — Only primary ack needed; secondary absence irrelevant.\n"
     "w:majority → SUCCESS (3.17 ms) — Majority = 2 nodes. Primary + mongo-rs0-3 = quorum met.\n"
     "Key insight: w:majority survived the partition because the surviving 2 nodes satisfy quorum.",
     colors.HexColor('#e8eaf6'), PURPLE),

    ("Step 4 — 30-Second Drift Observation",
     "Partition held for 30 seconds. mongo-rs0-2 accumulated replication lag "
     "(simulated +1,000 ms/10 s). Writes continued flowing through the surviving majority pair "
     "without interruption, demonstrating MongoDB's partition tolerance.",
     colors.HexColor('#fce4ec'), colors.HexColor('#b71c1c')),

    ("Step 5 — Partition Healed & Oplog Sync",
     "Command: docker network connect mongo-cluster-net mongo-rs0-2\n"
     "Heartbeat restored. mongo-rs0-2 transitioned: STARTUP2 → RECOVERING → SECONDARY.\n"
     "Oplog catch-up completed in ~3.2 seconds. All 3 nodes back in sync (0 ms lag).",
     colors.HexColor('#e0f7fa'), colors.HexColor('#006064')),
]

for title, desc, bg, border in steps:
    block = KeepTogether([
        Paragraph(f'<b>{title}</b>', h2_sty),
        box(Paragraph(desc.replace('\n', '<br/>'), body_sty), bg, border),
        Spacer(1, 0.25*cm),
    ])
    story.append(block)

story += [Spacer(1,0.2*cm), Paragraph("<b>Partition Metrics Summary</b>", h2_sty)]
pm_data = [[
    Paragraph('<b>Operation</b>', info_sty),
    Paragraph('<b>Result</b>',   info_sty),
    Paragraph('<b>Latency (ms)</b>', info_sty),
    Paragraph('<b>Notes</b>',    info_sty),
]] + [
    [Paragraph(r, info_sty), Paragraph(s, info_sty),
     Paragraph(l, info_sty), Paragraph(n, info_sty)]
    for r,s,l,n in [
        ("Baseline w:1",         "✅ SUCCESS", "16.01", "Primary ack"),
        ("Baseline w:majority",  "✅ SUCCESS", "14.19", "Quorum ack (2/3)"),
        ("Partitioned w:1",      "✅ SUCCESS", "1.70",  "Local write OK"),
        ("Partitioned w:majority","✅ SUCCESS","3.17",  "Surviving majority"),
        ("Oplog Catch-Up",       "✅ COMPLETE","—",     "3.2 s full sync"),
    ]
]
pmt = Table(pm_data, colWidths=[4*cm, 2.8*cm, 3.5*cm, 6.2*cm])
pmt.setStyle(TableStyle([
    ('BACKGROUND',   (0,0),(-1,0),  NAVY),
    ('TEXTCOLOR',    (0,0),(-1,0),  colors.white),
    ('FONTNAME',     (0,0),(-1,0),  'Helvetica-Bold'),
    ('FONTSIZE',     (0,0),(-1,-1), 9.5),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f5f5ff'), colors.white]),
    ('GRID',         (0,0),(-1,-1), 0.5, colors.HexColor('#ccccdd')),
    ('BOTTOMPADDING',(0,0),(-1,-1), 7),
    ('TOPPADDING',   (0,0),(-1,-1), 7),
    ('LEFTPADDING',  (0,0),(-1,-1), 8),
]))
story.append(pmt)

story += [
    Spacer(1,0.4*cm),
    Paragraph("<b>Conclusion</b>", h2_sty),
    Paragraph(
        "Lab 9 demonstrates two fundamental distributed-systems trade-offs in MongoDB: "
        "(1) <b>Durability vs. Latency</b> — write concerns let you choose where on the spectrum "
        "each write lands, and (2) <b>Availability vs. Consistency under partitions</b> — MongoDB's "
        "majority quorum ensures the cluster keeps accepting writes even with one failed node, "
        "while oplog-based replication guarantees the partition heals automatically with zero data loss. "
        "These properties make MongoDB well-suited for production systems that require both "
        "high throughput and strong consistency guarantees.",
        body_sty),
    Spacer(1,0.5*cm),
    hr(NAVY, 1),
    Spacer(1,0.2*cm),
    Paragraph("Submitted for NoSQL Lab 09 — M Gouthami (24BTRCL130)", sub_sty),
    Paragraph(f'Docker Image: <link href="{DOCKER_URL}">{DOCKER_URL}</link>',
              sty('FL', fontSize=9, textColor=LINK, alignment=TA_CENTER)),
]

doc.build(story)
print(f"PDF created: {OUTPUT}")
