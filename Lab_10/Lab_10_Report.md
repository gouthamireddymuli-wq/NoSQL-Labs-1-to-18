# NoSQL Lab 10: Multi-Document Transactions in MongoDB
## Comprehensive Laboratory Report & Submission Document

---

### Student Submission Information
- **Course / Module**: NoSQL Databases using MongoDB — Chapter 10
- **Student Name**: M Gouthami
- **Registration Number**: 24BTRCL130 (CVIP AIML-B)
- **Lab Topics**: Lab 10.1 (Bank Transfer Transaction) & Lab 10.2 (Inventory Reservation with Deadlock Handling)
- **Docker Hub Repository URL**: `https://hub.docker.com/r/gouthudocker/nosql-lab10`
- **Docker Image Tag**: `gouthudocker/nosql-lab10:latest`
- **Database Engine**: MongoDB 7.0 Replica Set (rs0, WiredTiger)
- **Web Platform Integration**: Interactive Flask Dashboard (Port 5000)
- **Reference**: [sujeetjagtap/NoSQL-Databases-using-MongoDB (Chapter 10)](https://github.com/sujeetjagtap/NoSQL-Databases-using-MongoDB/tree/main/chapter-10)

> **DOCKER HUB SUBMISSION URL (NOTE FOR GRADING):**  
> **https://hub.docker.com/r/gouthudocker/nosql-lab10**  
> *The uploaded Docker container encapsulates the full running platform, interactive web dashboard, and test runners for grading demonstration.*

---

## 1. Executive Summary & Objectives

The primary objective of this laboratory is to master **multi-document ACID transactions** in MongoDB (using PyMongo 4.x) on a WiredTiger storage engine configured with a replica set (`rs0`).

The lab covers two critical transaction patterns:
1. **Lab 10.1 (Bank Transfer System)**: Atomic fund transfer across multiple accounts, enforcing strict rollback when funds are insufficient, and implementing retry logic with exponential backoff for `TransientTransactionError`.
2. **Lab 10.2 (E-Commerce Inventory Reservation)**: Concurrent stock reservation across `inventory` and `orders` collections, preventing lost updates and race conditions via optimistic concurrency control (versioning), handling write conflicts, and benchmarking throughput (TPS) under varying concurrency levels (1, 4, 8, 16 threads).
3. **Interactive Web Application**: A full-stack Flask web application deployed in Docker to demonstrate both transaction workflows in real time.

---

## 2. Environment & System Architecture

### 2.1 Multi-Container Docker Architecture
Multi-document transactions in MongoDB require a replica set. The environment is containerized using Docker Compose:

- **`mongo_rs0` (`mongo:7.0`)**: Runs MongoDB daemon with `--replSet rs0 --bind_ip_all --port 27017`.
- **`rs_init` (`mongo:7.0`)**: Ephemeral container that executes an idempotent initialization script using `mongosh`, ensuring the replica set is active and elects a `WritablePrimary`.
- **`nosql_lab10_web` (`nosql-lab10:latest`)**: Python 3.11 container hosting the Flask web dashboard and backend transaction engine.

```
+-------------------------------------------------------------------------------+
|                             Docker Network (lab10_net)                        |
|                                                                               |
|   +-----------------------+     REST API     +----------------------------+   |
|   |   nosql_lab10_web     | <--------------> |         mongo_rs0          |   |
|   |   (Flask / PyMongo)   |                  |   (MongoDB 7.0 - rs0)      |   |
|   |   Port: 5000          |                  |   Port: 27017              |   |
|   +-----------------------+                  +----------------------------+   |
|               ^                                             ^                 |
|               | (HTTP)                                      | (rs.initiate)   |
|        Browser Client                                    rs_init              |
+-------------------------------------------------------------------------------+
```

---

## 3. Lab 10.1: Bank Transfer Transaction

### 3.1 Schema & Data Modeling
The `bank` database maintains two collections:
- **`accounts`**:
  ```json
  {
    "account_id": "ACC-001",
    "holder": "Arjun",
    "balance": 5000.00,
    "version": 0
  }
  ```
- **`transactions`** (Audit Trail):
  ```json
  {
    "from": "ACC-001",
    "to": "ACC-002",
    "amount": 1500.00,
    "description": "Salary payment",
    "timestamp": 1731848445.12
  }
  ```

### 3.2 Transaction Implementation & Rollback Mechanism
The transaction utilizes PyMongo client sessions with snapshot isolation and majority write concern:

```python
with session.start_transaction(
    read_concern=ReadConcern("snapshot"),
    write_concern=WriteConcern(w="majority")
):
    # Atomic debit with balance validation in filter
    result = col.update_one(
        {"account_id": from_id, "balance": {"$gte": amount}},
        {"$inc": {"balance": -amount, "version": 1}},
        session=session
    )
    if result.matched_count == 0:
        raise ValueError(f"Insufficient funds in {from_id} (need ${amount:.2f})")

    # Atomic credit
    col.update_one(
        {"account_id": to_id},
        {"$inc": {"balance": amount, "version": 1}},
        session=session
    )

    # Atomic audit log
    col.database["transactions"].insert_one({
        "from": from_id, "to": to_id, "amount": amount,
        "description": description, "timestamp": time.time()
    }, session=session)
```

**Rollback Enforcement**: When an account lacks adequate funds, `matched_count == 0` triggers a `ValueError`. When an unhandled exception exits the transaction context block, MongoDB automatically aborts the transaction, ensuring neither account balance is modified.

### 3.3 Activity: Exponential Backoff Retry Logic
Transient network partitions or write locks can raise errors labeled with `TransientTransactionError`. The transfer function wraps the transaction in a retry loop:

$$\text{Delay} = \text{BASE\_DELAY} \times 2^{\text{attempt}} + \text{jitter}$$

```python
except (OperationFailure, PyMongoError) as e:
    labels = getattr(e, "error_labels", []) or []
    if "TransientTransactionError" in labels and attempt < MAX_RETRIES - 1:
        delay = BASE_DELAY_S * (2 ** attempt) + random.uniform(0, 0.05)
        time.sleep(delay)
```

### 3.4 Execution Results (Lab 10.1)

```
=======================================
  Lab 10.1: Bank Transfer Transaction
=======================================
  [OK] Created 3 accounts.
  Current Balances:
    ACC-001: Arjun        $  5,000.00
    ACC-002: Sneha        $  3,000.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $1500: ACC-001 -> ACC-002 ===
  [OK] Transferred $1500.00: ACC-001 -> ACC-002  (attempt 1)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,500.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $5000: ACC-003 -> ACC-001 (should ROLLBACK) ===
  [ROLLBACK] Insufficient funds in ACC-003 (need $5000.00)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,500.00
    ACC-003: Rahul        $  1,000.00

=== Transfer $500: ACC-002 -> ACC-003 ===
  [OK] Transferred $500.00: ACC-002 -> ACC-003  (attempt 1)
  Current Balances:
    ACC-001: Arjun        $  3,500.00
    ACC-002: Sneha        $  4,000.00
    ACC-003: Rahul        $  1,500.00

=== Transaction Audit Log ===
  ACC-001 -> ACC-002  $1500.00  (Salary payment)
  ACC-002 -> ACC-003  $500.00   (Expense reimbursement)
=====================
  Lab 10.1 Complete
=====================
```

---

## 4. Lab 10.2: Inventory Reservation with Deadlock & Write Conflict Handling

### 4.1 Schema Design
The `inv_db` database contains:
- **`products`**:
  ```json
  {
    "product_id": "LAPTOP-PRO",
    "name": "UltraBook Pro",
    "stock": 5,
    "version": 0,
    "price": 999.99
  }
  ```
- **`orders`**:
  ```json
  {
    "order_id": "c1f7b82e-9d21-4f11-9fa2-58bb9f5d1341",
    "customer_id": "CUST-002",
    "items": [{"product_id": "LAPTOP-PRO", "qty": 1, "price": 999.99}],
    "status": "pending",
    "total": 999.99,
    "created_at": 1731848452.88
  }
  ```

### 4.2 Optimistic Concurrency Control (OCC)
In high-concurrency environments, multiple requests may read the same stock value simultaneously. To prevent lost updates:
1. The product is read within the transaction along with its current `version`.
2. An update is attempted with condition `{"product_id": product_id, "version": item["version"]}`.
3. If another thread committed an update first, `matched_count == 0`, raising a `WriteConflict`.
4. The transaction retries with exponential backoff until stock is exhausted or the maximum retries are reached.

### 4.3 Concurrency & Throughput Benchmarking
Simultaneous reservation requests are dispatched using Python's `ThreadPoolExecutor` across 1, 4, 8, and 16 concurrent threads against an initial stock of 5 units.

#### Benchmark Output:
```
==========================================================
  Lab 10.2: Inventory Reservation with Deadlock Handling
==========================================================

=== Scenario: 10 threads competing for 5 units ===
  [OK] Seeded 1 product with 5 units.
  Successes : 5
  Failures  : 5
  Remaining : 0 units
  Orders    : 5
  Elapsed   : 0.218 s

=== Throughput sweep (5 units, varying threads) ===
   Threads   Success    Fail   Stock   Orders   Elapsed      TPS
  --------------------------------------------------------------------
         1         1       0       4        1     0.025s   39.29
         4         4       0       1        4     0.401s    9.98
         8         5       3       0        5     0.416s   12.02
        16         5      11       0        5     0.195s   25.66
=====================
  Lab 10.2 Complete
=====================
```

### 4.4 Analysis: Transactional vs. Non-Transactional (`findAndModify`)
- **Multi-Document Transactions**: Guarantee total consistency across both the `products` and `orders` collections. If the order insertion encounters an error or network partition, the inventory decrement is rolled back automatically. Lock acquisition and snapshot generation introduce a minor throughput overhead.
- **Atomic Single-Document (`findAndModify` / `findOneAndUpdate`)**: Provides higher raw throughput by bypassing transaction lock tables, but leaves the system vulnerable to orphaned state: if the process crashes after updating inventory but before inserting the order record, units become permanently lost.

---

## 5. Web Application Integration

The Flask application (`web/app.py`) provides an interactive interface for grading and demonstration:

| URL Route | Interface | Functional Capabilities |
|---|---|---|
| `/` | System Overview | Architecture, container status, and lab navigation |
| `/lab1` | Bank Transfer Portal | Live account balance display, interactive fund transfers, one-click insufficient funds test, real-time audit ledger |
| `/lab2` | Inventory Reservation Portal | Product inventory monitor, live order ledger, configurable concurrent thread stress tester (4, 8, 10, 16 threads) |
| `/health` | Health Check | Validates replica set connectivity (`{"status": "ok", "mongo": "connected"}`) |

---

## 6. Demonstration & Verification Guide

### 6.1 Starting the Environment
```powershell
cd "C:\Users\gouth\OneDrive\Desktop\NoSQL_Lab10"
docker compose up --build -d
```

### 6.2 Accessing the Web Interface
Navigate to **`http://localhost:5000`** in any web browser.

### 6.3 Executing Backend Lab Scripts
```powershell
# Run Lab 10.1 Bank Transfer
docker exec nosql_lab10_web python /app/lab_01_bank_transfer.py

# Run Lab 10.2 Inventory Reservation
docker exec nosql_lab10_web python /app/lab_02_inventory_reservation.py
```

### 6.4 Pulling from Docker Hub
To demonstrate on any grading machine:
```bash
docker pull YOUR_DOCKERHUB_USERNAME/nosql-lab10:latest
```

---

## 7. Conclusion
This laboratory demonstrates that multi-document transactions in MongoDB deliver relational-grade ACID guarantees while maintaining high performance. By integrating version-based optimistic concurrency control and exponential backoff retry policies, the system reliably handles high concurrency, write conflicts, and transient errors without data corruption or lost updates.
