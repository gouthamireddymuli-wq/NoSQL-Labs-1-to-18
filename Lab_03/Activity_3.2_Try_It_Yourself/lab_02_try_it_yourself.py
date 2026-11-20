"""Activity 3.2 (Try It Yourself): High-Volume Comments Architecture & Benchmark
Deep architectural analysis and PyMongo implementation of the 10,000 Comments Challenge.
Demonstrates why embedding 10,000 comments causes 16MB document limit risks, RAM working set
thrashing, and write lock contention.
Implements the industry-standard SUBSET PATTERN and compound index pagination for massive scale.
"""

import os
import sys
import time
from bson import ObjectId, BSON
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
for path in (BASE_DIR, PARENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from config.connection import get_db, banner, export_collection_to_json


def print_theoretical_analysis():
    """Print architectural breakdown of why embedding 10,000 comments is problematic."""
    print("=" * 75)
    print("ARCHITECTURAL ANALYSIS: THE 10,000 COMMENTS EMBEDDING PROBLEM")
    print("=" * 75)
    print("""
1. WHY FULL EMBEDDING FAILS AT 10,000 COMMENTS:
   ---------------------------------------------------------------------
   A. 16MB BSON Document Limit Violation:
      • MongoDB enforces a hard 16MB document size ceiling (BSONObjMaxInternalSize).
      • If each rich comment (user metadata, text, timestamps, upvotes, replies)
        averages 500 to 1,500 bytes:
        - 10,000 comments × 1,000 bytes = 10,000,000 bytes (~9.54 MB).
        - Rich comments with threads or media URLs easily exceed 16MB, triggering
          fatal BSON serialization errors and crashing write operations.
   
   B. RAM & WiredTiger Working Set Thrashing:
      • When a client requests a blog post, MongoDB reads the ENTIRE document from
        disk into the WiredTiger cache.
      • Loading a 10MB document repeatedly into RAM for readers who only glance
        at the first few comments purges hot cache pages, severely degrading
        database throughput for all other queries.

   C. Massive Network Bandwidth Waste & Latency:
      • Mobile users on cellular networks must download 10MB of comments just
        to read the article text.
      • Destroys Time to First Meaningful Paint (TTFP) and increases mobile latency.

   D. WiredTiger Storage Fragmentation & Document Relocation:
      • In-place continuous document growth caused by $push forces WiredTiger to
        continually allocate new extent space, rewriting the document to new disk
        locations, creating excessive write amplification and disk fragmentation.

   E. Concurrency & Write Lock Contention:
      • MongoDB uses document-level locking. When 10,000 users comment on a viral
        post concurrently, every comment write must acquire an exclusive write lock
        on that SAME single post document, creating catastrophic lock queues.

2. ALTERNATIVE SCALABLE ARCHITECTURES:
   ---------------------------------------------------------------------
   • Pattern 1: THE SUBSET PATTERN (Industry Standard / Best Practice)
     Embed only the TOP N (e.g. 5 most recent) comments inside the post document
     for instant initial page render, while storing ALL comments in a dedicated
     collection indexed by (post_id, created_at).
   
   • Pattern 2: THE BUCKET PATTERN (Paging Buckets)
     Group comments into bounded bucket documents (e.g., 50 comments per bucket
     document) referencing post_id and bucket_index.

   • Pattern 3: PURE REFERENCED WITH CURSOR-BASED PAGINATION
     Normalized comments collection with compound index { post_id: 1, created_at: -1 }.
     Clients fetch comments incrementally using limit(20).
    """)


def main():
    banner("Activity 3.2 (Try It Yourself): 10,000 Comments at Scale")
    print_theoretical_analysis()

    db = get_db("nosql_labs")

    # Collections
    posts_col = db["scale_posts"]
    comments_col = db["scale_comments"]
    posts_col.drop()
    comments_col.drop()

    # Indexing comments for rapid cursor pagination
    comments_col.create_index([("post_id", 1), ("created_at", -1)])

    # 1. Create a viral blog post
    post_id = ObjectId()
    post_doc = {
        "_id": post_id,
        "title": "Quantum Computing & Neuromorphic AI Breakthroughs 2026",
        "author": "Dr. Priya Sharma",
        "content": "Exploring topological qubits, scalable error correction, and quantum supremacy...",
        "views": 250000,
        "comment_count": 0,
        "recent_comments": []  # SUBSET PATTERN: Maintains strictly the latest 5 comments
    }
    posts_col.insert_one(post_doc)
    print(f"[OK] Created viral post '{post_doc['title']}' (ID: {post_id})\n")

    # 2. Simulate high-volume comments using the SUBSET PATTERN
    print("=" * 75)
    print("IMPLEMENTATION: Simulating High-Volume Comments via the SUBSET PATTERN")
    print("=" * 75)

    simulated_comments_count = 1000  # High sample simulation for benchmarking
    print(f"Simulating {simulated_comments_count} high-frequency comments arriving concurrently...")

    comment_batch = []
    base_time = time.time()
    for i in range(1, simulated_comments_count + 1):
        c_doc = {
            "_id": ObjectId(),
            "post_id": post_id,
            "author": f"Researcher_{i % 50}",
            "text": f"Crucial observation #{i}: What are the cryogenic cooling requirements for this architecture?",
            "likes": (i * 7) % 100,
            "created_at": datetime.fromtimestamp(base_time + i, tz=timezone.utc)
        }
        comment_batch.append(c_doc)

    # Insert into dedicated comments collection
    t0 = time.perf_counter()
    comments_col.insert_many(comment_batch)
    t_insert = time.perf_counter() - t0
    print(f"[OK] Inserted {len(comment_batch)} comments into dedicated collection in {t_insert*1000:.2f} ms")

    # Update post using SUBSET PATTERN ($push with $slice: -5 to keep latest 5 comments embedded)
    # This keeps the post document size perfectly constant regardless of 10,000 comments!
    latest_5 = [
        {"author": c["author"], "text": c["text"], "likes": c["likes"], "created_at": c["created_at"]}
        for c in comment_batch[-5:]
    ]
    posts_col.update_one(
        {"_id": post_id},
        {
            "$set": {"recent_comments": latest_5},
            "$inc": {"comment_count": simulated_comments_count}
        }
    )
    print(f"[OK] Updated post with Subset Pattern: embedded latest 5 comments & comment_count={simulated_comments_count}\n")

    # 3. Document Size & BSON Analysis
    print("=" * 75)
    print("BSON DOCUMENT SIZE & MEMORY IMPACT COMPARISON")
    print("=" * 75)

    updated_post = posts_col.find_one({"_id": post_id})
    subset_bson_bytes = len(BSON.encode(updated_post))

    # Calculate theoretical fully-embedded 10,000 comments document size
    sample_comment_bytes = len(BSON.encode(comment_batch[0]))
    projected_10k_embedded_bytes = subset_bson_bytes + (sample_comment_bytes * 10000)
    projected_10k_mb = projected_10k_embedded_bytes / (1024 * 1024)
    limit_mb = 16.0

    print(f"  • Single Comment BSON Size            : {sample_comment_bytes} bytes")
    print(f"  • Subset Pattern Post Document Size   : {subset_bson_bytes:,} bytes ({subset_bson_bytes/1024:.2f} KB)")
    print(f"  • Projected 10,000 Embedded Doc Size  : {projected_10k_embedded_bytes:,} bytes ({projected_10k_mb:.2f} MB)")
    print(f"  • MongoDB Hard BSON Size Limit        : 16,777,216 bytes ({limit_mb:.2f} MB)")
    print(f"  • Capacity Consumed by Fully Embedded : {(projected_10k_mb / limit_mb) * 100:.1f}% of MAX ALLOWABLE CAPACITY!\n")

    # 4. Read Query Benchmark: Initial Page Load vs Paginated Comments
    print("=" * 75)
    print("QUERY PERFORMANCE: Zero-Join Initial Load vs Paginated Fetch")
    print("=" * 75)

    # Initial Page Load: 1 fast query, retrieves article + 5 latest preview comments
    t_start = time.perf_counter()
    post_view = posts_col.find_one({"_id": post_id})
    t_post_load = (time.perf_counter() - t_start) * 1000

    print(f"1. Initial Article Page Load (Subset Pattern):")
    print(f"   • Database Queries : 1 (find_one)")
    print(f"   • Latency          : {t_post_load:.3f} ms")
    print(f"   • Payload Size     : {len(BSON.encode(post_view))} bytes")
    print(f"   • Preview Comments : {len(post_view['recent_comments'])} preview comments displayed instantly")
    for idx, c in enumerate(post_view['recent_comments'], 1):
        print(f"     ↳ [{idx}] @{c['author']}: {c['text'][:55]}...")
    print()

    # On-demand Pagination (User clicks 'View All Comments' or scrolls down)
    page_size = 10
    t_start = time.perf_counter()
    paginated_comments = list(comments_col.find(
        {"post_id": post_id}
    ).sort("created_at", -1).skip(5).limit(page_size))
    t_page_load = (time.perf_counter() - t_start) * 1000

    print(f"2. On-Demand Paginated Comments Fetch (Page 2, 10 comments):")
    print(f"   • Database Queries : 1 (Indexed cursor query using post_id + created_at)")
    print(f"   • Latency          : {t_page_load:.3f} ms")
    print(f"   • Comments Fetched : {len(paginated_comments)} records")
    print(f"   • Payload Size     : {sum(len(BSON.encode(c)) for c in paginated_comments)} bytes")
    print()

    # Step 5: Export collection state to JSON
    json_path = os.path.join(BASE_DIR, "high_volume_comments_subset_pattern.json")
    export_collection_to_json("nosql_labs", "scale_posts", json_path)

    banner("Activity 3.2 Try It Yourself Complete")


if __name__ == "__main__":
    main()
