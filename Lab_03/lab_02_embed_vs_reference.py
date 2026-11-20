"""Lab 3.2 - Migrate from Referenced to Embedded Design
Blog system demonstrating referenced (normalized) vs embedded (denormalized) schema.
Includes $lookup retrieval, aggregation pipeline data migration, and query count comparison.
"""

import os
import sys
from bson import ObjectId
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.connection import get_db, banner, export_collection_to_json

INITIAL_POSTS = [
    {
        "_id": ObjectId("665000000000000000000001"),
        "title": "Architecting Scalable Microservices with MongoDB",
        "author": "Dr. Priya Sharma",
        "tags": ["architecture", "microservices", "mongodb"],
        "views": 1420,
        "published_at": datetime(2026, 1, 10, 9, 30, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId("665000000000000000000002"),
        "title": "Mastering Aggregation Pipelines & Window Functions",
        "author": "Arjun Mehta",
        "tags": ["aggregation", "analytics", "database"],
        "views": 2150,
        "published_at": datetime(2026, 1, 18, 14, 0, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId("665000000000000000000003"),
        "title": "CAP Theorem Demystified: CP vs AP Trade-offs",
        "author": "Sneha Reddy",
        "tags": ["distributed-systems", "cap", "consistency"],
        "views": 3100,
        "published_at": datetime(2026, 2, 1, 11, 15, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId("665000000000000000000004"),
        "title": "Vector Search and Generative AI Embeddings",
        "author": "Dr. Anil Gupta",
        "tags": ["ai", "vector-search", "llm"],
        "views": 4890,
        "published_at": datetime(2026, 2, 14, 16, 45, tzinfo=timezone.utc)
    },
    {
        "_id": ObjectId("665000000000000000000005"),
        "title": "Graph Traversal vs Embedded Documents in NoSQL",
        "author": "Dr. Meera Joshi",
        "tags": ["graph", "data-modeling", "schema-design"],
        "views": 1870,
        "published_at": datetime(2026, 2, 25, 10, 0, tzinfo=timezone.utc)
    }
]

INITIAL_COMMENTS = [
    {"post_id": ObjectId("665000000000000000000001"), "author": "DevGuru", "text": "Great insights on bounded contexts with document databases!", "likes": 12, "created_at": datetime(2026, 1, 10, 10, 15, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000001"), "author": "CloudArchitect", "text": "How do you handle cross-service distributed transactions?", "likes": 5, "created_at": datetime(2026, 1, 11, 8, 45, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000002"), "author": "MongoCoder", "text": "$facet and $bucket are game changers for reporting dashboards.", "likes": 18, "created_at": datetime(2026, 1, 19, 9, 0, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000002"), "author": "DataScientist", "text": "The memory limit of 100MB per pipeline stage is worth noting.", "likes": 9, "created_at": datetime(2026, 1, 20, 11, 20, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000002"), "author": "StudentDev", "text": "Clear explanation of $lookup pipeline expressions, thank you!", "likes": 4, "created_at": datetime(2026, 1, 21, 15, 30, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000003"), "author": "SystemDesigner", "text": "PACELC theorem is also critical when there is no network partition.", "likes": 22, "created_at": datetime(2026, 2, 2, 13, 10, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000003"), "author": "NetAdmin", "text": "Network partitions are unavoidable; latency vs consistency is the real choice.", "likes": 14, "created_at": datetime(2026, 2, 3, 17, 40, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000004"), "author": "AIEngineer", "text": "Hierarchical Navigable Small World (HNSW) indexing makes search blazingly fast.", "likes": 31, "created_at": datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000004"), "author": "NLPResearcher", "text": "Combining vector similarity with scalar metadata filters is very elegant.", "likes": 17, "created_at": datetime(2026, 2, 16, 12, 15, tzinfo=timezone.utc)},
    {"post_id": ObjectId("665000000000000000000005"), "author": "GraphFanatic", "text": "$graphLookup handles tree hierarchies well up to reasonable depth.", "likes": 8, "created_at": datetime(2026, 2, 26, 14, 50, tzinfo=timezone.utc)}
]


def main():
    banner("Activity 3.2: Referenced to Embedded Schema Migration")
    db = get_db("nosql_labs")

    posts_col = db["blog_posts_referenced"]
    comments_col = db["blog_comments_referenced"]
    posts_col.drop()
    comments_col.drop()

    posts_col.insert_many(INITIAL_POSTS)
    comments_col.insert_many(INITIAL_COMMENTS)
    comments_col.create_index("post_id")
    print(f"[OK] Seeded '{posts_col.name}': {posts_col.count_documents({})} documents")
    print(f"[OK] Seeded '{comments_col.name}': {comments_col.count_documents({})} documents (indexed on post_id)\n")

    target_post_id = ObjectId("665000000000000000000002")
    print("=" * 72)
    print(f"STEP 2: Single-Query Retrieval using $lookup for Post ID: {target_post_id}")
    print("=" * 72)

    lookup_pipeline = [
        {"$match": {"_id": target_post_id}},
        {
            "$lookup": {
                "from": "blog_comments_referenced",
                "localField": "_id",
                "foreignField": "post_id",
                "as": "comments"
            }
        }
    ]
    joined_result = list(posts_col.aggregate(lookup_pipeline))[0]
    print(f"Post Title   : {joined_result['title']}")
    print(f"Author       : {joined_result['author']}")
    print(f"Tags         : {', '.join(joined_result['tags'])}")
    print(f"Comment Count: {len(joined_result['comments'])}")
    print("Retrieved Comments via $lookup:")
    for idx, c in enumerate(joined_result['comments'], 1):
        print(f"  [{idx}] @{c['author']} ({c['likes']} likes): \"{c['text']}\"")
    print()

    print("=" * 72)
    print("STEP 3: Migrating Data from Referenced to Embedded Schema via $out")
    print("=" * 72)

    embedded_col_name = "blog_posts_embedded"
    if embedded_col_name in db.list_collection_names():
        db.drop_collection(embedded_col_name)

    migration_pipeline = [
        {
            "$lookup": {
                "from": "blog_comments_referenced",
                "localField": "_id",
                "foreignField": "post_id",
                "pipeline": [{"$project": {"post_id": 0}}],
                "as": "comments"
            }
        },
        {
            "$addFields": {
                "comment_count": {"$size": "$comments"},
                "migrated_at": datetime.now(timezone.utc)
            }
        },
        {"$out": embedded_col_name}
    ]
    posts_col.aggregate(migration_pipeline)
    embedded_col = db[embedded_col_name]
    migrated_count = embedded_col.count_documents({})
    print(f"[OK] Server-side aggregation migration complete.")
    print(f"[OK] Created '{embedded_col_name}' collection with {migrated_count} embedded documents.\n")

    sample_emb = embedded_col.find_one({"_id": target_post_id})
    print("Sample Migrated Embedded Document Structure:")
    print(f"  Post Title    : {sample_emb['title']}")
    print(f"  Embedded Array: 'comments' ({len(sample_emb['comments'])} embedded items)")
    print(f"  Comment Count : {sample_emb['comment_count']}")
    print(f"  First Comment : Author={sample_emb['comments'][0]['author']}, Likes={sample_emb['comments'][0]['likes']}\n")

    print("=" * 72)
    print("STEP 4: Database Query Count & Architectural Performance Comparison")
    print("=" * 72)
    print("  • Referenced Design (Application Joins) : 2 Database Queries (2 network roundtrips)")
    print("  • Referenced Design ($lookup Pipeline)  : 1 Database Query (server join overhead)")
    print("  • Embedded Design (Single Document)     : 1 Database Query (0 joins, 1 single I/O fetch)\n")

    print("-" * 72)
    print(f"{'Performance Metric':<25} | {'Referenced Design':<20} | {'Embedded Design':<22}")
    print("-" * 72)
    print(f"{'DB Queries to Display':<25} | {'2 (or 1 with $lookup)':<20} | {'1 (Simple find_one)':<22}")
    print(f"{'Server Join Overhead':<25} | {'Yes ($lookup stage)':<20} | {'None (No join required)':<22}")
    print(f"{'Storage Locality':<25} | {'Fragmented (2 col)':<20} | {'Contiguous on disk':<22}")
    print(f"{'Data Duplication':<25} | {'Zero (Normalized)':<20} | {'Possible if denorm':<22}")
    print(f"{'Document Size Limit':<25} | {'Independent (16MB)':<20} | {'Must fit within 16MB':<22}")
    print(f"{'Atomicity / ACID':<25} | {'Multi-document txn':<20} | {'Single-doc atomic':<22}")
    print(f"{'Ideal Scenario':<25} | {'10,000+ comments':<20} | {'< 100 comments/post':<22}")
    print("-" * 72)
    print()

    json_path = os.path.join(BASE_DIR, "Activity_3.2", "posts_referenced_and_embedded.json")
    export_collection_to_json("nosql_labs", embedded_col_name, json_path)
    banner("Activity 3.2 Execution Complete")


if __name__ == "__main__":
    main()
