#!/usr/bin/env python3
"""NoSQL Lab 18 – Comparative Capstone Runner.
Author: M Gouthami (24BTRCL130)

Usage:
    python run_all.py          # run all labs (Lab 18.1 & Lab 18.2)
    python run_all.py lab1     # run only Lab 18.1 (Comparative Capstone Lab)
    python run_all.py lab2     # run only Lab 18.2 (Comparative Analysis Report)
    python run_all.py web      # start the interactive web application
"""
import sys
import importlib.util
import os

base = os.path.dirname(os.path.abspath(__file__))
if base not in sys.path:
    sys.path.insert(0, base)


def run_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "main"):
        mod.main()


labs = {
    "lab1": os.path.join(base, "lab_01_comparative_capstone.py"),
    "lab2": os.path.join(base, "lab_02_comparative_report.py"),
}

arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

if arg == "all":
    for lab_name, path in labs.items():
        print(f"\n{'='*70}")
        print(f"  Running {lab_name}: {os.path.basename(path)}")
        print(f"{'='*70}")
        run_module(path, lab_name)
elif arg in labs:
    run_module(labs[arg], arg)
elif arg == "web":
    from web.app import app
    port = int(os.getenv("PORT", 5000))
    print(f"\nStarting NoSQL Lab 18 Web UI on http://localhost:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
else:
    print(f"Unknown arg '{arg}'. Use: all | lab1 | lab2 | web")
    sys.exit(1)
