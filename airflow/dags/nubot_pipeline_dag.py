from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys

#  Add backend code path for Airflow (very important)
sys.path.append('/opt/airflow/services/backend/src/dataflow')

from scraper import run_scraper
from chunk_data import run_chunking

default_args = {
    'owner': 'arjun',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='nubot_data_pipeline',
    default_args=default_args,
    schedule_interval=None,  # Run manually for now
    catchup=False
) as dag:

    task_scrape = PythonOperator(
        task_id='scrape_website',
        python_callable=run_scraper
    )

    task_chunk = PythonOperator(
        task_id='chunk_scraped_data',
        python_callable=run_chunking
    )

    task_scrape >> task_chunk  # run chunking only after scraping
