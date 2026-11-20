# NoSQL Lab 10 — MongoDB Multi-Document Transactions

## Quick Start (Docker)

```bash
# 1. Build and launch everything
docker compose up --build -d

# 2. Wait ~20 seconds for MongoDB replica set to initialise, then open:
#    http://localhost:5000

# 3. Run lab scripts inside the container
docker exec nosql_lab10_web python /app/lab_01_bank_transfer.py
docker exec nosql_lab10_web python /app/lab_02_inventory_reservation.py

# 4. Stop all containers
docker compose down
```

## Labs

| Lab | File | Topic |
|-----|------|-------|
| 10.1 | `lab_01_bank_transfer.py` | ACID bank transfer + rollback + exponential-backoff retry |
| 10.2 | `lab_02_inventory_reservation.py` | Inventory reservation + write-conflict handling + throughput sweep |

## Web UI

The Flask web application (`web/app.py`) provides an interactive dashboard:

- **/** — Home page with architecture overview
- **/lab1** — Execute transfers, test rollback, view audit log
- **/lab2** — Reserve inventory, run concurrent test, view orders
- **/health** — MongoDB connectivity check

## Docker Hub

Image is published on Docker Hub:
```bash
docker pull gouthudocker/nosql-lab10:latest
```
Docker Hub URL: https://hub.docker.com/r/gouthudocker/nosql-lab10
