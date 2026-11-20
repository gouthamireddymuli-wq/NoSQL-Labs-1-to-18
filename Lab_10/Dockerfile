# ── Python 3.11 slim base ────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt          ./requirements.txt
COPY web/requirements.txt      ./web_requirements.txt
RUN pip install --no-cache-dir \
      -r requirements.txt \
      -r web_requirements.txt

# Copy project files
COPY config/                        ./config/
COPY lab_01_bank_transfer.py        ./
COPY lab_02_inventory_reservation.py ./
COPY multi_document_transaction.py  ./
COPY web/                           ./web/

# Environment
ENV MONGO_URI="mongodb://mongo:27017/?replicaSet=rs0"
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "/app/web/app.py"]
