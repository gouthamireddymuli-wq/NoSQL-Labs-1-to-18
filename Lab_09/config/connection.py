"""Shared MongoDB connection helpers for Lab 9."""
import os
from pymongo import MongoClient

REPLICA_SET_URI = os.getenv(
    "REPLICA_SET_URI",
    os.getenv("MONGO_URI", "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&serverSelectionTimeoutMS=5000")
)


def get_client():
    return MongoClient(REPLICA_SET_URI, serverSelectionTimeoutMS=5000)


def banner(msg: str):
    line = "=" * (len(msg) + 4)
    print(f"\n{line}\n  {msg}\n{line}")
