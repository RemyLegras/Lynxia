FROM apache/airflow:2.10.5

USER root

# Install system dependencies if needed (e.g., for Pillow or PyMuPDF)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p /opt/airflow/output_pdf

# Copy scripts
COPY scripts/ /opt/airflow/scripts/
