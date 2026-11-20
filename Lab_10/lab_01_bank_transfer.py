"""Lab 10.1 - Implement a Bank Transfer Transaction
Multi-document ACID transactions with exponential-backoff retry logic.

Requires: MongoDB 4.0+ running as a replica set (rs0).
"""

import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from pymongo.errors import OperationFailure, PyMongoError
from config.connection import banner, get_client

MAX_RETRIES = 5
BASE_DELAY_S = 0.1   # 100 ms


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def create_accounts(col):
    """Drop and re-seed the accounts collection."""
    col.drop()
    col.insert_many([
        {"account_id": "ACC-001", "holder": "Arjun",  "balance": 5000.00, "version": 0},
        {"account_id": "ACC-002", "holder": "Sneha",  "balance": 3000.00, "version": 0},
        {"account_id": "ACC-003", "holder": "Rahul",  "balance": 1000.00, "version": 0},
    ])
    print("  [OK] Created 3 accounts.")


def print_balances(col):
    print("  Current Balances:")
    for doc in col.find({}, sort=[("account_id", 1)]):
        print(f"    {doc['account_id']}: {doc['holder']:<12} ${doc['balance']:>10,.2f}")


# ---------------------------------------------------------------------------
# Core transaction (single attempt)
# ---------------------------------------------------------------------------

def _do_transfer(col, from_id, to_id, amount, description, session):
    """Execute all transaction operations inside an already-started session."""
    # Debit – filter includes balance check → zero matched == insufficient funds
    result = col.update_one(
        {"account_id": from_id, "balance": {"$gte": amount}},
        {"$inc": {"balance": -amount, "version": 1}},
        session=session,
    )
    if result.matched_count == 0:
        raise ValueError(f"Insufficient funds in {from_id} (need ${amount:.2f})")

    # Credit
    col.update_one(
        {"account_id": to_id},
        {"$inc": {"balance": amount, "version": 1}},
        session=session,
    )

    # Audit record
    col.database["transactions"].insert_one(
        {
            "from": from_id,
            "to": to_id,
            "amount": amount,
            "description": description,
            "timestamp": time.time(),
        },
        session=session,
    )


# ---------------------------------------------------------------------------
# Public API – wraps _do_transfer with retry + exponential back-off
# ---------------------------------------------------------------------------

def transfer_funds(col, from_id, to_id, amount, description=""):
    """Transfer funds between accounts using an ACID transaction.

    Retries up to MAX_RETRIES times on TransientTransactionError with
    exponential back-off + jitter (Activity requirement for Lab 10.1).

    Returns True on success, False on permanent failure.
    """
    client = col.database.client

    for attempt in range(MAX_RETRIES):
        session = client.start_session()
        try:
            with session.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority"),
            ):
                _do_transfer(col, from_id, to_id, amount, description, session)

            print(f"  [OK] Transferred ${amount:.2f}: {from_id} → {to_id}  (attempt {attempt+1})")
            return True

        except ValueError as e:
            # Business-logic failure – do NOT retry
            print(f"  [ROLLBACK] {e}")
            return False

        except (OperationFailure, PyMongoError) as e:
            labels = getattr(e, "error_labels", []) or []
            if "TransientTransactionError" in labels and attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY_S * (2 ** attempt) + random.uniform(0, 0.05)
                print(f"  [RETRY] TransientTransactionError – retrying in {delay*1000:.0f} ms (attempt {attempt+1})")
                time.sleep(delay)
            else:
                print(f"  [FAIL] {e}")
                return False

        finally:
            session.end_session()

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    banner("Lab 10.1: Bank Transfer Transaction")
    client = get_client()
    db     = client["bank"]
    col    = db["accounts"]

    create_accounts(col)
    print_balances(col)

    # Scenario 1 – successful transfer
    print("\n=== Transfer $1500: ACC-001 → ACC-002 ===")
    transfer_funds(col, "ACC-001", "ACC-002", 1500.00, "Salary payment")
    print_balances(col)

    # Scenario 2 – insufficient funds (should rollback, balances unchanged)
    print("\n=== Transfer $5000: ACC-003 → ACC-001 (should ROLLBACK) ===")
    transfer_funds(col, "ACC-003", "ACC-001", 5000.00, "Exceeds balance")
    print_balances(col)

    # Scenario 3 – normal transfer that succeeds
    print("\n=== Transfer $500: ACC-002 → ACC-003 ===")
    transfer_funds(col, "ACC-002", "ACC-003", 500.00, "Expense reimbursement")
    print_balances(col)

    # Transaction audit log
    print("\n=== Transaction Audit Log ===")
    for t in db["transactions"].find({}, {"_id": 0}).sort("timestamp", 1):
        print(f"  {t['from']} → {t['to']}  ${t['amount']:.2f}  ({t['description']})")

    client.close()
    banner("Lab 10.1 Complete")


if __name__ == "__main__":
    main()
