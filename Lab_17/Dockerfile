# ── NoSQL Lab 17: RAG Pipeline & Vector Indexes (HNSW vs IVF) ──────────────
# Author: M Gouthami (24BTRCL130)
# Docker Hub: gouthudocker/nosql-lab17:latest
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

LABEL maintainer="M Gouthami <24BTRCL130>" \
      description="NoSQL Lab 17: Simple RAG Pipeline & HNSW vs IVF Vector Index Comparison"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY config/ /app/config/
COPY web/ /app/web/
COPY lab_01_rag_pipeline.py /app/
COPY lab_02_hnsw_vs_ivf.py /app/
COPY run_all.py /app/

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    PORT=5000 \
    MONGO_URI="mongodb://localhost:27017/" \
    MONGO_URI_STANDALONE="mongodb://host.docker.internal:27017/"

EXPOSE 5000

# Default execution starts the Flask Web Application
CMD ["python", "web/app.py"]
