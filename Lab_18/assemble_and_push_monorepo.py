import os
import shutil
import subprocess

TARGET_DIR = r"C:\Users\gouth\OneDrive\Desktop\NoSQL_All_Labs_Master"
REPO_URL = "https://github.com/gouthamireddymuli-wq/NoSQL-Labs-1-to-18.git"

LAB_DIRS = [
    (1, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_1", "Lab 01: Classify Databases and Application Mapping"),
    (2, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_2", "Lab 02: Document Model Design & Embedding vs Referencing"),
    (3, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_3", "Lab 03: MongoDB CRUD Operations & Bulk Writes"),
    (4, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_4", "Lab 04: Advanced MongoDB CRUD & Schema Validation"),
    (5, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_5", "Lab 05: MongoDB Aggregation Pipeline Framework"),
    (6, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_6", "Lab 06: Indexing Strategies & Query Optimization"),
    (7, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_7", "Lab 07: Cyber Threat Intelligence Platform & Working Set Analysis"),
    (8, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_8", "Lab 08: Geospatial Queries & GeoJSON Indexing in MongoDB"),
    (9, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab_9", "Lab 09: Time Series Collections & IoT Sensor Ingestion"),
    (10, r"C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab10", "Lab 10: Multi-Document ACID Transactions in MongoDB"),
    (11, r"C:\Users\gouth\OneDrive\Desktop\NoSQL lab11", "Lab 11: Sharding & Horizontal Partitioning in MongoDB"),
    (12, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab12", "Lab 12: Replica Sets & High Availability Failover"),
    (13, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab13", "Lab 13: MongoDB Security, RBAC & Auditing"),
    (14, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab 14", "Lab 14: Disaster Recovery, Backup & Restore Strategies"),
    (15, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab15", "Lab 15: Change Streams & Real-Time Event-Driven Architecture"),
    (16, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab16", "Lab 16: Polyglot Persistence - MongoDB, Cassandra & Neo4j Integration"),
    (17, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab17", "Lab 17: RAG Pipeline & HNSW vs IVF Vector Index Benchmarking"),
    (18, r"C:\Users\gouth\OneDrive\Desktop\NoSQL Lab18", "Lab 18: Comparative Capstone - Fraud Detection Data Platform"),
]

def ignore_patterns(path, names):
    ignored = set()
    for name in names:
        if name in {".git", "__pycache__", ".vscode", ".idea", "node_modules", "venv", ".venv"}:
            ignored.add(name)
        elif name.endswith((".pyc", ".pyo")):
            ignored.add(name)
    return ignored

def assemble():
    if os.path.exists(TARGET_DIR):
        # Keep .git if already initialized
        for item in os.listdir(TARGET_DIR):
            if item != ".git":
                item_path = os.path.join(TARGET_DIR, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                else:
                    os.remove(item_path)
    else:
        os.makedirs(TARGET_DIR, exist_ok=True)

    print("Copying all 18 labs into master directory...")
    for num, src_path, title in LAB_DIRS:
        dest_folder = os.path.join(TARGET_DIR, f"Lab_{num:02d}")
        print(f"  Copying Lab {num:02d} from {src_path}...")
        if os.path.exists(src_path):
            shutil.copytree(src_path, dest_folder, ignore=ignore_patterns, dirs_exist_ok=True)

    # Generate master README.md
    readme_content = """# NoSQL Database Systems — Complete Laboratory Portfolio (Labs 1–18)

**Student Name:** M Gouthami  
**Register No / USN:** 24BTRCL130  
**Course:** NoSQL Database Systems  
**Academic Year:** 2026–2027  
**Docker Hub Organization:** [gouthudocker](https://hub.docker.com/u/gouthudocker)  
**GitHub Repository:** [NoSQL-Labs-1-to-18](https://github.com/gouthamireddymuli-wq/NoSQL-Labs-1-to-18)

---

## 📚 Complete Laboratory Index (All 18 Labs)

Click any lab link below to browse its complete source code, reports, benchmarks, and Docker configurations directly:

| Lab # | Topic / Domain | Direct Folder Link | Key Technologies & Highlights |
| :---: | :--- | :--- | :--- |
| **Lab 01** | Database Classification & App Mapping | [📁 Lab_01](./Lab_01) | ACID vs BASE, CAP theorem, Document vs Key-Value vs Columnar vs Graph |
| **Lab 02** | Document Model Design | [📁 Lab_02](./Lab_02) | Embedding vs Referencing, 1:1, 1:N, N:M data relationships |
| **Lab 03** | MongoDB CRUD & Bulk Writes | [📁 Lab_03](./Lab_03) | Ordered vs Unordered bulk writes, projection, write concern |
| **Lab 04** | Advanced CRUD & Schema Validation | [📁 Lab_04](./Lab_04) | JSON Schema validation, `$jsonSchema`, update operators |
| **Lab 05** | Aggregation Pipeline Framework | [📁 Lab_05](./Lab_05) | `$match`, `$group`, `$project`, `$unwind`, `$lookup`, `$facet` |
| **Lab 06** | Indexing & Query Optimization | [📁 Lab_06](./Lab_06) | Compound indexes, ESR rule, covered queries, explain plans |
| **Lab 07** | Cyber Threat Intelligence & Working Set | [📁 Lab_07](./Lab_07) | RAM working set sizing, WiredTiger cache, eviction dynamics |
| **Lab 08** | Geospatial Queries & GeoJSON Indexing | [📁 Lab_08](./Lab_08) | `2dsphere` indexes, `$near`, `$geoWithin`, spatial proximity |
| **Lab 09** | Time Series Collections & IoT Ingestion | [📁 Lab_09](./Lab_09) | Time-series bucketing, metaField, granularity, rollups |
| **Lab 10** | Multi-Document ACID Transactions | [📁 Lab_10](./Lab_10) | Two-phase commit, session transactions, rollback on abort |
| **Lab 11** | Sharding & Horizontal Partitioning | [📁 Lab_11](./Lab_11) | Shard keys, chunks, mongos routing, jumbo chunk prevention |
| **Lab 12** | Replica Sets & High Availability | [📁 Lab_12](./Lab_12) | Primary-Secondary replication, heartbeat elections, automatic failover |
| **Lab 13** | MongoDB Security, RBAC & Auditing | [📁 Lab_13](./Lab_13) | SCRAM authentication, custom roles, TLS/SSL, audit logs |
| **Lab 14** | Disaster Recovery, Backup & Restore | [📁 Lab_14](./Lab_14) | `mongodump`, `mongorestore`, point-in-time recovery, oplog replay |
| **Lab 15** | Change Streams & Event-Driven Architecture | [📁 Lab_15](./Lab_15) | Real-time notifications, resume tokens, reactive pipelines |
| **Lab 16** | Polyglot Persistence Architecture | [📁 Lab_16](./Lab_16) | MongoDB + Cassandra + Neo4j integration and hybrid routing |
| **Lab 17** | RAG Pipeline & HNSW vs IVF Vector Search | [📁 Lab_17](./Lab_17) | RAG chunking, mock embeddings, IVF vs NSW graph ANN search |
| **Lab 18** | Comparative Capstone — Fraud Detection | [📁 Lab_18](./Lab_18) | 10k transactions benchmark, polyglot matrix, Flask Web GUI |

---

## 🐳 Docker Hub Demonstrations

The laboratory suite includes production Docker containers for interactive grading and demonstration:

* **Lab 18 Capstone Container:** `docker pull gouthudocker/nosql-lab18:latest`
  * Web Dashboard: `docker run -d --name nosql_lab18 -p 5006:5000 gouthudocker/nosql-lab18:latest` (Access at `http://localhost:5006`)
* **Lab 17 RAG & Vector Index Container:** `docker pull gouthudocker/nosql-lab17:latest`
* **Lab 15 Change Streams Container:** `docker pull gouthudocker/nosql-lab15:latest`
* **Lab 13 Security Container:** `docker pull gouthudocker/nosql-lab13:latest`
* **Lab 12 Replica Set Container:** `docker pull gouthudocker/nosql-lab12:latest`

---

## 🚀 Quick Start / How to Run Locally

To run any individual lab (e.g., Lab 18):

```bash
cd Lab_18
pip install -r requirements.txt
python run_all.py          # Runs Activity 1 & Activity 2 benchmarks
python run_all.py web      # Starts interactive web dashboard on http://localhost:5000
```
"""

    with open(os.path.join(TARGET_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("Master README.md created!")

    # Git init, commit, push
    git_dir = os.path.join(TARGET_DIR, ".git")
    if not os.path.exists(git_dir):
        subprocess.run("git init -b main", cwd=TARGET_DIR, shell=True, check=True)
        subprocess.run('git config user.name "GOUTHAMI REDDY"', cwd=TARGET_DIR, shell=True, check=True)
        subprocess.run('git config user.email "gouthamireddymuli@gmail.com"', cwd=TARGET_DIR, shell=True, check=True)
        subprocess.run(f"git remote add origin {REPO_URL}", cwd=TARGET_DIR, shell=True, check=True)
    else:
        subprocess.run(f"git remote set-url origin {REPO_URL}", cwd=TARGET_DIR, shell=True, check=True)

    print("Staging and committing files...")
    subprocess.run("git add .", cwd=TARGET_DIR, shell=True, check=True)
    subprocess.run('git commit -m "Complete portfolio: All 18 NoSQL Labs (Labs 1-18) with source code, reports and web apps"', cwd=TARGET_DIR, shell=True)

    print(f"Pushing to {REPO_URL} on main branch...")
    res = subprocess.run("git push -u origin main --force", cwd=TARGET_DIR, shell=True, capture_output=True, text=True)
    print("Push Output:", res.stdout, res.stderr)
    if res.returncode == 0:
        print("\nSUCCESS! All 18 labs are live at:", REPO_URL)

if __name__ == "__main__":
    assemble()
