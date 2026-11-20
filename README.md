# NoSQL Database Systems — Complete Laboratory Portfolio (Labs 1–18)

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
