# ── NoSQL Lab 12: MongoDB Security, RBAC & TLS Encryption ─────────────
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including OpenSSL
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./requirements.txt
COPY web/requirements.txt ./web_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r web_requirements.txt

# Copy configuration and certificates
COPY config/                 ./config/
COPY tls/                    ./tls/

# Copy lab execution scripts
COPY generate_tls_certs.py   ./
COPY lab_01_rbac_setup.py    ./
COPY lab_01_rbac_setup.sh    ./
COPY lab_02_tls_setup.py     ./
COPY lab_02_tls_setup.sh     ./
COPY rbac_field_redaction.py ./
COPY create_docx_report.py   ./

# Copy documentation and diagrams
COPY ["Threat Modelling.jpg", "./"]
COPY Lab_12_Report.docx      ./
COPY Lab_12_Report.pdf       ./
COPY NoSQL_Lab12_Submission.pdf ./

# Copy web application
COPY web/                    ./web/

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=web/app.py \
    MONGO_URI=mongodb://mongo:27017/ \
    PORT=5000

EXPOSE 5000

CMD ["python", "web/app.py"]
