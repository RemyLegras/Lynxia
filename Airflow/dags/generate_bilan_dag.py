import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Add the scripts directory to the path so we can import the generation function
sys.path.append(os.path.join(os.environ['AIRFLOW_HOME'], 'scripts'))

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from generate_random_bilan_v2 import generate_random_bilan_v2

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_generate_bilan():
    OUTPUT_DIR = "/tmp"
    output_path = generate_random_bilan_v2(OUTPUT_DIR_JSON=OUTPUT_DIR)
    
    # Upload to MinIO
    if output_path and os.path.exists(output_path):
        hook = S3Hook(aws_conn_id="minio_conn")
        filename = os.path.basename(output_path)
        hook.load_file(
            filename=output_path,
            key=filename,
            bucket_name="raw",
            replace=True
        )
        print(f"Bilan {filename} uploadé vers MinIO 'raw'")
        os.remove(output_path)

with DAG(
    'generate_random_bilan',
    default_args=default_args,
    description='Génère des bilans aléatoires quotidiennement',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['generation', 'pdf'],
) as dag:

    generate_task = PythonOperator(
        task_id='generate_bilan',
        python_callable=run_generate_bilan,
    )

    generate_task
