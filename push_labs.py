import os
import subprocess
import sys

GH_PATH = r"C:\Users\gouth\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Program Files\GitHub CLI;C:\Users\gouth\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe"
os.environ["PATH"] = GH_PATH + ";" + os.environ["PATH"]

LABS = [
    {"num": 1, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_1", "repo": "NoSQL_Lab_1", "desc": "NoSQL Lab 1: Classify Databases and Application Mapping"},
    {"num": 2, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_2", "repo": "NoSQL_Lab_2", "desc": "NoSQL Lab 2: Document Model Design & Embedding vs Referencing"},
    {"num": 3, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_3", "repo": "NoSQL_Lab_3", "desc": "NoSQL Lab 3: MongoDB CRUD Operations & Bulk Writes"},
    {"num": 4, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_4", "repo": "NoSQL_Lab_4", "desc": "NoSQL Lab 4: Advanced MongoDB CRUD & Schema Validation"},
    {"num": 5, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_5", "repo": "NoSQL_Lab_5", "desc": "NoSQL Lab 5: MongoDB Aggregation Pipeline Framework"},
    {"num": 6, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_6", "repo": "NoSQL_Lab_6", "desc": "NoSQL Lab 6: Indexing Strategies & Query Optimization"},
    {"num": 7, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_7", "repo": "NoSQL_Lab_7", "desc": "NoSQL Lab 7: Cyber Threat Intelligence Platform with Working Set Analysis"},
    {"num": 8, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_8", "repo": "NoSQL_Lab_8", "desc": "NoSQL Lab 8: Geospatial Queries & GeoJSON Indexing in MongoDB"},
    {"num": 9, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9", "repo": "NoSQL_Lab_9", "desc": "NoSQL Lab 9: Time Series Collections & IoT Sensor Ingestion"},
    {"num": 10, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab10", "repo": "NoSQL_Lab_10", "desc": "NoSQL Lab 10: Multi-Document ACID Transactions in MongoDB"},
    {"num": 11, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL lab11", "repo": "NoSQL_Lab_11", "desc": "NoSQL Lab 11: Sharding & Horizontal Partitioning in MongoDB"},
    {"num": 12, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab12", "repo": "NoSQL_Lab_12", "desc": "NoSQL Lab 12: Replica Sets & High Availability Failover"},
    {"num": 13, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab13", "repo": "NoSQL_Lab_13", "desc": "NoSQL Lab 13: MongoDB Security, Role-Based Access Control & Auditing"},
    {"num": 14, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab 14", "repo": "NoSQL_Lab_14", "desc": "NoSQL Lab 14: Disaster Recovery, Backup & Restore Strategies"},
    {"num": 15, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab15", "repo": "NoSQL_Lab_15", "desc": "NoSQL Lab 15: Change Streams & Real-Time Event-Driven Architecture"},
    {"num": 16, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab16", "repo": "NoSQL_Lab_16", "desc": "NoSQL Lab 16: Polyglot Persistence - MongoDB, Cassandra & Neo4j Integration"},
    {"num": 17, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab17", "repo": "NoSQL_Lab_17", "desc": "NoSQL Lab 17: RAG Pipeline & HNSW vs IVF Vector Index Benchmarking"},
    {"num": 18, "path": r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab18", "repo": "NoSQL_Lab_18", "desc": "NoSQL Lab 18: Comparative Capstone - Fraud Detection Data Platform"},
]

def run(cmd, cwd=None):
    res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def push_lab(lab):
    path = lab["path"]
    repo = lab["repo"]
    desc = lab["desc"]
    print(f"\n==========================================")
    print(f"Processing Lab {lab['num']}: {repo}")
    print(f"Path: {path}")

    if not os.path.exists(path):
        print(f"Error: Path {path} does not exist!")
        return None

    # Write a clean .gitignore if none exists or ensure standard ignore
    gitignore_path = os.path.join(path, ".gitignore")
    ignore_content = "\n__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.env\nvenv/\n.venv/\nnode_modules/\n"
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write(ignore_content)
    else:
        with open(gitignore_path, "a") as f:
            f.write(ignore_content)

    # Check git init
    git_dir = os.path.join(path, ".git")
    if not os.path.exists(git_dir):
        run("git init -b main", cwd=path)
        run("git config user.name \"GOUTHAMI REDDY\"", cwd=path)
        run("git config user.email \"gouthamireddymuli@gmail.com\"", cwd=path)
    
    # Check if branch is main
    run("git branch -M main", cwd=path)

    # Add and commit
    run("git add .", cwd=path)
    num = lab["num"]
    code, out, err = run(f'git commit -m "NoSQL Lab {num}: {desc}"', cwd=path)
    if "nothing to commit" in out or "nothing to commit" in err:
        print("  Working tree clean / already committed.")
    else:
        print("  Committed changes.")

    # Check remote
    code, remotes, _ = run("git remote -v", cwd=path)
    owner = "gouthamireddymuli-wq"
    expected_remote = f"https://github.com/{owner}/{repo}.git"

    if "origin" not in remotes:
        # Create repo using gh
        print(f"  Creating GitHub repo {owner}/{repo}...")
        c, o, e = run(f'gh repo create {owner}/{repo} --public --description "{desc}" --source="{path}" --remote=origin --push', cwd=path)
        if c == 0:
            print(f"  Repo created and pushed: https://github.com/{owner}/{repo}")
            return f"https://github.com/{owner}/{repo}"
        else:
            # If repo already exists on remote, set origin and push
            print(f"  gh repo create returned: {e or o}. Setting origin manually...")
            run(f"git remote add origin {expected_remote}", cwd=path)
    
    # Push to origin main
    print(f"  Pushing to {expected_remote}...")
    c, o, e = run("git push -u origin main", cwd=path)
    if c == 0:
        print(f"  Successfully pushed: https://github.com/{owner}/{repo}")
        return f"https://github.com/{owner}/{repo}"
    else:
        # Retry with force if needed or pull
        print(f"  Push output: {o} {e}")
        run("git push -u origin main --force", cwd=path)
        return f"https://github.com/{owner}/{repo}"

if __name__ == "__main__":
    results = {}
    for lab in LABS:
        url = push_lab(lab)
        results[lab["num"]] = {"repo": lab["repo"], "url": url, "desc": lab["desc"]}

    print("\n\n==========================================")
    print("ALL LABS PUSHED SUMMARY:")
    for num, data in results.items():
        print(f"Lab {num:02d}: {data['url']}")
