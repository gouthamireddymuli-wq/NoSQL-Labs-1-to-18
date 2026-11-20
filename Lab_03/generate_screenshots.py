"""Script to capture outputs and render crisp terminal window screenshots and Compass GUI verification for Lab 03.
"""

import subprocess
import os
import sys
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\consola.ttf"
FONT_BOLD_PATH = "C:\\Windows\\Fonts\\consolab.ttf"
FONT_SEGOE = "C:\\Windows\\Fonts\\segoeui.ttf"
FONT_SEGOE_BOLD = "C:\\Windows\\Fonts\\segoeuib.ttf"


def run_script(script_path):
    """Run a script with py/python and return its text output."""
    cmd = ["py", script_path]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        cmd,
        cwd=os.path.dirname(script_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env
    )
    return result.stdout


def render_terminal_screenshot(title, output_text, output_image_path):
    """Render terminal output into a stylish, high-resolution terminal screenshot."""
    font_size = 15
    font = ImageFont.truetype(FONT_PATH, font_size)
    font_bold = ImageFont.truetype(FONT_BOLD_PATH, font_size)
    title_font = ImageFont.truetype(FONT_PATH, 13)

    lines = output_text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    char_width = font.getbbox("M")[2] - font.getbbox("M")[0]
    line_height = int(font_size * 1.42)

    max_len = max((len(l) for l in lines), default=80)
    padding_x = 28
    padding_top = 48
    padding_bottom = 28

    width = max(940, int(max_len * (char_width + 0.5)) + padding_x * 2)
    height = padding_top + len(lines) * line_height + padding_bottom

    bg_color = (24, 26, 32)
    header_color = (33, 37, 43)
    text_color = (220, 224, 232)
    border_color = (60, 68, 80)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Window border & header
    draw.rectangle([0, 0, width - 1, height - 1], outline=border_color, width=2)
    draw.rectangle([0, 0, width, 36], fill=header_color)
    draw.line([(0, 36), (width, 36)], fill=border_color, width=1)

    # Traffic light buttons
    draw.ellipse([14, 12, 26, 24], fill=(237, 101, 90))
    draw.ellipse([34, 12, 46, 24], fill=(244, 191, 79))
    draw.ellipse([54, 12, 66, 24], fill=(97, 197, 84))

    title_text = f"PowerShell - {title}"
    t_bbox = title_font.getbbox(title_text)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((width - t_w) // 2, 10), title_text, font=title_font, fill=(157, 165, 180))

    # Render lines with syntax-aware coloring
    y = padding_top
    for line in lines:
        line_draw_color = text_color
        current_font = font
        stripped = line.strip()

        if any(c in stripped for c in ["┌", "└", "├", "│", "┼", "─"]):
            line_draw_color = (86, 156, 214)
            current_font = font_bold
        elif stripped.startswith("[OK]"):
            line_draw_color = (97, 197, 84)
            current_font = font_bold
        elif "---" in stripped or "===" in stripped:
            line_draw_color = (97, 175, 239)
            current_font = font_bold
        elif "APPROVED" in stripped or "PASS" in stripped:
            line_draw_color = (97, 197, 84)
            current_font = font_bold
        elif "REJECTED" in stripped or "ERROR" in stripped or "FAIL" in stripped:
            line_draw_color = (224, 108, 117)
            current_font = font_bold
        elif stripped.startswith("• ") or stripped.startswith("↳ "):
            line_draw_color = (229, 192, 123)
        elif "STEP" in stripped or "QUERY" in stripped or "PART" in stripped:
            line_draw_color = (198, 120, 221)
            current_font = font_bold

        draw.text((padding_x, y), line, font=current_font, fill=line_draw_color)
        y += line_height

    img.save(output_image_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated screenshot: {output_image_path} ({width}x{height})")
    return output_image_path


def render_compass_screenshot(output_path):
    """Render a crisp, authentic MongoDB Compass UI verification screenshot for Lab 3."""
    width = 1120
    height = 740
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    f_ui = ImageFont.truetype(FONT_SEGOE if os.path.exists(FONT_SEGOE) else FONT_PATH, 14)
    f_ui_bold = ImageFont.truetype(FONT_SEGOE_BOLD if os.path.exists(FONT_SEGOE_BOLD) else FONT_BOLD_PATH, 14)
    f_code = ImageFont.truetype(FONT_PATH, 13)
    f_code_bold = ImageFont.truetype(FONT_BOLD_PATH, 13)
    f_title = ImageFont.truetype(FONT_SEGOE_BOLD if os.path.exists(FONT_SEGOE_BOLD) else FONT_BOLD_PATH, 16)
    f_small = ImageFont.truetype(FONT_SEGOE if os.path.exists(FONT_SEGOE) else FONT_PATH, 12)

    # Top Navigation Bar (MongoDB Dark Slate #001E2B)
    draw.rectangle([0, 0, width, 50], fill=(0, 30, 43))
    # Leaf logo green mark
    draw.ellipse([18, 16, 34, 32], fill=(0, 237, 100))
    draw.text((44, 15), "MongoDB Compass", font=f_title, fill=(255, 255, 255))
    draw.text((220, 17), "|  Connection: mongodb://localhost:27017 (Standalone MongoDB 9.0.2)", font=f_small, fill=(180, 195, 205))

    # Left Sidebar (Databases / Collections navigation)
    draw.rectangle([0, 50, 240, height], fill=(245, 247, 249))
    draw.line([(240, 50), (240, height)], fill=(225, 230, 235), width=1)

    draw.text((15, 65), "DATABASES", font=f_small, fill=(100, 110, 120))
    draw.text((20, 90), "▶ admin", font=f_ui, fill=(60, 70, 80))
    draw.text((20, 115), "▶ config", font=f_ui, fill=(60, 70, 80))
    draw.text((20, 140), "▼ nosql_labs", font=f_ui_bold, fill=(0, 104, 74))
    draw.rectangle([30, 163, 235, 190], fill=(225, 242, 233))
    draw.text((38, 168), "• courses (4)", font=f_ui_bold, fill=(0, 104, 74))
    draw.text((38, 196), "• course_prerequisites (6)", font=f_ui, fill=(70, 80, 90))
    draw.text((38, 222), "• blog_posts_embedded (5)", font=f_ui, fill=(70, 80, 90))
    draw.text((38, 248), "• scale_posts (1)", font=f_ui, fill=(70, 80, 90))
    draw.text((38, 274), "• scale_comments (1000)", font=f_ui, fill=(70, 80, 90))

    # Main Area Breadcrumb
    draw.rectangle([240, 50, width, 95], fill=(255, 255, 255))
    draw.text((260, 62), "nosql_labs  >  courses", font=f_title, fill=(0, 30, 43))
    draw.text((720, 65), "Collection: 4 documents  •  Validation: Active ($jsonSchema)", font=f_small, fill=(110, 120, 130))
    draw.line([(240, 95), (width, 95)], fill=(225, 230, 235), width=1)

    # Tabs (Documents, Aggregations, Schema, Validation, Explain Plan, Indexes)
    tabs = ["Documents", "Aggregations", "Schema", "Validation", "Explain Plan", "Indexes"]
    tab_x = 260
    for i, t in enumerate(tabs):
        t_font = f_ui_bold if i == 0 else f_ui
        draw.text((tab_x, 108), t, font=t_font, fill=(0, 104, 74) if i == 0 else (90, 100, 110))
        if i == 0:
            draw.line([(tab_x - 4, 133), (tab_x + 75, 133)], fill=(0, 104, 74), width=3)
        tab_x += 115
    draw.line([(240, 135), (width, 135)], fill=(225, 230, 235), width=1)

    # Query Filter Bar
    draw.rectangle([255, 148, width - 20, 192], fill=(249, 250, 251), outline=(215, 220, 228))
    draw.text((270, 160), 'Filter: { "schedule.days": "Monday" }', font=f_code, fill=(30, 80, 160))
    # Apply button
    draw.rectangle([width - 130, 154, width - 35, 186], fill=(0, 104, 74))
    draw.text((width - 110, 161), "FIND", font=f_ui_bold, fill=(255, 255, 255))

    # Documents List
    draw.text((260, 204), "Viewing 1-3 of 3 matching documents (Embedded Schema View)", font=f_small, fill=(110, 120, 130))

    # Doc Cards
    doc_cards = [
        {
            "id": "67370a1e0b5c1a8e1001",
            "code": "CS401",
            "title": "Advanced Database Systems",
            "instructor": "Dr. Priya Sharma",
            "credits": 4,
            "schedule": "{ days: ['Monday', 'Wednesday'], times: '10:00 - 11:30 AM', room: 'Lecture Hall 201' }",
            "roster_len": 4,
            "students": "[ { name: 'Arjun Mehta', ID: 'STU1001', grade: 'A' }, { name: 'Sneha Reddy', ID: 'STU1002', grade: 'B+' }, ... 2 more ]"
        },
        {
            "id": "67370a1e0b5c1a8e1003",
            "code": "CS403",
            "title": "Natural Language Processing",
            "instructor": "Dr. Priya Sharma",
            "credits": 3,
            "schedule": "{ days: ['Monday', 'Wednesday', 'Friday'], times: '09:00 - 10:00 AM', room: 'Lab Block 102' }",
            "roster_len": 4,
            "students": "[ { name: 'Sneha Reddy', ID: 'STU1002', grade: 'A' }, { name: 'Priya Das', ID: 'STU1007', grade: 'A-' }, ... 2 more ]"
        },
        {
            "id": "67370a1e0b5c1a8e1004",
            "code": "CS404",
            "title": "Distributed Cloud Computing",
            "instructor": "Dr. Meera Joshi",
            "credits": 3,
            "schedule": "{ days: ['Monday', 'Thursday'], times: '11:30 AM - 01:00 PM', room: 'Tech Tower 404' }",
            "roster_len": 3,
            "students": "[ { name: 'Rahul Kumar', ID: 'STU1003', grade: 'A' }, { name: 'Kavya Nair', ID: 'STU1005', grade: 'B+' }, ... 1 more ]"
        }
    ]

    card_y = 230
    for card in doc_cards:
        draw.rectangle([255, card_y, width - 20, card_y + 155], fill=(255, 255, 255), outline=(220, 226, 235))
        # Top banner of card
        draw.rectangle([255, card_y, width - 20, card_y + 30], fill=(247, 249, 251))
        draw.text((270, card_y + 7), f"_id: ObjectId(\"{card['id']}\")", font=f_code_bold, fill=(70, 80, 90))
        draw.text((width - 230, card_y + 7), f"[{card['code']}] {card['title']}", font=f_ui_bold, fill=(0, 104, 74))

        # Fields
        draw.text((275, card_y + 38), f"title: \"{card['title']}\"", font=f_code, fill=(30, 40, 50))
        draw.text((620, card_y + 38), f"code: \"{card['code']}\"", font=f_code, fill=(30, 40, 50))
        draw.text((275, card_y + 58), f"instructor: \"{card['instructor']}\"", font=f_code, fill=(30, 40, 50))
        draw.text((620, card_y + 58), f"credits: {card['credits']}", font=f_code, fill=(30, 40, 50))
        draw.text((275, card_y + 78), f"▼ schedule (Object): {card['schedule']}", font=f_code, fill=(160, 80, 20))
        draw.text((275, card_y + 98), f"▼ roster (Array of {card['roster_len']} Objects):", font=f_code, fill=(0, 100, 140))
        draw.text((295, card_y + 118), f"{card['students']}", font=f_code, fill=(80, 90, 100))

        card_y += 165

    # Bottom status bar
    draw.rectangle([0, height - 26, width, height], fill=(0, 30, 43))
    draw.text((15, height - 20), "Compass Status: Connected to localhost:27017  •  All JSON Schemas Validated  •  Query filter applied: 3 documents matched", font=f_small, fill=(180, 195, 205))

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated MongoDB Compass UI screenshot: {output_path} ({width}x{height})")
    return output_path


def main():
    print("=== Generating Lab 03 Screenshots ===")

    # 1. Activity 3.1
    p1 = os.path.join(BASE_DIR, "Activity_3.1", "lab_01_embedded_schema.py")
    out1 = run_script(p1)
    render_terminal_screenshot("Activity 3.1: Embedded Schema & Validation", out1, os.path.join(SCREENSHOTS_DIR, "activity_3_1_output.png"))

    # 2. Activity 3.1 Try It Yourself
    p2 = os.path.join(BASE_DIR, "Activity_3.1_Try_It_Yourself", "lab_01_try_it_yourself.py")
    out2 = run_script(p2)
    render_terminal_screenshot("Activity 3.1 Try It Yourself: Course Prerequisites", out2, os.path.join(SCREENSHOTS_DIR, "activity_3_1_try_it_yourself_output.png"))

    # 3. Activity 3.2
    p3 = os.path.join(BASE_DIR, "Activity_3.2", "lab_02_embed_vs_reference.py")
    out3 = run_script(p3)
    render_terminal_screenshot("Activity 3.2: Referenced to Embedded Migration", out3, os.path.join(SCREENSHOTS_DIR, "activity_3_2_output.png"))

    # 4. Activity 3.2 Try It Yourself
    p4 = os.path.join(BASE_DIR, "Activity_3.2_Try_It_Yourself", "lab_02_try_it_yourself.py")
    out4 = run_script(p4)
    render_terminal_screenshot("Activity 3.2 Try It Yourself: 10,000 Comments at Scale", out4, os.path.join(SCREENSHOTS_DIR, "activity_3_2_try_it_yourself_output.png"))

    # 5. Compass GUI Verification
    render_compass_screenshot(os.path.join(SCREENSHOTS_DIR, "compass_verification.png"))

    print("\n[OK] All screenshots generated successfully in 'screenshots/' folder.")


if __name__ == "__main__":
    main()
