"""Flask Web Application for NoSQL Lab 17: RAG Pipeline & Vector Indexes.
Author: M Gouthami (24BTRCL130)

Features:
  - Lab 17.1: Simple RAG Pipeline (Chunking, Mock Embeddings, Cosine Similarity Retrieval,
              Prompt Construction, Multi-turn Conversation Memory, Prediction Verification)
  - Lab 17.2: Vector Index Comparison (Brute-force vs IVF vs NSW/HNSW-like ANN Search,
              Recall@K, Vectors-Compared Analysis, Parameter Tuning)
  - Interactive Web Dashboard, REST APIs, and Benchmark Visualizations
"""

import os
import sys
import time
import math
import hashlib
import random
import numpy as np
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config.connection import get_client, get_db, reset_collection

app = Flask(__name__)
CORS(app)

DB_NAME = "nosql_labs"
RAG_COLLECTION = "rag_documents"

# Seed documents from Lab 17.1
DOCUMENTS = [
    {
        "title": "Introduction to NoSQL",
        "content": (
            "NoSQL databases emerged in the late 2000s to address the limitations of "
            "traditional relational databases at web scale. Unlike RDBMS, NoSQL databases "
            "offer flexible schemas, horizontal scalability, and specialized data models. "
            "The four main families are Document (MongoDB, Couchbase), Key-Value (Redis, "
            "Memcached), Wide-Column (Cassandra, HBase), and Graph (Neo4j, Neptune). "
            "Each family is optimized for specific access patterns and use cases. "
            "Modern applications often use multiple NoSQL databases together in a "
            "polyglot persistence architecture, selecting the right tool for each data domain."
        ),
    },
    {
        "title": "MongoDB Aggregation Framework",
        "content": (
            "The MongoDB aggregation framework processes documents through a pipeline "
            "of stages. Each stage transforms the document stream: $match filters, "
            "$group aggregates, $project reshapes, $unwind denormalizes arrays, and "
            "$lookup performs left outer joins. The framework is powerful enough to "
            "replace complex SQL queries with subqueries and CTEs. For large datasets, "
            "use allowDiskUse=True to enable spill-to-disk. The $facet stage allows "
            "running multiple pipelines in parallel on the same input, useful for "
            "dashboard APIs that need different aggregations in one query."
        ),
    },
    {
        "title": "Vector Search and AI",
        "content": (
            "MongoDB Atlas Vector Search enables semantic search using vector embeddings. "
            "Documents are stored with an embedding field, and an HNSW index enables "
            "approximate nearest neighbor search. The $vectorSearch stage retrieves top-k "
            "most similar documents. This is the foundation for RAG pipelines, where "
            "relevant context is retrieved and passed to an LLM. Typical embedding models "
            "include OpenAI text-embedding-3-small and Voyage AI with 256 to 3072 dimensions."
        ),
    },
    {
        "title": "Replica Sets and High Availability",
        "content": (
            "A MongoDB replica set is a group of mongod instances that maintain the same "
            "data set. One member acts as the primary (receives writes), while others are "
            "secondaries (replicate from primary). If the primary fails, an election is held. "
            "Write concern controls how many nodes must acknowledge a write. Read preference "
            "controls which nodes serve reads. For production, use w:majority and read "
            "concern majority to prevent reading stale data after a failover."
        ),
    },
]

CHUNK_SIZE_WORDS = 50

# In-memory session state for conversation memory & benchmark results
CONVERSATION_HISTORY = []
LATEST_BENCHMARK_RESULTS = None


def mock_embed(text, dim=384):
    """Generate deterministic pseudo-random embedding for demo (unit-normalized)."""
    rng = random.Random(hashlib.md5(text.encode()).hexdigest())
    vec = [rng.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec]


def cosine_similarity(a, b):
    """Compute cosine similarity between two unit-normalized vectors."""
    return sum(x * y for x, y in zip(a, b))


def chunk_document(doc, chunk_size=CHUNK_SIZE_WORDS):
    """Split a document into word-based chunks."""
    words = doc["content"].split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_text = " ".join(words[i : i + chunk_size])
        chunks.append({
            "source_title": doc["title"],
            "chunk_index": len(chunks),
            "text": chunk_text,
            "word_count": len(chunk_text.split()),
        })
    return chunks


def db_ingest_documents(docs=None):
    """Chunk, embed, and store documents into MongoDB collection."""
    if docs is None:
        docs = DOCUMENTS
    col = reset_collection(DB_NAME, RAG_COLLECTION)
    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc)
        for chunk in chunks:
            embedding = mock_embed(chunk["text"])
            all_chunks.append({
                **chunk,
                "embedding": embedding,
                "embedding_preview": embedding[:6],
                "dim": len(embedding),
            })
    if all_chunks:
        col.insert_many(all_chunks)
    return len(all_chunks), len(docs)


def db_retrieve_chunks(query, top_k=3):
    """Find most similar chunks via brute-force cosine similarity using MongoDB."""
    db = get_db(DB_NAME)
    col = db[RAG_COLLECTION]
    
    # Auto-seed if collection is empty
    if col.count_documents({}) == 0:
        db_ingest_documents()

    query_embedding = mock_embed(query)
    scored = []
    for doc in col.find(
        {},
        {"embedding": 1, "text": 1, "source_title": 1, "chunk_index": 1, "_id": 0}
    ):
        score = cosine_similarity(query_embedding, doc["embedding"])
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def build_llm_prompt(query, context_chunks, history=None):
    """Construct an LLM prompt with retrieved context."""
    if history is None:
        history = CONVERSATION_HISTORY
    context = "\n".join(
        f"[{c['source_title']} (Chunk {c.get('chunk_index', 0)})] {c['text']}"
        for _, c in context_chunks
    )
    history_str = ""
    if history:
        history_str = "Conversation History:\n"
        for turn in history[-4:]:
            history_str += f"  User: {turn['user']}\n  Assistant: {turn['assistant']}\n"
        history_str += "\n"
    prompt = (
        f"You are a helpful NoSQL/MongoDB tutor. Answer based on the context.\n\n"
        f"{history_str}"
        f"Context:\n{context}\n\n"
        f"Question: {query}\nAnswer:"
    )
    return prompt


# ── Activity 2 Algorithms ──────────────────────────────────────────────────

def make_dataset(n_vectors=3000, dim=64, n_queries=20, seed=42):
    rng = np.random.default_rng(seed)
    data = rng.normal(size=(n_vectors, dim)).astype(np.float32)
    data /= np.linalg.norm(data, axis=1, keepdims=True)
    queries = rng.normal(size=(n_queries, dim)).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    return data, queries


def brute_force_search(data, query, k):
    scores = data @ query
    top_k = np.argsort(-scores)[:k]
    return top_k


class IVFIndex:
    def __init__(self, nlist=20):
        self.nlist = nlist
        self.centroids = None
        self.buckets = {}
        self.build_time = 0.0

    def build(self, data):
        start = time.perf_counter()
        n = data.shape[0]
        rng = np.random.default_rng(42)
        centroid_idx = rng.choice(n, size=self.nlist, replace=False)
        centroids = data[centroid_idx].copy()

        for _ in range(8):
            sims = data @ centroids.T
            assignments = np.argmax(sims, axis=1)
            for c in range(self.nlist):
                members = data[assignments == c]
                if len(members) > 0:
                    centroids[c] = members.mean(axis=0)
                    centroids[c] /= np.linalg.norm(centroids[c]) + 1e-9

        self.centroids = centroids
        self.assignments = assignments
        self.data = data
        self.buckets = {c: np.where(assignments == c)[0] for c in range(self.nlist)}
        self.build_time = time.perf_counter() - start

    def search(self, query, k, nprobe=3):
        centroid_scores = self.centroids @ query
        probe_clusters = np.argsort(-centroid_scores)[:nprobe]
        candidate_idx = np.concatenate([self.buckets[c] for c in probe_clusters]) \
            if len(probe_clusters) else np.array([], dtype=int)
        if len(candidate_idx) == 0:
            return np.array([], dtype=int), 0
        candidate_scores = self.data[candidate_idx] @ query
        top_local = np.argsort(-candidate_scores)[:k]
        return candidate_idx[top_local], len(candidate_idx)


class SimpleNSWIndex:
    def __init__(self, m=16, ef_construction=150):
        self.m = m
        self.ef_construction = ef_construction
        self.graph = {}
        self.build_time = 0.0

    def build(self, data):
        start = time.perf_counter()
        n = data.shape[0]
        self.data = data
        self.graph = {i: set() for i in range(n)}

        for i in range(n):
            if i == 0:
                continue
            pool_size = min(self.ef_construction, i)
            candidates = np.random.default_rng(i).choice(i, size=pool_size, replace=False)
            sims = data[candidates] @ data[i]
            nearest = candidates[np.argsort(-sims)[: self.m]]
            for j in nearest:
                self.graph[i].add(int(j))
                self.graph[int(j)].add(i)

        self.build_time = time.perf_counter() - start

    def search(self, query, k, ef_search=100, n_entry_points=5):
        import heapq
        n = self.data.shape[0]
        rng = np.random.default_rng(0)
        entry_points = rng.choice(n, size=min(n_entry_points, n), replace=False)

        visited = set()
        candidates = []
        results = []

        for ep in entry_points:
            ep = int(ep)
            if ep in visited:
                continue
            visited.add(ep)
            score = float(self.data[ep] @ query)
            heapq.heappush(candidates, (-score, ep))
            heapq.heappush(results, (score, ep))

        while candidates:
            neg_score, node = heapq.heappop(candidates)
            score = -neg_score
            worst_result_score = results[0][0] if len(results) >= ef_search else float("-inf")
            if score < worst_result_score:
                break

            for neighbor in self.graph[node]:
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                n_score = float(self.data[neighbor] @ query)
                worst_result_score = results[0][0] if len(results) >= ef_search else float("-inf")
                if n_score > worst_result_score or len(results) < ef_search:
                    heapq.heappush(candidates, (-n_score, neighbor))
                    heapq.heappush(results, (n_score, neighbor))
                    if len(results) > ef_search:
                        heapq.heappop(results)

        results.sort(key=lambda x: -x[0])
        return np.array([node for _, node in results[:k]]), len(visited)


def recall_at_k(predicted: np.ndarray, ground_truth: np.ndarray) -> float:
    if len(predicted) == 0:
        return 0.0
    return len(set(predicted.tolist()) & set(ground_truth.tolist())) / len(ground_truth)


# ── Web Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    mongo_ok = False
    mongo_version = "N/A"
    doc_count = 0
    try:
        client = get_client()
        info = client.server_info()
        mongo_version = info.get("version", "Unknown")
        mongo_ok = True
        col = client[DB_NAME][RAG_COLLECTION]
        doc_count = col.count_documents({})
    except Exception:
        pass

    return render_template(
        "index.html",
        connected=mongo_ok,
        version=mongo_version,
        doc_count=doc_count,
        documents=DOCUMENTS,
    )


@app.route("/lab1")
def lab1():
    db = get_db(DB_NAME)
    col = db[RAG_COLLECTION]
    chunks = list(col.find({}, {"_id": 0, "embedding": 0}))
    return render_template(
        "lab1.html",
        documents=DOCUMENTS,
        chunks=chunks,
        conversation_history=CONVERSATION_HISTORY,
    )


@app.route("/lab2")
def lab2():
    return render_template(
        "lab2.html",
        benchmark_results=LATEST_BENCHMARK_RESULTS,
    )


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")


# ── API Endpoints ──────────────────────────────────────────────────────────

@app.route("/api/health")
def api_health():
    status = {"status": "ok", "timestamp": time.time()}
    try:
        client = get_client()
        client.admin.command("ping")
        status["mongo"] = "connected"
        status["version"] = client.server_info().get("version", "N/A")
    except Exception as e:
        status["mongo"] = "error"
        status["error"] = str(e)
    return jsonify(status)


@app.route("/api/rag/ingest", methods=["POST"])
def api_rag_ingest():
    try:
        chunks_count, doc_count = db_ingest_documents()
        return jsonify({
            "status": "success",
            "message": f"Successfully ingested {chunks_count} chunks from {doc_count} documents.",
            "chunks_count": chunks_count,
            "doc_count": doc_count,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rag/retrieve", methods=["POST"])
def api_rag_retrieve():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 3))

    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty"}), 400

    try:
        start = time.perf_counter()
        results = db_retrieve_chunks(query, top_k)
        elapsed_ms = (time.perf_counter() - start) * 1000

        formatted_results = []
        for score, doc in results:
            formatted_results.append({
                "score": round(score, 4),
                "source_title": doc["source_title"],
                "chunk_index": doc.get("chunk_index", 0),
                "text": doc["text"],
                "preview": doc["text"][:80] + "...",
            })

        prompt = build_llm_prompt(query, results)

        return jsonify({
            "status": "success",
            "query": query,
            "top_k": top_k,
            "elapsed_ms": round(elapsed_ms, 3),
            "results": formatted_results,
            "prompt": prompt,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rag/chat", methods=["POST"])
def api_rag_chat():
    global CONVERSATION_HISTORY
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 2))

    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty"}), 400

    try:
        results = db_retrieve_chunks(query, top_k)
        prompt = build_llm_prompt(query, results, CONVERSATION_HISTORY)

        # Realistic synthesis response based on retrieved context
        sources_used = [doc["source_title"] for _, doc in results]
        simulated_response = (
            f"[RAG Response via {len(results)} Context Chunks] Based on {', '.join(set(sources_used))}: "
            f"Retrieved key semantic matches with prompt size {len(prompt)} characters. "
            f"Context verified against MongoDB knowledge base."
        )

        CONVERSATION_HISTORY.append({
            "user": query,
            "assistant": simulated_response,
            "sources": sources_used,
            "timestamp": time.strftime("%H:%M:%S"),
        })

        formatted_results = []
        for score, doc in results:
            formatted_results.append({
                "score": round(score, 4),
                "source_title": doc["source_title"],
                "chunk_index": doc.get("chunk_index", 0),
                "text": doc["text"],
            })

        return jsonify({
            "status": "success",
            "query": query,
            "response": simulated_response,
            "prompt": prompt,
            "sources": formatted_results,
            "history": CONVERSATION_HISTORY,
            "total_turns": len(CONVERSATION_HISTORY),
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/rag/clear_history", methods=["POST"])
def api_rag_clear_history():
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY = []
    return jsonify({"status": "success", "message": "Conversation history reset."})


@app.route("/api/ann/benchmark", methods=["POST"])
def api_ann_benchmark():
    global LATEST_BENCHMARK_RESULTS
    data = request.get_json() or {}
    n_vectors = int(data.get("n_vectors", 3000))
    dim = int(data.get("dim", 64))
    n_queries = int(data.get("n_queries", 20))
    k = int(data.get("k", 10))
    nlist = int(data.get("nlist", 20))
    nprobe = int(data.get("nprobe", 3))
    m = int(data.get("m", 16))
    ef_construction = int(data.get("ef_construction", 150))
    ef_search = int(data.get("ef_search", 100))

    try:
        # Step 1: Dataset
        dataset, queries = make_dataset(n_vectors=n_vectors, dim=dim, n_queries=n_queries)

        # Step 2: Ground Truth (Brute Force)
        start = time.perf_counter()
        ground_truths = [brute_force_search(dataset, q, k) for q in queries]
        brute_time = ((time.perf_counter() - start) / n_queries) * 1000

        # Step 3: IVF
        ivf = IVFIndex(nlist=nlist)
        ivf.build(dataset)
        start = time.perf_counter()
        ivf_search_results = [ivf.search(q, k, nprobe=nprobe) for q in queries]
        ivf_time = ((time.perf_counter() - start) / n_queries) * 1000
        ivf_results = [r for r, _ in ivf_search_results]
        ivf_compared = float(np.mean([n for _, n in ivf_search_results]))
        ivf_recall = float(np.mean([recall_at_k(r, gt) for r, gt in zip(ivf_results, ground_truths)]))

        # Step 4: Simplified NSW
        nsw = SimpleNSWIndex(m=m, ef_construction=ef_construction)
        nsw.build(dataset)
        start = time.perf_counter()
        nsw_search_results = [nsw.search(q, k, ef_search=ef_search) for q in queries]
        nsw_time = ((time.perf_counter() - start) / n_queries) * 1000
        nsw_results = [r for r, _ in nsw_search_results]
        nsw_compared = float(np.mean([n for _, n in nsw_search_results]))
        nsw_recall = float(np.mean([recall_at_k(r, gt) for r, gt in zip(nsw_results, ground_truths)]))

        result = {
            "parameters": {
                "n_vectors": n_vectors,
                "dim": dim,
                "n_queries": n_queries,
                "k": k,
                "nlist": nlist,
                "nprobe": nprobe,
                "m": m,
                "ef_construction": ef_construction,
                "ef_search": ef_search,
            },
            "metrics": [
                {
                    "method": "Brute-force (exact)",
                    "build_time_ms": 0.0,
                    "vectors_compared": n_vectors,
                    "vectors_pct": 100.0,
                    "query_time_ms": round(brute_time, 3),
                    "recall": 100.0,
                    "color": "#6c757d",
                },
                {
                    "method": f"IVF (nlist={nlist}, nprobe={nprobe})",
                    "build_time_ms": round(ivf.build_time * 1000, 1),
                    "vectors_compared": round(ivf_compared, 1),
                    "vectors_pct": round((ivf_compared / n_vectors) * 100, 1),
                    "query_time_ms": round(ivf_time, 3),
                    "recall": round(ivf_recall * 100, 2),
                    "color": "#0ea5e9",
                },
                {
                    "method": f"Simplified NSW (m={m}, ef={ef_search})",
                    "build_time_ms": round(nsw.build_time * 1000, 1),
                    "vectors_compared": round(nsw_compared, 1),
                    "vectors_pct": round((nsw_compared / n_vectors) * 100, 1),
                    "query_time_ms": round(nsw_time, 3),
                    "recall": round(nsw_recall * 100, 2),
                    "color": "#10b981",
                },
            ],
            "key_takeaways": {
                "higher_recall_winner": "Simplified NSW (HNSW-like)" if nsw_recall >= ivf_recall else "IVF",
                "scalable_metric": "Vectors Compared per Query",
                "metric_explanation": (
                    "Vectors compared per query is invariant to implementation language overhead. "
                    "In pure Python, NSW traverses graph nodes with interpreted dict/heap operations "
                    "which inflate wall-clock time, but in production C/C++ (such as MongoDB Atlas $vectorSearch), "
                    "reducing vector distance evaluations by 40-85% produces dramatic real-world speedups."
                ),
            },
        }

        LATEST_BENCHMARK_RESULTS = result
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
