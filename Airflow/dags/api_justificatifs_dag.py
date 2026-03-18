import sys
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append(os.path.join(os.environ['AIRFLOW_HOME'], 'scripts'))

from api_justificatifs import fetch_Api_justificatifs

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_fetch():
    output_dir = "/opt/airflow/output_pdf"
    paths = fetch_Api_justificatifs(output_dir=output_dir)
    print(f"{len(paths)} fichiers téléchargés")

with DAG(
    'fetch_Api_justificatifs',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    generate_task = PythonOperator(
        task_id='fetch_justificatifs',
        python_callable=run_fetch,
    )

    generate_task