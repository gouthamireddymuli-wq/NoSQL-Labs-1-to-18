"""Shared MongoDB connection helpers for Lab 12 Security."""
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

def get_client(uri: str = None):
    target_uri = uri or MONGO_URI
    return MongoClient(target_uri, serverSelectionTimeoutMS=5000)

def get_db(db_name: str = "nosql_labs", uri: str = None):
    return get_client(uri)[db_name]

def reset_collection(db_name: str, col_name: str, uri: str = None):
    db = get_db(db_name, uri)
    db[col_name].drop()
    return db[col_name]

def banner(msg: str):
    line = "=" * (len(msg) + 6)
    print(f"\n{line}\n  [SEC] {msg}\n{line}")
