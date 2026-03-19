import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add the scripts directory to the path so we can import the generation function
sys.path.append(os.path.join(os.environ['AIRFLOW_HOME'], 'scripts'))

from generate_random_devis_v1 import generate_random_devis

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_generate_devis():
    OUTPUT_DIR_JSON = "/opt/airflow/data/bronze"
    output_path = generate_random_devis(OUTPUT_DIR_JSON=OUTPUT_DIR_JSON)
    print(f"Devis généré avec succès à l'emplacement : {output_path}")

with DAG(
        'generate_random_devis',
        default_args=default_args,
        description='Génère des devis aléatoires quotidiennement',
        schedule_interval=timedelta(days=1),
        catchup=False,
        tags=['generation', 'pdf'],
) as dag:

    generate_task = PythonOperator(
        task_id='generate_bilan',
        python_callable=run_generate_devis,
    )

    generate_task