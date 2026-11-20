# =============================================================================
# Dockerfile: NoSQL Lab 9 - MongoDB Write Concerns & Network Partition
# Repository: https://hub.docker.com/r/gouthudocker/nosql-lab-9
# Student:    M Gouthami (24BTRCL130)
# =============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PYTHONPATH="/app:/app/web_platform/backend" \
    MONGO_URI="mongodb://mongo:27017/?replicaSet=rs0&serverSelectionTimeoutMS=5000" \
    REPLICA_SET_URI="mongodb://mongo-rs0-1:27017,mongo-rs0-2:27018,mongo-rs0-3:27019/?replicaSet=rs0&serverSelectionTimeoutMS=3000"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency requirements
COPY web_platform/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy root activity files & config
COPY config /app/config
COPY lab_01_write_concern_latency.py /app/lab_01_write_concern_latency.py
COPY lab_02_simulate_partition.sh /app/lab_02_simulate_partition.sh
COPY Lab9_Report.pdf /app/Lab9_Report.pdf
COPY Lab9_Report.docx /app/Lab9_Report.docx
COPY Lab9_Report.html /app/Lab9_Report.html
COPY Write-Concern-TradeOffs.jpg /app/Write-Concern-TradeOffs.jpg
COPY README.md /app/README.md

# Copy application directories & activity suites
COPY Activity_9_1 /app/Activity_9_1
COPY Activity_9_1_TryItYourself /app/Activity_9_1_TryItYourself
COPY Activity_9_2 /app/Activity_9_2
COPY Activity_9_2_TryItYourself /app/Activity_9_2_TryItYourself
COPY web_platform /app/web_platform
COPY Write-Concern-TradeOffs.jpg /app/web_platform/frontend/Write-Concern-TradeOffs.jpg

# Expose web server port
EXPOSE 5000

# Start Flask application entrypoint
WORKDIR /app/web_platform/backend
CMD ["python", "app.py"]
