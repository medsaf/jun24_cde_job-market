from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import random
from FranceTravailDataExtractor2 import *


with DAG(
    dag_id='Extract_and_load_data',
    schedule_interval=None,
    start_date=days_ago(0)
) as my_dag:

    load_and_extract = PythonOperator(
        task_id='python_task',
        python_callable=load_and_extract
    )
    my_task 
