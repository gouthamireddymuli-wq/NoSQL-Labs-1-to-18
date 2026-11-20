# ============================================================
#  NoSQL Lab 16 – Polyglot Persistence
#  Author : M Gouthami (24BTRCL130)
# ============================================================
FROM python:3.11-slim

LABEL maintainer="M Gouthami <24BTRCL130>" \
      description="NoSQL Lab 16: Polyglot Persistence – MongoDB / Cassandra / Neo4j modeling & hybrid query service"

WORKDIR /app

# Install system deps (none heavy needed for these labs)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Default env – override at run time:
#   docker run -e MONGO_URI=mongodb://host:27017/ ...
ENV MONGO_URI=mongodb://mongo:27017/ \
    PYTHONUNBUFFERED=1

# Entry point: run both labs sequentially
CMD ["sh", "-c", "echo '==============================' && echo ' Lab 16.1 – Polyglot Modeling' && echo '==============================' && python lab_01_polyglot_modeling.py && echo '' && echo '======================================' && echo ' Lab 16.2 – Hybrid Query Service' && echo '======================================' && python lab_02_hybrid_query_service.py"]
