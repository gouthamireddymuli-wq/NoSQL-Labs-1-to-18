"""
Package NoSQL_Lab_9_Submission.zip with all activities, reports, Docker configurations,
and web assets.
"""

import os
import zipfile

BASE_DIR = r"c:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9"
ZIP_PATH = os.path.join(BASE_DIR, "NoSQL_Lab_9_Submission.zip")

dirs_to_zip = [
    "Activity_9_1",
    "Activity_9_1_TryItYourself",
    "Activity_9_2",
    "Activity_9_2_TryItYourself",
    "screenshots",
    "web_platform"
]

files_to_zip = [
    "Lab9_Report.pdf",
    "Lab9_Report.docx",
    "Dockerfile",
    "docker-compose.yml",
    "Write-Concern-TradeOffs.jpg",
    "lab_01_write_concern_latency.py",
    "lab_02_simulate_partition.sh"
]

print("Packaging NoSQL_Lab_9_Submission.zip...")
with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
    for d in dirs_to_zip:
        dir_full = os.path.join(BASE_DIR, d)
        if os.path.exists(dir_full):
            for root, _, files in os.walk(dir_full):
                if "__pycache__" in root or ".git" in root:
                    continue
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, BASE_DIR)
                    zf.write(full_p, rel_p)

    for f in files_to_zip:
        full_p = os.path.join(BASE_DIR, f)
        if os.path.exists(full_p):
            zf.write(full_p, f)

size = os.path.getsize(ZIP_PATH)
print(f"[OK] Successfully packaged: {ZIP_PATH} ({size:,} bytes / {size / (1024*1024):.2f} MB)")
