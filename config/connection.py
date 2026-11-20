"""Shared MongoDB connection helpers and utilities for Lab 13."""
import os
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://admin:AdminPass123!@localhost:27017,localhost:27018,localhost:27019/admin?replicaSet=rs0&authSource=admin"
)

def get_client(uri: str = None):
    target_uri = uri or MONGO_URI
    return MongoClient(target_uri, serverSelectionTimeoutMS=5000)

def get_db(db_name: str = "nosql_labs", uri: str = None):
    return get_client(uri)[db_name]

def banner(msg: str):
    line = "=" * (len(msg) + 8)
    print(f"\n{line}\n  [LAB 13] {msg}\n{line}")
