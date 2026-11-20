"""Package the Lab 03 submission into clean .ZIP archives matching the required format.
"""

import os
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP_DIR = os.path.dirname(BASE_DIR)

ZIP_NAMES = [
    "NoSQL_Lab_03_M_Gouthami_24BTRCL130.zip",
    "NoSQL_Lab_3_Submission.zip"
]

folders_to_include = [
    "Activity_3.1",
    "Activity_3.1_Try_It_Yourself",
    "Activity_3.2",
    "Activity_3.2_Try_It_Yourself",
    "config",
    "screenshots"
]

files_to_include = [
    "NoSQL_Lab_03_Report.docx"
]

for zip_name in ZIP_NAMES:
    zip_path = os.path.join(BASE_DIR, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add activity folders and supporting assets
        for folder in folders_to_include:
            folder_full = os.path.join(BASE_DIR, folder)
            if os.path.exists(folder_full):
                for root, dirs, files in os.walk(folder_full):
                    # Skip __pycache__
                    if "__pycache__" in root:
                        continue
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, BASE_DIR)
                        zf.write(full_path, rel_path)

        # Add DOCX report
        for f in files_to_include:
            f_full = os.path.join(BASE_DIR, f)
            if os.path.exists(f_full):
                zf.write(f_full, f)

    print(f"[OK] Created {zip_path} ({os.path.getsize(zip_path):,} bytes)")

    # Copy to Desktop for easy access
    desktop_dest = os.path.join(DESKTOP_DIR, zip_name)
    shutil.copy2(zip_path, desktop_dest)
    print(f"[OK] Copied to Desktop: {desktop_dest}")

# Also copy DOCX report to Desktop
docx_name = "NoSQL_Lab_03_Report.docx"
docx_src = os.path.join(BASE_DIR, docx_name)
docx_desktop = os.path.join(DESKTOP_DIR, docx_name)
if os.path.exists(docx_src):
    shutil.copy2(docx_src, docx_desktop)
    print(f"[OK] Copied DOCX report to Desktop: {docx_desktop}")

print("\nVerification of ZIP contents:")
with zipfile.ZipFile(os.path.join(BASE_DIR, ZIP_NAMES[0]), "r") as zf:
    for info in zf.infolist():
        print(f"  {info.filename:60} ({info.file_size:,} bytes)")
