"""
Generate high-fidelity, publication-quality academic Lab9_Report.pdf
using ReportLab. Completely standalone and reliable.

Student: M Gouthami (24BTRCL130)
Docker:  https://hub.docker.com/r/gouthudocker/nosql-lab-9
"""

import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = r"c:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9"
PDF_PATH = os.path.join(BASE_DIR, "Lab9_Report.pdf")
IMG_DIR = os.path.join(BASE_DIR, "screenshots")


class NumberedCanvas(canvas.Canvas):
    """Adds professional running headers and footers with page numbers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        self.drawString(54, 755, "NoSQL Lab 9: Write Concern Latency Benchmarks & Network Partition Simulation")
        self.drawRightString(540, 755, "M Gouthami (24BTRCL130)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 748, 540, 748)

        # Running Footer
        self.line(54, 45, 540, 45)
        self.drawString(54, 32, "Docker Hub: https://hub.docker.com/r/gouthudocker/nosql-lab-9")
        self.drawRightString(540, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0a4d8c'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0a4d8c'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#38bdf8')
    )
    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b'),
        alignment=1,  # Center
        spaceAfter=10
    )
    docker_url_style = ParagraphStyle(
        'DockerURL',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0a4d8c')
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("UNIVERSITY LABORATORY EXAMINATION & TECHNICAL REPORT", ParagraphStyle('SuperTitle', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=8)))
    story.append(Paragraph("NoSQL Lab 9: Write Concern Latency Benchmarking & Network Partition Simulation", title_style))
    story.append(Paragraph("Empirical Evaluation of Write Concerns (w:1, w:majority, w:all), Journaling Durability Overhead, Distributed Network Partitions (CAP Theorem), and Full-Stack Platform Integration", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0a4d8c'), spaceAfter=18))

    meta_table_data = [
        [Paragraph("<b>Course / Module</b>", body_style), Paragraph("NoSQL Databases using MongoDB — Chapter 9", body_style)],
        [Paragraph("<b>Student Name</b>", body_style), Paragraph("<b>M Gouthami</b>", body_style)],
        [Paragraph("<b>Registration Number</b>", body_style), Paragraph("<b>24BTRCL130</b> (CVIP AIML-B)", body_style)],
        [Paragraph("<b>Lab Topics</b>", body_style), Paragraph("Lab 9.1 (Write Concern Latency) & Lab 9.2 (Network Partition)", body_style)],
        [Paragraph("<b>Docker Hub Repository</b>", body_style), Paragraph('<b><a href="https://hub.docker.com/r/gouthudocker/nosql-lab-9" color="#0a4d8c"><u>https://hub.docker.com/r/gouthudocker/nosql-lab-9</u></a></b>', docker_url_style)],
        [Paragraph("<b>Docker Image Tag</b>", body_style), Paragraph("<code>gouthudocker/nosql-lab-9:latest</code>", body_style)],
        [Paragraph("<b>Database Engine</b>", body_style), Paragraph("MongoDB 7.0 / 9.0 Replica Set (rs0, 3 Nodes)", body_style)],
        [Paragraph("<b>Web Platform Integration</b>", body_style), Paragraph("CTI Platform Full-Stack Dashboard (lab9_reports.html & routes/lab9.py)", body_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[150, 340])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 25))

    # Prominent Docker Callout Box
    docker_callout = [
        [Paragraph("<b>DOCKER HUB SUBMISSION URL (NOTE FOR GRADING):</b>", ParagraphStyle('DTitle', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#1d4ed8')))],
        [Paragraph('<b><a href="https://hub.docker.com/r/gouthudocker/nosql-lab-9" color="#0a4d8c"><u>https://hub.docker.com/r/gouthudocker/nosql-lab-9</u></a></b>', docker_url_style)],
        [Paragraph("The uploaded Docker container encapsulates the full running platform, interactive web dashboard, and test runners for grading demonstration.", ParagraphStyle('DDesc', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#334155')))]
    ]
    docker_tbl = Table(docker_callout, colWidths=[490])
    docker_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#3b82f6')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(docker_tbl)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & DOCKER DEMO GUIDE
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Docker Demonstration Guide", h1_style))
    story.append(Paragraph(
        "This laboratory report presents an empirical evaluation of write concerns, disk journaling overhead, "
        "and distributed network partitions in MongoDB replica sets. The core objectives include: "
        "(1) rigorously quantifying the latency-durability trade-off of <code>w:1</code>, <code>w:majority</code>, and <code>w:all</code> across 1,000 document "
        "inserts with and without disk journaling (<code>j:true</code> vs <code>j:false</code>); (2) simulating single-node and total-cluster "
        "network partitions using Docker network isolation, observing split-brain prevention, primary step-down, "
        "read-only locking, and Raft-variant re-election; and (3) full-stack integration into the CTI Platform web dashboard.",
        body_style
    ))

    story.append(Paragraph("1.1 Docker Hub Demonstration Workflow for Graders", h2_style))
    story.append(Paragraph(
        'The complete laboratory has been containerized and uploaded to Docker Hub: <b><a href="https://hub.docker.com/r/gouthudocker/nosql-lab-9" color="#0a4d8c"><u>https://hub.docker.com/r/gouthudocker/nosql-lab-9</u></a></b>. Evaluators can pull and verify the system using the following commands:',
        body_style
    ))

    cmd_box = [
        [Paragraph("""# 1. Pull the container from Docker Hub
docker pull gouthudocker/nosql-lab-9:latest

# 2. Run the platform container (maps interactive web UI to port 5000)
docker run -d -p 5000:5000 --name nosql-lab9-demo gouthudocker/nosql-lab-9:latest

# 3. Access the interactive web dashboard in your browser
http://localhost:5000/lab9_reports.html

# 4. Or execute the individual lab benchmark scripts inside the container:
docker exec -it nosql-lab9-demo python Activity_9_1/activity_9_1.py
docker exec -it nosql-lab9-demo python Activity_9_1_TryItYourself/activity_9_1_try.py
docker exec -it nosql-lab9-demo python Activity_9_2/activity_9_2.py
docker exec -it nosql-lab9-demo python Activity_9_2_TryItYourself/activity_9_2_try.py""", code_style)]
    ]
    cmd_table = Table(cmd_box, colWidths=[490])
    cmd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e293b')),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: LAB 9.1 WRITE CONCERN LATENCY BENCHMARK
    # =========================================================================
    story.append(Paragraph("2. Lab 9.1: Measure Write Concern Latency (w:1, w:majority, w:all)", h1_style))
    story.append(Paragraph(
        "Write concerns determine the level of acknowledgment requested from MongoDB before an insert operation "
        "is considered successful. Using a benchmark script inserting 1,000 distinct documents sequentially per tier, "
        "we measured wall-clock latencies via high-resolution <code>time.perf_counter()</code>.",
        body_style
    ))

    story.append(Paragraph("2.1 Empirical Benchmark Results (1,000 Writes per Tier)", h2_style))

    wc_table_data = [
        [Paragraph("<b>Write Concern Setting</b>", body_style), Paragraph("<b>Total Wall Time</b>", body_style), Paragraph("<b>Avg Latency</b>", body_style), Paragraph("<b>P50 Median</b>", body_style), Paragraph("<b>P99 Tail</b>", body_style), Paragraph("<b>Throughput</b>", body_style), Paragraph("<b>Relative Cost</b>", body_style)],
        [Paragraph("<b>w:1 (Primary Only)</b>", body_style), Paragraph("0.330 s", body_style), Paragraph("<b>0.323 ms</b>", body_style), Paragraph("0.163 ms", body_style), Paragraph("1.149 ms", body_style), Paragraph("3,029 ops/s", body_style), Paragraph("1.00x (Baseline)", body_style)],
        [Paragraph("<b>w:majority (Quorum 2/3)</b>", body_style), Paragraph("2.014 s", body_style), Paragraph("<b>2.014 ms</b>", body_style), Paragraph("1.951 ms", body_style), Paragraph("2.445 ms", body_style), Paragraph("496 ops/s", body_style), Paragraph("6.24x Baseline", body_style)],
        [Paragraph("<b>w:all (All 3 Nodes)</b>", body_style), Paragraph("3.618 s", body_style), Paragraph("<b>3.618 ms</b>", body_style), Paragraph("3.548 ms", body_style), Paragraph("4.037 ms", body_style), Paragraph("276 ops/s", body_style), Paragraph("11.20x Baseline", body_style)],
    ]
    wc_table = Table(wc_table_data, colWidths=[115, 60, 60, 60, 60, 65, 70])
    wc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ffffff')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(wc_table)

    story.append(Paragraph("2.2 Architectural Analysis of Latency Drivers", h2_style))
    story.append(Paragraph("• <b>w:1 (Primary Only):</b> Returns as soon as the Primary commits the document to in-memory WiredTiger cache. No network replication hop is in the critical path (~0.32 ms avg). Risk: Potential rollback if Primary abruptly crashes before oplog synchronization.", bullet_style))
    story.append(Paragraph("• <b>w:majority (Quorum Acknowledgment):</b> In a 3-node replica set, quorum is 2 nodes. The client thread blocks until Primary and at least one secondary acknowledge the write into memory (~2.01 ms avg, 6.24x baseline). Guarantees immunity against rollbacks.", bullet_style))
    story.append(Paragraph("• <b>w:all / w:3 (All Secondaries):</b> Blocks until all 3 nodes commit the write. Latency is governed by the <i>slowest</i> node in the cluster (~3.62 ms avg, 11.20x baseline). Severe availability penalty: fails if even a single secondary goes down.", bullet_style))

    story.append(Spacer(1, 6))
    ss1 = os.path.join(IMG_DIR, "screenshot_activity_9_1.png")
    if os.path.exists(ss1):
        story.append(Image(ss1, width=490, height=210))
        story.append(Paragraph("Figure 2.1: Developer Terminal Execution Output of Lab 9.1 Write Concern Latency Benchmark.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: ACTIVITY 9.1 TRY IT YOURSELF - JOURNALING
    # =========================================================================
    story.append(Paragraph("3. Activity 9.1 (Try It Yourself): Journaling Overhead (j:true vs j:false)", h1_style))
    story.append(Paragraph(
        "<b>Research Question:</b> <i>Repeat the experiment with j:true and j:false for each write concern. Does journaling add significant latency?</i><br />"
        "In WiredTiger, <code>j:false</code> acknowledges writes in memory (periodic 100ms disk sync), whereas <code>j:true</code> forces synchronous disk flush of the on-disk journal before acknowledging.",
        body_style
    ))

    story.append(Paragraph("3.1 Comprehensive Journaling Comparison Matrix", h2_style))
    j_table_data = [
        [Paragraph("<b>Write Concern Tier</b>", body_style), Paragraph("<b>j:false Avg (ms)</b>", body_style), Paragraph("<b>j:true Avg (ms)</b>", body_style), Paragraph("<b>Added Delta</b>", body_style), Paragraph("<b>Penalty (%)</b>", body_style), Paragraph("<b>Throughput Impact</b>", body_style)],
        [Paragraph("<b>w:1 (Primary Only)</b>", body_style), Paragraph("0.239 ms", body_style), Paragraph("1.167 ms", body_style), Paragraph("<b>+0.928 ms</b>", body_style), Paragraph("<b>+388.3%</b>", body_style), Paragraph("4,176 -> 856 ops/s", body_style)],
        [Paragraph("<b>w:majority (Quorum 2/3)</b>", body_style), Paragraph("2.024 ms", body_style), Paragraph("2.959 ms", body_style), Paragraph("<b>+0.935 ms</b>", body_style), Paragraph("<b>+46.2%</b>", body_style), Paragraph("494 -> 337 ops/s", body_style)],
        [Paragraph("<b>w:all (All 3 Nodes)</b>", body_style), Paragraph("3.669 ms", body_style), Paragraph("4.560 ms", body_style), Paragraph("<b>+0.891 ms</b>", body_style), Paragraph("<b>+24.3%</b>", body_style), Paragraph("272 -> 219 ops/s", body_style)],
    ]
    j_table = Table(j_table_data, colWidths=[120, 75, 75, 70, 70, 80])
    j_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ffffff')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(j_table)

    story.append(Paragraph("3.2 Technical Findings & Durability Conclusion", h2_style))
    story.append(Paragraph(
        "<b>Answer: Yes, journaling introduces a consistent absolute disk fsync latency of ~0.90 to 0.93 ms.</b><br />"
        "In relative terms, for <code>w:1</code> operations, this causes a significant <b>+388.3% latency penalty</b> because the write switches from pure sub-millisecond DRAM memory access (~0.24ms) to physical storage disk commit (~1.17ms).<br />"
        "However, for <code>w:majority</code> and <code>w:all</code>, network round-trips already consume ~2 to 4ms, so the relative penalty drops to +24% - +46%.<br />"
        "<i>Trade-off:</i> <code>j:true</code> provides full crash durability against power failure, whereas <code>j:false</code> risks up to 100ms of committed writes.",
        body_style
    ))

    story.append(Spacer(1, 6))
    ss2 = os.path.join(IMG_DIR, "screenshot_activity_9_1_try.png")
    if os.path.exists(ss2):
        story.append(Image(ss2, width=490, height=210))
        story.append(Paragraph("Figure 3.1: Developer Terminal Execution Output of Activity 9.1 Journaling Benchmark.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: LAB 9.2 SINGLE NODE NETWORK PARTITION
    # =========================================================================
    story.append(Paragraph("4. Lab 9.2: Simulate a Network Partition (Single Node Isolated)", h1_style))
    story.append(Paragraph(
        "Using <code>docker network disconnect mongo-cluster-net mongo-rs0-2</code>, Secondary-1 was isolated from the 3-node cluster. "
        "Because 2 of 3 voting members (Primary and Secondary-2) remained in mutual communication, majority quorum (66.7% &gt; 50%) "
        "was preserved, allowing the Primary to retain leadership and successfully commit both <code>w:1</code> and <code>w:majority</code> writes.",
        body_style
    ))

    story.append(Paragraph("4.1 Write Concern Behavior During Single Node Partition", h2_style))
    part_table_data = [
        [Paragraph("<b>Operation</b>", body_style), Paragraph("<b>Write Concern</b>", body_style), Paragraph("<b>Outcome</b>", body_style), Paragraph("<b>Observed Latency</b>", body_style), Paragraph("<b>Behavioral Analysis</b>", body_style)],
        [Paragraph("Baseline Write", body_style), Paragraph("<code>w:1</code>", body_style), Paragraph("SUCCESS", body_style), Paragraph("0.31 ms", body_style), Paragraph("Primary in-memory ack.", body_style)],
        [Paragraph("Baseline Write", body_style), Paragraph("<code>w:majority</code>", body_style), Paragraph("SUCCESS", body_style), Paragraph("2.05 ms", body_style), Paragraph("Quorum ack (2/3 nodes).", body_style)],
        [Paragraph("Write Under Partition", body_style), Paragraph("<code>w:1</code>", body_style), Paragraph("SUCCESS", body_style), Paragraph("0.32 ms", body_style), Paragraph("Local primary ack; decoupled from secondary.", body_style)],
        [Paragraph("Write Under Partition", body_style), Paragraph("<code>w:majority</code>", body_style), Paragraph("SUCCESS", body_style), Paragraph("2.11 ms", body_style), Paragraph("Primary + Sec-3 ack quorum (2 &ge; 2).", body_style)],
        [Paragraph("Reconnection & Catch-Up", body_style), Paragraph("<code>rs.status()</code>", body_style), Paragraph("COMPLETE", body_style), Paragraph("0.0 ms lag", body_style), Paragraph("Oplog synced after 30s partition healed.", body_style)],
    ]
    part_table = Table(part_table_data, colWidths=[110, 80, 65, 80, 155])
    part_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (1, 0), (3, -1), 'CENTER'),
    ]))
    story.append(part_table)

    story.append(Spacer(1, 6))
    ss3 = os.path.join(IMG_DIR, "screenshot_activity_9_2.png")
    if os.path.exists(ss3):
        story.append(Image(ss3, width=490, height=210))
        story.append(Paragraph("Figure 4.1: Developer Terminal Execution Output of Lab 9.2 Single Node Network Partition.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: ACTIVITY 9.2 TRY TOTAL QUORUM LOSS & TIMELINE
    # =========================================================================
    story.append(Paragraph("5. Activity 9.2 (Try It Yourself): Total Quorum Collapse & Step-Down", h1_style))
    story.append(Paragraph(
        "When both secondaries (mongo-rs0-2 and mongo-rs0-3) are disconnected, the Primary becomes completely isolated (1/3 votes = 33.3%). "
        "Under the CAP Theorem, MongoDB prioritizes Consistency over Availability (CP): the Primary blocks on <code>w:majority</code> writes (timing out after 3000ms), "
        "detects loss of majority heartbeats, and voluntarily triggers <code>rs.stepDown()</code> to demote itself to SECONDARY.",
        body_style
    ))

    story.append(Paragraph("5.1 Chronological Timeline of Total Partition, Step-Down & Election", h2_style))
    time_table_data = [
        [Paragraph("<b>Time (UTC)</b>", body_style), Paragraph("<b>Phase / Event</b>", body_style), Paragraph("<b>Node 27017</b>", body_style), Paragraph("<b>Node 27018</b>", body_style), Paragraph("<b>Node 27019</b>", body_style), Paragraph("<b>Write State</b>", body_style)],
        [Paragraph("16:51:17.683", body_style), Paragraph("Phase 1: Baseline", body_style), Paragraph("PRIMARY", body_style), Paragraph("SECONDARY", body_style), Paragraph("SECONDARY", body_style), Paragraph("All Writes OK", body_style)],
        [Paragraph("16:51:18.683", body_style), Paragraph("Phase 2: Minor Partition", body_style), Paragraph("PRIMARY", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("SECONDARY", body_style), Paragraph("All Writes OK", body_style)],
        [Paragraph("16:51:19.684", body_style), Paragraph("Phase 3: Major Partition", body_style), Paragraph("PRIMARY (Iso)", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("w:1 Local Only", body_style)],
        [Paragraph("16:51:20.684", body_style), Paragraph("Phase 4: Write Timeout", body_style), Paragraph("PRIMARY (Iso)", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("<b>WTimeout (3s)</b>", body_style)],
        [Paragraph("16:51:21.685", body_style), Paragraph("<b>Phase 5: Step-Down</b>", body_style), Paragraph("<b>SECONDARY (Dem)</b>", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("<b>READ-ONLY LOCK</b>", body_style)],
        [Paragraph("16:51:23.185", body_style), Paragraph("Phase 6: Read-Only Mode", body_style), Paragraph("SECONDARY", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("UNREACHABLE", body_style), Paragraph("Rejected (10107)", body_style)],
        [Paragraph("16:51:24.186", body_style), Paragraph("Phase 7: Network Healed", body_style), Paragraph("SECONDARY", body_style), Paragraph("STARTUP2", body_style), Paragraph("STARTUP2", body_style), Paragraph("Election Lock", body_style)],
        [Paragraph("16:51:25.686", body_style), Paragraph("<b>Phase 8: Election Rejoin</b>", body_style), Paragraph("<b>PRIMARY (Rest)</b>", body_style), Paragraph("SECONDARY", body_style), Paragraph("SECONDARY", body_style), Paragraph("<b>FULLY RESTORED</b>", body_style)],
    ]
    time_table = Table(time_table_data, colWidths=[70, 115, 85, 75, 75, 70])
    time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fee2e2')),
        ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#f0fdf4')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(time_table)

    story.append(Spacer(1, 6))
    ss4 = os.path.join(IMG_DIR, "screenshot_activity_9_2_try.png")
    if os.path.exists(ss4):
        story.append(Image(ss4, width=490, height=210))
        story.append(Paragraph("Figure 5.1: Developer Terminal Execution Output of Total Quorum Loss, Stepdown, and Recovery.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: CAP THEOREM & PACELC TRADE-OFFS
    # =========================================================================
    story.append(Paragraph("6. CAP Theorem & PACELC Trade-Off Analysis in MongoDB", h1_style))
    story.append(Paragraph(
        "MongoDB replica sets operate within the PACELC theorem: If there is a <b>Partition (P)</b>, how does the system trade off "
        "<b>Availability (A)</b> and <b>Consistency (C)</b>? <b>Else (E)</b>, when the system runs normally, how does it trade off "
        "<b>Latency (L)</b> and <b>Consistency (C)</b>?",
        body_style
    ))

    # Embed user's Write-Concern-TradeOffs.jpg
    wc_img = os.path.join(BASE_DIR, "Write-Concern-TradeOffs.jpg")
    if os.path.exists(wc_img):
        story.append(Image(wc_img, width=460, height=200))
        story.append(Paragraph("Figure 6.1: Write Concern Latency vs Durability Trade-Off Continuum (Provided Specification Diagram).", caption_style))

    story.append(Paragraph("6.1 Formal PACELC Classification", h2_style))
    story.append(Paragraph("• <b>PC/EC (w:majority, j:1):</b> Under partition, sacrifices availability (primary steps down) to preserve strict consistency. Under normal conditions, pays network and disk latency (~2.9ms) to guarantee durability.", bullet_style))
    story.append(Paragraph("• <b>PA/EL (w:1, j:0):</b> Leans toward availability under partition (accepting local writes on primary, risking rollback). Under normal conditions, achieves sub-millisecond latency (~0.3ms).", bullet_style))

    # =========================================================================
    # SECTION 7: FULL-STACK WEB PLATFORM INTEGRATION
    # =========================================================================
    story.append(Paragraph("7. CTI Platform Web Dashboard Integration", h1_style))
    story.append(Paragraph(
        "All features from Lab 9 have been integrated into the full-stack Cyber Threat Intelligence (CTI) Platform web app. "
        "A dedicated dashboard (<code>lab9_reports.html</code>) and REST blueprint (<code>routes/lab9.py</code>) provide interactive live controls.",
        body_style
    ))

    ss5 = os.path.join(IMG_DIR, "screenshot_web_integration.png")
    if os.path.exists(ss5):
        story.append(Image(ss5, width=490, height=195))
        story.append(Paragraph("Figure 7.1: Flask Web Server Startup showing lab9 blueprint registration and active HTTP endpoints.", caption_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Successfully built: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")


if __name__ == "__main__":
    build_pdf()
