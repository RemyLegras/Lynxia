import os
import sys
import json
import shutil
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append(os.path.join(os.environ["AIRFLOW_HOME"], "scripts"))

from ocr.analyzer import OCRAnalyzer

INPUT_DIR = "/opt/airflow/input_pdf"
WORK_DIR = "/opt/airflow/work_pdf"
OUTPUT_DIR = "/opt/airflow/output_json"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def upload_task(**context):
    os.makedirs(WORK_DIR, exist_ok=True)
    files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))
    ]
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé dans {INPUT_DIR}")

    latest = max(
        [os.path.join(INPUT_DIR, f) for f in files],
        key=os.path.getmtime
    )
    dest = os.path.join(WORK_DIR, os.path.basename(latest))
    shutil.copy2(latest, dest)

    context["ti"].xcom_push(key="file_path", value=dest)
    context["ti"].xcom_push(key="file_name", value=os.path.basename(dest))

def ocr_task(**context):
    analyzer = OCRAnalyzer()
    file_path = context["ti"].xcom_pull(task_ids="upload_task", key="file_path")
    file_name = context["ti"].xcom_pull(task_ids="upload_task", key="file_name")

    result = analyzer.analyze(file_path, file_name, element_id=1)
    context["ti"].xcom_push(key="ocr_result", value=result)

def extraction_task(**context):
    result = context["ti"].xcom_pull(task_ids="ocr_task", key="ocr_result")

    extracted = {
        "document_type": result.get("document_type"),
        "description": result.get("description"),
        "siret": result.get("siret"),
        "tva": result.get("tva"),
        "montant_ht": result.get("montant_ht"),
        "montant_tva": result.get("montant_tva"),
        "montant_ttc": result.get("montant_ttc"),
        "date_validation": result.get("date_validation"),
        "devise": result.get("devise"),
        "statut": result.get("statut"),
        "justificatif_url": result.get("justificatif_url"),
    }

    context["ti"].xcom_push(key="extracted_data", value=extracted)

def validation_task(**context):
    extracted = context["ti"].xcom_pull(task_ids="extraction_task", key="extracted_data")

    checks = {
        "has_document_type": extracted.get("document_type") not in (None, "", "autre"),
        "has_amount": extracted.get("montant_ttc", 0) > 0,
        "has_status": extracted.get("statut") is not None,
    }

    extracted["validation"] = checks
    extracted["is_valid"] = all(checks.values())

    context["ti"].xcom_push(key="validated_data", value=extracted)

def save_task(**context):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    validated = context["ti"].xcom_pull(task_ids="validation_task", key="validated_data")
    file_name = context["ti"].xcom_pull(task_ids="upload_task", key="file_name")

    output_name = os.path.splitext(file_name)[0] + ".json"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)

    print(f"Résultat sauvegardé : {output_path}")

with DAG(
        "ocr_pipeline",
        default_args=default_args,
        description="Pipeline OCR simple : upload > ocr > extraction > validation > save",
        schedule_interval=None,
        catchup=False,
        tags=["ocr", "pipeline"],
) as dag:

    upload = PythonOperator(
        task_id="upload_task",
        python_callable=upload_task,
    )

    ocr = PythonOperator(
        task_id="ocr_task",
        python_callable=ocr_task,
    )

    extract = PythonOperator(
        task_id="extraction_task",
        python_callable=extraction_task,
    )

    validate = PythonOperator(
        task_id="validation_task",
        python_callable=validation_task,
    )

    save = PythonOperator(
        task_id="save_task",
        python_callable=save_task,
    )

    upload >> ocr >> extract >> validate >> save