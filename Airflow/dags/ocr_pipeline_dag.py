import os
import sys
import json
import tempfile
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable

sys.path.append(os.path.join(os.environ["AIRFLOW_HOME"], "scripts"))

from loguru import logger
from ocr.analyzer import OCRAnalyzer
from ocr.llm_extractor import extract_with_llm
import pymysql

# Loguru configuration
logger.add("/opt/airflow/data/pipeline.log", rotation="10 MB")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def get_db_connection():
    return pymysql.connect(
        host="mysql",
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database=os.getenv("MYSQL_DATABASE", "documents_db"),
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_raw_files(**context):
    """
    Task 1: List files in the RAW zone.
    """
    hook = S3Hook(aws_conn_id="minio_conn")
    bucket = "raw"
    files = hook.list_keys(bucket_name=bucket)
    if not files:
        logger.info("Aucun fichier neuf dans RAW.")
        return []
    logger.info(f"Fichiers RAW détectés: {files}")
    return files

def ocr_and_clean_task(**context):
    """
    Task 2: Download from RAW, run OCR, save text to CLEAN.
    """
    ti = context["ti"]
    files = ti.xcom_pull(task_ids="fetch_raw_task")
    if not files: return

    target_file = files[0]
    hook = S3Hook(aws_conn_id="minio_conn")
    engine = Variable.get("ocr_engine", default_var="tesseract")
    
    local_path = hook.download_file(target_file, bucket_name="raw", local_path="/tmp")
    analyzer = OCRAnalyzer(engine=engine)
    result = analyzer.analyze(local_path, target_file, element_id=1)
    
    # Save the full OCR JSON result to the CLEAN zone
    clean_filename = f"{os.path.splitext(target_file)[0]}.json"
    hook.load_string(json.dumps(result, indent=2), key=clean_filename, bucket_name="clean", replace=True)
    
    # Store partial results for the next task
    ti.xcom_push(key="ocr_result", value=result)
    ti.xcom_push(key="current_file", value=target_file)
    ti.xcom_push(key="clean_file", value=clean_filename)
    
    if os.path.exists(local_path):
        os.remove(local_path)

def extract_and_curate_task(**context):
    """
    Task 3: Read from CLEAN, extract via LLM, save to CURATED.
    """
    ti = context["ti"]
    ocr_result = ti.xcom_pull(task_ids="ocr_clean_task", key="ocr_result")
    clean_file = ti.xcom_pull(task_ids="ocr_clean_task", key="clean_file")
    original_file = ti.xcom_pull(task_ids="ocr_clean_task", key="current_file")
    
    if not ocr_result: return

    hook = S3Hook(aws_conn_id="minio_conn")
    raw_text = hook.read_key(clean_file, bucket_name="clean")
    
    logger.info("Extraction LLM en cours...")
    extracted_data = extract_with_llm(raw_text)
    final_data = {**ocr_result, **extracted_data, "processed_at": str(datetime.now())}
    
    # Save finalized JSON to CURATED zone
    curated_filename = f"{os.path.splitext(original_file)[0]}.json"
    hook.load_string(json.dumps(final_data, indent=2), key=curated_filename, bucket_name="curated", replace=True)
    
    ti.xcom_push(key="final_result", value=final_data)
    ti.xcom_push(key="curated_file", value=curated_filename)

def finalize_db_task(**context):
    """
    Task 4: Update DB and potentially move/tag the RAW file.
    """
    ti = context["ti"]
    data = ti.xcom_pull(task_ids="extract_curate_task", key="final_result")
    filename = ti.xcom_pull(task_ids="ocr_clean_task", key="current_file")
    
    if not data: return

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Update the document status in DB (assuming the record already exists from the API upload)
            sql = """
                UPDATE documents 
                SET status = %s, 
                    document_type = %s, 
                    curated_data = %s
                WHERE raw_path = %s
            """
            cursor.execute(sql, (
                data["statut"],
                data["document_type"],
                json.dumps(data),
                filename
            ))
        conn.commit()
        logger.info(f"DB mise à jour pour {filename} (Zone Curated OK)")
    finally:
        conn.close()

with DAG(
    "datalake_pipeline_zones",
    default_args=default_args,
    description="Pipeline Data Lake: Raw -> Clean -> Curated",
    schedule_interval=timedelta(minutes=1),
    catchup=False,
) as dag:

    fetch_raw = PythonOperator(task_id="fetch_raw_task", python_callable=fetch_raw_files)
    ocr_clean = PythonOperator(task_id="ocr_clean_task", python_callable=ocr_and_clean_task)
    extract_curate = PythonOperator(task_id="extract_curate_task", python_callable=extract_and_curate_task)
    finalize_db = PythonOperator(task_id="finalize_db_task", python_callable=finalize_db_task)

    fetch_raw >> ocr_clean >> extract_curate >> finalize_db