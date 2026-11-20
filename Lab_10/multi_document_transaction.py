import os
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/?replicaSet=rs0"))
db = client["banking"]

# Start a session for the transaction
with client.start_session() as session:
    with session.start_transaction():
        accounts = db["accounts"]
        history = db["transaction_history"]

        # Debit source account
        accounts.update_one(
            {"account_id": "ACC-001", "balance": {"$gte": 100}},
            {"$inc": {"balance": -100}},
            session=session
        )

        # Credit destination account
        accounts.update_one(
            {"account_id": "ACC-002"},
            {"$inc": {"balance": 100}},
            session=session
        )

        # Record the transaction
        history.insert_one(
            {"from": "ACC-001", "to": "ACC-002",
             "amount": 100, "timestamp": "2024-06-15T10:30:00Z"},
            session=session
        )

        # If any operation fails, the entire transaction is rolled back
        # If all succeed, the transaction is committed on session exit

print("Transfer completed successfully.")
client.close()
