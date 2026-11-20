#!/usr/bin/env python3
"""NoSQL Lab 17 – Run all activities.
Author: M Gouthami (24BTRCL130)

Usage:
    python run_all.py          # run all labs
    python run_all.py lab1     # run only Lab 17.1 (Simple RAG Pipeline)
    python run_all.py lab2     # run only Lab 17.2 (HNSW vs IVF Vector Indexes)
"""
import sys
import importlib.util
import os


def run_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "main"):
        mod.main()


base = os.path.dirname(os.path.abspath(__file__))

labs = {
    "lab1": os.path.join(base, "lab_01_rag_pipeline.py"),
    "lab2": os.path.join(base, "lab_02_hnsw_vs_ivf.py"),
}

arg = sys.argv[1] if len(sys.argv) > 1 else "all"

if arg == "all":
    for lab_name, path in labs.items():
        print(f"\n{'='*70}")
        print(f"  Running {lab_name}: {os.path.basename(path)}")
        print(f"{'='*70}")
        run_module(path, lab_name)
elif arg in labs:
    run_module(labs[arg], arg)
else:
    print(f"Unknown arg '{arg}'. Use: all | lab1 | lab2")
    sys.exit(1)
