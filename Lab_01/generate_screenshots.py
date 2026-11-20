"""Script to capture outputs and render crisp terminal window screenshots.
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


def run_script(script_path):
    """Run a script and return its text output."""
    cmd = [sys.executable, script_path]
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
    # Clean up empty lines at start/end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    # Calculate dimensions
    char_width = font.getbbox("M")[2] - font.getbbox("M")[0]
    line_height = int(font_size * 1.42)

    max_len = max((len(l) for l in lines), default=80)
    padding_x = 28
    padding_top = 48
    padding_bottom = 28

    width = max(900, int(max_len * (char_width + 0.5)) + padding_x * 2)
    height = padding_top + len(lines) * line_height + padding_bottom

    # Canvas colors (modern dark terminal theme)
    bg_color = (24, 26, 32)
    header_color = (33, 37, 43)
    text_color = (220, 224, 232)
    border_color = (60, 68, 80)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw border
    draw.rectangle([0, 0, width - 1, height - 1], outline=border_color, width=2)

    # Draw header title bar
    draw.rectangle([0, 0, width, 36], fill=header_color)
    draw.line([(0, 36), (width, 36)], fill=border_color, width=1)

    # Draw window buttons (red, yellow, green dots)
    draw.ellipse([14, 12, 26, 24], fill=(237, 101, 90))
    draw.ellipse([34, 12, 46, 24], fill=(244, 191, 79))
    draw.ellipse([54, 12, 66, 24], fill=(97, 197, 84))

    # Draw terminal title in header
    title_text = f"PowerShell - {title}"
    t_bbox = title_font.getbbox(title_text)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((width - t_w) // 2, 10), title_text, font=title_font, fill=(157, 165, 180))

    # Render lines with contextual syntax highlighting
    y = padding_top
    for line in lines:
        line_draw_color = text_color
        current_font = font

        # Context color rules
        stripped = line.strip()
        if stripped.startswith("+--") or stripped.startswith("|--"):
            line_draw_color = (86, 156, 214) # cyan border
        elif stripped.startswith("[OK]"):
            line_draw_color = (97, 197, 84) # green success
            current_font = font_bold
        elif "---" in stripped and "---" in stripped:
            line_draw_color = (229, 192, 123) # gold header
            current_font = font_bold
        elif stripped.startswith("===") or stripped.startswith(">>>"):
            line_draw_color = (97, 175, 239) # bright blue
            current_font = font_bold
        elif "Expected answers:" in stripped or "Alignment Status" in stripped:
            line_draw_color = (198, 120, 221) # magenta
            current_font = font_bold
        elif stripped.startswith("* ") or stripped.startswith("- "):
            line_draw_color = (171, 178, 191)

        draw.text((padding_x, y), line, font=current_font, fill=line_draw_color)
        y += line_height

    img.save(output_image_path, "PNG", dpi=(300, 300))
    print(f"[OK] Generated screenshot: {output_image_path} ({width}x{height})")
    return output_image_path


def main():
    scripts = [
        ("Activity 1.1: Classify Database Products",
         os.path.join(BASE_DIR, "Activity_1.1", "lab_01_classify_databases.py"),
         os.path.join(SCREENSHOTS_DIR, "activity_1_1_output.png")),

        ("Activity 1.1 Try It Yourself: Advanced Database Classification",
         os.path.join(BASE_DIR, "Activity_1.1_Try_It_Yourself", "lab_01_try_it_yourself.py"),
         os.path.join(SCREENSHOTS_DIR, "activity_1_1_try_it_yourself_output.png")),

        ("Activity 1.2: Map Application Data Domains to NoSQL Families",
         os.path.join(BASE_DIR, "Activity_1.2", "lab_02_map_application.py"),
         os.path.join(SCREENSHOTS_DIR, "activity_1_2_output.png")),

        ("Activity 1.2 Try It Yourself: Architectural Mapping & Self-Evaluation",
         os.path.join(BASE_DIR, "Activity_1.2_Try_It_Yourself", "lab_02_try_it_yourself.py"),
         os.path.join(SCREENSHOTS_DIR, "activity_1_2_try_it_yourself_output.png")),
    ]

    for title, script_path, img_path in scripts:
        print(f"Executing and capturing: {title}...")
        output = run_script(script_path)
        render_terminal_screenshot(title, output, img_path)

    print("\nAll screenshots generated successfully!")


if __name__ == "__main__":
    main()
