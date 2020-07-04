import datetime as dt

import airflow
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(1),# dt.datetime(2020, 6, 25),
    'concurrency': 1,
    'retries': 0,
    # 'schedule_interval':'@once'
    'schedule_interval':'@daily'
}

# docker-compose run --rm webserver airflow variables --import /usr/local/airflow/dags/config/example_variables.json

dag_config = Variable.get("variables_config", deserialize_json=True)

task = dag_config["task"]
raw_invoice_path = dag_config["raw_invoice_path"]
csv_store_location = dag_config["csv_store_location"]

def change_dir(path):
    os.chdir(path)
    print(os.getcwd())

with DAG('abinbev_invoice_extraction_pipeline',
         default_args=default_args
         ) as dag:
    ### Join the paths according to docker env
    raw_invoice_path = os.path.join("/usr/local/airflow",raw_invoice_path)
    csv_store_location = os.path.join("/usr/local/airflow",csv_store_location)

    templated_command_api = """
    python /usr/local/airflow/dags/round2_api.py 
    """
    
    # python run_job.py --task batch --source_path ../Round\ 2 --csv_path ../csv_outputs_v2.0

    templated_command_runjob = """
    python /usr/local/airflow/dags/run_job.py --task={{params.task}} --source_path="{{params.raw_invoice_path}}" --csv_path="{{params.csv_store_location}}"
    """
    templated_command_mongodb = """
    python /usr/local/airflow/dags/mongodb_upload.py --path={{params.csv_store_location}}
    """
    ## we don't use the -u, -g, option for mongodb script, its not much of a difference,
    ## will just use the default

    pwd = BashOperator(task_id='pwd',depends_on_past=False,bash_command='pwd')

    # run_api = BashOperator(task_id='run_api',
    #                     depends_on_past=False,
    #                     bash_command=templated_command_api,
    #                     dag=dag)

    run_batch_extraction = BashOperator(task_id='run_batch_extraction',
                        depends_on_past=False,
                        bash_command=templated_command_runjob,
                        params={'task': task,
                        'raw_invoice_path':raw_invoice_path,
                        'csv_store_location':csv_store_location},
                        dag=dag)
    
    mongodb_integration = BashOperator(task_id='mongodb_integration',
                        depends_on_past=True,
                        bash_command=templated_command_mongodb,
                        params={'task': task,
                        'raw_invoice_path':raw_invoice_path,
                        'csv_store_location':csv_store_location},
                        dag=dag)

# pwd >> [run_api, run_batch_extraction]
# run_batch_extraction.set_downstream(mongodb_integration)

pwd >> run_batch_extraction >> mongodb_integration