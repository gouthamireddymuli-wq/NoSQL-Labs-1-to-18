# ── NoSQL Lab 14: Monitoring, Backup & Restore ──────────────────────────────
# Installs MongoDB Database Tools (mongodump/mongorestore) via direct .deb
# download — avoids the MongoDB apt repo SHA1 key rejection on Debian trixie.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS base

# MongoDB Database Tools version to install (debian12 / amd64 build)
ARG TOOLS_VERSION=100.9.4
ARG TOOLS_DEB=mongodb-database-tools-debian12-x86_64-${TOOLS_VERSION}.deb
ARG TOOLS_URL=https://fastdl.mongodb.org/tools/db/${TOOLS_DEB}

# Install tools + clean up in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates libcurl4 libssl3 \
    && curl -fsSL "${TOOLS_URL}" -o /tmp/db-tools.deb \
    && dpkg -i /tmp/db-tools.deb \
    && rm /tmp/db-tools.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config/        /app/config/
COPY web/           /app/web/
COPY lab_01_monitoring_dashboard.py /app/
COPY lab_02_backup_restore.py       /app/

# Persistent directories (logs & backups are written here at runtime)
RUN mkdir -p /app/logs /app/backups

# Environment
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    PORT=5000 \
    MONGO_URI="mongodb://admin:AdminPass123!@mongo-rs0-1:27017,mongo-rs0-2:27017,mongo-rs0-3:27017/admin?replicaSet=rs0&authSource=admin" \
    MONGO_URI_STANDALONE="mongodb://localhost:27017"

EXPOSE 5000

CMD ["python", "web/app.py"]
