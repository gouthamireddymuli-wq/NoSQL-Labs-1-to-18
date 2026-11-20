"""Shared MongoDB connection helpers and utilities for Lab 18: Comparative Capstone.
Author: M Gouthami (24BTRCL130)
"""
import os
from pymongo import MongoClient

# MongoDB URIs – container / Atlas overridden by env, then localhost fallback
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

MONGO_URI_RS = os.getenv(
    "MONGO_URI_RS",
    "mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin",
)

MONGO_URI_STANDALONE = os.getenv(
    "MONGO_URI_STANDALONE",
    "mongodb://localhost:27017/",
)


def get_client(uri: str = None):
    """Obtain a connected MongoClient, trying preferred URIs with fallback."""
    candidate_uris = []
    if uri:
        candidate_uris.append(uri)
    if os.getenv("MONGO_URI"):
        candidate_uris.append(os.getenv("MONGO_URI"))
    if os.getenv("MONGO_URI_STANDALONE"):
        candidate_uris.append(os.getenv("MONGO_URI_STANDALONE"))
    if os.getenv("MONGO_URI_RS"):
        candidate_uris.append(os.getenv("MONGO_URI_RS"))

    # Common environments: local mongod, docker, host.docker.internal
    candidate_uris.extend([
        "mongodb://localhost:27017/",
        "mongodb://127.0.0.1:27017/",
        "mongodb://host.docker.internal:27017/",
        "mongodb://mongo:27017/",
    ])

    for target in candidate_uris:
        try:
            client = MongoClient(
                target,
                serverSelectionTimeoutMS=2000,
                directConnection=True if (
                    "localhost" in target
                    or "127.0.0.1" in target
                    or "host.docker.internal" in target
                ) else False,
            )
            client.admin.command("ping")
            return client
        except Exception:
            continue

    # Final fallback attempt
    return MongoClient(uri or MONGO_URI, serverSelectionTimeoutMS=3000)


def get_db(db_name: str = "nosql_labs", uri: str = None):
    return get_client(uri)[db_name]


def reset_collection(db_name: str, collection_name: str, uri: str = None):
    """Drop and recreate a collection, returning the collection object."""
    db = get_db(db_name, uri)
    db[collection_name].drop()
    return db[collection_name]


def banner(msg: str):
    line = "=" * (len(msg) + 8)
    print(f"\n{line}\n  [LAB 18] {msg}\n{line}")
