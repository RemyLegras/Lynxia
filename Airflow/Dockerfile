FROM apache/airflow:2.10.5

USER root

# Install system dependencies if needed (e.g., for Pillow or PyMuPDF)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create datalake directories
RUN mkdir -p /opt/airflow/data/bronze /opt/airflow/data/silver /opt/airflow/data/gold

ENV PYTHONPATH="/opt/airflow/scripts:${PYTHONPATH}"
# Copy scripts
COPY scripts/ /opt/airflow/scripts/
