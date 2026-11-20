import os
import subprocess
import time
import sys

GH_PATH = r"C:\Users\gouth\AppData\Local\Programs\DockerDesktop\resources\bin;C:\Program Files\GitHub CLI;C:\Users\gouth\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe"
os.environ["PATH"] = GH_PATH + ";" + os.environ["PATH"]

REMAINING_LABS = [
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

def attempt_push():
    owner = "gouthamireddymuli-wq"
    pending = list(REMAINING_LABS)
    
    print(f"Starting auto-push daemon for {len(pending)} remaining labs...")
    
    while pending:
        lab = pending[0]
        repo = lab["repo"]
        path = lab["path"]
        desc = lab["desc"]
        num = lab["num"]

        print(f"\n[Attempting Lab {num}: {repo}]")
        c, o, e = run(f'gh repo create {owner}/{repo} --public --description "{desc}"')
        
        if c == 0 or "already exists" in (e + o):
            print(f"  Success or exists! Repo ready: https://github.com/{owner}/{repo}")
            # Set remote and push
            target_remote = f"https://github.com/{owner}/{repo}.git"
            run(f"git remote set-url origin {target_remote}", cwd=path)
            c_push, o_push, e_push = run("git push -u origin main --force", cwd=path)
            if c_push == 0:
                print(f"  Pushed main branch to {target_remote}!")
                pending.pop(0)
            else:
                print(f"  Push failed: {e_push}. Will retry.")
        else:
            if "too many repositories" in (e + o) or "rate limit" in (e + o):
                print(f"  GitHub rate-limit still active. Sleeping 60s before retry...")
                time.sleep(60)
            else:
                print(f"  Error: {e or o}. Sleeping 30s...")
                time.sleep(30)

    print("\nALL REMAINING LABS PUSHED AS STANDALONE REPOSITORIES SUCCESSFULLY!")

if __name__ == "__main__":
    attempt_push()
