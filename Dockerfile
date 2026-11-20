# ── NoSQL Lab 18: Comparative Capstone Lab & Analysis Report ───────────────
# Author: M Gouthami (24BTRCL130)
# Docker Hub: gouthudocker/nosql-lab18:latest
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

LABEL maintainer="M Gouthami <24BTRCL130>" \
      description="NoSQL Lab 18: Comparative Capstone - Fraud Detection Data Platform (MongoDB vs Cassandra vs Neo4j)"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY config/ /app/config/
COPY web/ /app/web/
COPY reports/ /app/reports/
COPY lab_01_comparative_capstone.py /app/
COPY lab_02_comparative_report.py /app/
COPY generate_pdf_direct.py /app/
COPY run_all.py /app/
COPY Lab_18_Report.pdf /app/
COPY NoSQL_Lab18_Submission.pdf /app/

# Environment defaults
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    PORT=5000 \
    MONGO_URI="mongodb://localhost:27017/" \
    MONGO_URI_STANDALONE="mongodb://host.docker.internal:27017/"

EXPOSE 5000

# Default execution starts the Flask Web Application
CMD ["python", "web/app.py"]
