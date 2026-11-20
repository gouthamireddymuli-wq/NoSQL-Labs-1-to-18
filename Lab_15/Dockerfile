# ── NoSQL Lab 15: Multi-Tenant API & Tenant Migration Strategies ────────────
# Author: M Gouthami (24BTRCL130)
# Docker Hub: gouthudocker/nosql-lab15:latest
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY config/ /app/config/
COPY web/ /app/web/
COPY lab_01_multitenant_api.py /app/
COPY lab_02_tenant_migration.py /app/

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    PORT=5000 \
    MONGO_URI="mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin" \
    MONGO_URI_STANDALONE="mongodb://admin:AdminPass123!@mongo-rs0-1:27017/?authSource=admin"

EXPOSE 5000

CMD ["python", "web/app.py"]
