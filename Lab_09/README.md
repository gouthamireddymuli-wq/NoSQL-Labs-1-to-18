# NoSQL Lab 9 — Write Concern Latency & Network Partition Simulation

**Student:** M Gouthami (24BTRCL130)  
**Docker Hub Repository:** [https://hub.docker.com/r/gouthudocker/nosql-lab-9](https://hub.docker.com/r/gouthudocker/nosql-lab-9)

---

## Quick Start (Docker)

### 1. Pull and Launch the Platform
```bash
# Pull the latest image from Docker Hub
docker pull gouthudocker/nosql-lab-9:latest

# Run the container (maps interactive dashboard to http://localhost:5000)
docker run -d -p 5000:5000 --name nosql-lab9-demo gouthudocker/nosql-lab-9:latest
```

### 2. Access the Interactive Dashboard
Open your web browser and navigate to:
**http://localhost:5000/lab9_reports.html**

---

## Running Lab Scripts Inside the Container

```bash
# Lab 9.1: Write Concern Latency Benchmark (1,000 writes)
docker exec -it nosql-lab9-demo python /app/Activity_9_1/activity_9_1.py

# Activity 9.1 Try It Yourself: Journaling Overhead (j:true vs j:false)
docker exec -it nosql-lab9-demo python /app/Activity_9_1_TryItYourself/activity_9_1_try.py

# Lab 9.2: Simulate Network Partition (Single node isolated)
docker exec -it nosql-lab9-demo python /app/Activity_9_2/activity_9_2.py

# Activity 9.2 Try It Yourself: Total Quorum Collapse, Step-down & Re-election
docker exec -it nosql-lab9-demo python /app/Activity_9_2_TryItYourself/activity_9_2_try.py

# Starter Scripts
docker exec -it nosql-lab9-demo python /app/lab_01_write_concern_latency.py
docker exec -it nosql-lab9-demo bash /app/lab_02_simulate_partition.sh
```

---

## Lab Structure

```
NoSQL_Lab_9/
├── Dockerfile                           # Container definition for Docker Hub
├── docker-compose.yml                   # Multi-node cluster orchestration
├── Lab9_Report.pdf                      # Comprehensive PDF report with Docker URL
├── Lab9_Report.docx                     # Academic report in Word format
├── Lab9_Report.html                     # Standalone HTML report
├── Write-Concern-TradeOffs.jpg          # Specification diagram
├── Activity_9_1/                        # Lab 9.1: Write concern latency benchmark
│   ├── activity_9_1.py
│   ├── docker-compose.yml
│   └── results_activity_9_1.json
├── Activity_9_1_TryItYourself/          # Activity 9.1: Journaling overhead
│   ├── activity_9_1_try.py
│   ├── docker-compose.yml
│   └── results_activity_9_1_try.json
├── Activity_9_2/                        # Lab 9.2: Single node network partition
│   ├── activity_9_2.py
│   ├── docker-compose.yml
│   ├── lab_02_simulate_partition.sh
│   └── results_activity_9_2.json
├── Activity_9_2_TryItYourself/          # Activity 9.2: Quorum collapse & stepdown
│   ├── activity_9_2_try.py
│   ├── docker-compose.yml
│   └── results_activity_9_2_try.json
└── web_platform/                        # Integrated CTI Platform (Flask + Web UI)
```
