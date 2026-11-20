"""Shared MongoDB connection helpers and utilities for Lab 14."""
import os
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin"
)

# Fallback for standalone / local dev
MONGO_URI_STANDALONE = os.getenv(
    "MONGO_URI_STANDALONE",
    "mongodb://localhost:27017"
)


def get_client(uri: str = None):
    target = uri or MONGO_URI
    try:
        client = MongoClient(target, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except Exception:
        # Try standalone fallback
        client = MongoClient(MONGO_URI_STANDALONE, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client


def get_db(db_name: str = "nosql_labs", uri: str = None):
    return get_client(uri)[db_name]


def reset_collection(db_name: str, collection_name: str):
    """Drop and recreate a collection, returning the collection object."""
    db = get_db(db_name)
    db[collection_name].drop()
    return db[collection_name]


def banner(msg: str):
    line = "=" * (len(msg) + 8)
    print(f"\n{line}\n  [LAB 14] {msg}\n{line}")
