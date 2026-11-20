"""Shared MongoDB connection helpers."""
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/?replicaSet=rs0")


def get_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)


def banner(msg: str):
    line = "=" * (len(msg) + 4)
    print(f"\n{line}\n  {msg}\n{line}")
