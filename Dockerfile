# ─── NoSQL Lab 13: Production Deployment, Orchestration & Cloud Provisioning ───
# Author: M Gouthami (24BTRCL130)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl and OpenSSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./requirements.txt
COPY web/requirements.txt ./web_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web_requirements.txt

# Copy lab manifests, configs, and scripts
COPY config/                     ./config/
COPY k8s/                        ./k8s/
COPY docker-compose-production.yml ./
COPY keyfile                     ./
COPY lab_01_deploy_prod.sh       ./
COPY lab_01_deploy_prod.py       ./
COPY lab_02_k8s_statefulset.py   ./
COPY main.tf                     ./

# Copy web application
COPY web/                        ./web/

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    MONGO_URI=mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin \
    PORT=5000

EXPOSE 5000

CMD ["python", "web/app.py"]
