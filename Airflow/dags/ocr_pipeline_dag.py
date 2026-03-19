import os
import sys
import json
import shutil
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException

sys.path.append(os.path.join(os.environ["AIRFLOW_HOME"], "scripts"))

from loguru import logger
from ocr.analyzer import OCRAnalyzer
from ocr.llm_extractor import extract_with_llm
from ocr.utils.sirene_api import fetch_sirene_info
from data_augmentation import apply_data_augmentation
import pymysql

# Configure Loguru to write to a file in the data dir
logger.add("/opt/airflow/data/pipeline.log", rotation="10 MB")

INPUT_DIR_BRONZE = "/opt/airflow/data/bronze"
WORK_DIR_SILVER = "/opt/airflow/data/silver/work"
OUTPUT_DIR_SILVER = "/opt/airflow/data/silver/extracted"
OUTPUT_DIR_GOLD = "/opt/airflow/data/gold"

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
    os.makedirs(WORK_DIR_SILVER, exist_ok=True)
    files = [
        f for f in os.listdir(INPUT_DIR_BRONZE)
        if f.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))
    ]
    unprocessed = []
    for f in files:
        gold_name = os.path.splitext(f)[0] + "_gold.json"
        gold_path = os.path.join(OUTPUT_DIR_GOLD, gold_name)
        if not os.path.exists(gold_path):
            unprocessed.append(f)
    
    logger.info(f"Fichiers trouvés dans Bronze: {len(files)}, non traités: {len(unprocessed)}")
    
    if not unprocessed:
        logger.info("Tous les fichiers de la zone Bronze ont déjà été traités.")
        raise AirflowSkipException("Pas de nouveaux fichiers à traiter.")

    # On prend le plus ancien des non-traités pour garder un ordre chronologique
    target = sorted(unprocessed, key=lambda f: os.path.getmtime(os.path.join(INPUT_DIR_BRONZE, f)))[0]
    
    dest = os.path.join(WORK_DIR_SILVER, target)
    shutil.copy2(os.path.join(INPUT_DIR_BRONZE, target), dest)

    context["ti"].xcom_push(key="file_path", value=dest)
    context["ti"].xcom_push(key="file_name", value=target)
    
    return target

def data_augmentation_task(**context):
    file_path = context["ti"].xcom_pull(task_ids="upload_task", key="file_path")
    out_path = file_path.replace(".pdf", "_aug.png") if file_path.endswith(".pdf") else file_path.replace(".", "_aug.")
    final_path = apply_data_augmentation(file_path, out_path)
    context["ti"].xcom_push(key="aug_file_path", value=final_path)
    context["ti"].xcom_push(key="aug_file_name", value=os.path.basename(final_path))

def ocr_task(**context):
    analyzer = OCRAnalyzer()
    file_path = context["ti"].xcom_pull(task_ids="data_augmentation_task", key="aug_file_path")
    file_name = context["ti"].xcom_pull(task_ids="data_augmentation_task", key="aug_file_name")

    logger.info(f"Démarrage OCR sur {file_name}")
    result = analyzer.analyze(file_path, file_name, element_id=1)
    
    context["ti"].xcom_push(key="ocr_result", value=result)

def extraction_task(**context):
    result = context["ti"].xcom_pull(task_ids="ocr_task", key="ocr_result")
    raw_text = result.get("raw_text", "")
    
    logger.info("Tentative d'extraction intelligente via LLM Ollama...")
    llm_data = extract_with_llm(raw_text) if raw_text else None
    
    if llm_data and isinstance(llm_data, dict) and llm_data.get("document_type"):
        logger.info(f"Extraction LLM réussie: {llm_data.get('document_type')}")
        # Merge dynamique : on prend tout ce que le LLM a trouvé, en gardant les champs de base du result
        extracted = result.copy()
        extracted.update(llm_data)
        # S'assurer que les champs prioritaires du result (comme justificatif_url) restent s'ils sont là
        if "justificatif_url" in result:
            extracted["justificatif_url"] = result["justificatif_url"]
    else:
        logger.info("Fallback sur les données du routeur/processeur classique.")
        extracted = result.copy()


    context["ti"].xcom_push(key="extracted_data", value=extracted)

def validation_task(**context):
    extracted = context["ti"].xcom_pull(task_ids="extraction_task", key="extracted_data")

    logger.info("Début de la validation métier et mathématique...")

    # Math Check (Seulement pour les factures)
    math_valid = True
    doc_type = extracted.get("document_type", "").lower()
    
    if doc_type == "facture":
        tva = float(extracted.get("montant_tva") or 0)
        ht = float(extracted.get("montant_ht") or 0)
        ttc = float(extracted.get("montant_ttc") or 0)
        math_valid = abs((ht + tva) - ttc) < 0.1 if ttc > 0 else False
        if not math_valid:
            logger.warning(f"Incohérence mathématique Facture: HT({ht}) + TVA({tva}) != TTC({ttc})")

    checks = {
        "has_document_type": doc_type not in (None, "", "autre"),
        "has_amount": True if doc_type != "facture" else (float(extracted.get("montant_ttc", 0)) > 0),
        "has_status": extracted.get("statut") is not None,
        "cross_check_ok": True,
        "sirene_valid": True,
        "math_valid": math_valid
    }

    # API SIRENE Check
    siret = extracted.get("siret")
    if siret and siret != "N/A":
        logger.info(f"Vérification SIRENE pour le SIRET: {siret}")
        sirene_info = fetch_sirene_info(siret)
        if sirene_info["is_valid"]:
            logger.info(f"SIRENE OK: {sirene_info['company_name']}")
            extracted["company_name"] = sirene_info["company_name"]
            extracted["address"] = sirene_info["address"]
        else:
            logger.warning("SIRET invalide ou introuvable sur SIRENE.")
            checks["sirene_valid"] = False

    # Cross-Check SIRET & Montant
    if extracted.get("document_type", "").lower() == "facture" and siret and siret != "N/A":
        try:
            logger.info("Cross-check Facture VS Devis dans la BDD...")
            conn = pymysql.connect(
                host="mysql",
                user="root",
                password=os.getenv("MYSQL_ROOT_PASSWORD", "root"),
                database="documents_db",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT curated_data FROM documents WHERE document_type = 'devis' OR document_type = 'Devis'")
                devis_list = cursor.fetchall()
                found_match = False
                for d in devis_list:
                    data = d['curated_data']
                    if isinstance(data, str):
                        import json
                        data = json.loads(data)
                    if data.get("siret") == siret:
                        devis_ttc = float(data.get("montant_ttc", 0))
                        if devis_ttc > 0:
                            diff = abs(ttc - devis_ttc) / devis_ttc
                            if diff > 0.01:
                                checks["cross_check_ok"] = False
                                logger.warning(f"Montant divergeant avec le devis ({ttc} vs {devis_ttc})")
                            else:
                                logger.info("Facture <-> Devis vérifié avec succès.")
                        found_match = True
                        break
                if not found_match:
                    logger.warning("Aucun devis correspondant au SIRET de la facture.")
                    checks["cross_check_ok"] = False
            conn.close()
        except Exception as e:
            logger.error(f"Erreur DB Cross-Check: {e}")
            checks["cross_check_ok"] = False

    extracted["validation"] = checks
    extracted["is_valid"] = all(checks.values())
    if not extracted["is_valid"]:
        extracted["statut"] = "Incohérent"
        logger.warning(f"Validation échouée. Raisons: {checks}")
    else:
        logger.info("Validation complète réussie.")

    context["ti"].xcom_push(key="validated_data", value=extracted)

def save_to_gold_task(**context):
    os.makedirs(OUTPUT_DIR_SILVER, exist_ok=True)
    os.makedirs(OUTPUT_DIR_GOLD, exist_ok=True)

    validated = context["ti"].xcom_pull(task_ids="validation_task", key="validated_data")
    file_name = context["ti"].xcom_pull(task_ids="upload_task", key="file_name")

    silver_name = os.path.splitext(file_name)[0] + "_silver.json"
    silver_path = os.path.join(OUTPUT_DIR_SILVER, silver_name)
    with open(silver_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)

    gold_name = os.path.splitext(file_name)[0] + "_gold.json"
    gold_path = os.path.join(OUTPUT_DIR_GOLD, gold_name)
    with open(gold_path, "w", encoding="utf-8") as f:
        json.dump(validated, f, ensure_ascii=False, indent=2)

    logger.info(f"Résultat sauvegardé en Silver ({silver_path}) et Gold ({gold_path})")

with DAG(
        "ocr_pipeline",
        default_args=default_args,
        description="Pipeline OCR robuste : upload > ocr > extraction > validation > save",
        schedule_interval="* * * * *",
        catchup=False,
        tags=["ocr", "pipeline"],
) as dag:

    upload = PythonOperator(
        task_id="upload_task",
        python_callable=upload_task,
    )

    augment = PythonOperator(
        task_id="data_augmentation_task",
        python_callable=data_augmentation_task,
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
        task_id="save_to_gold_task",
        python_callable=save_to_gold_task,
    )

    upload >> augment >> ocr >> extract >> validate >> save