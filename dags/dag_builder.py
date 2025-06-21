# dags/dag_builder.py

import os
from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from ingestion.transformers.sql_executor import execute_sql_with_jinja
    from ingestion.core.config_loader import load_config_for_dag
except ModuleNotFoundError:
    DAG = None

TRANSFORM_ROOT = "/opt/airflow/transform"
DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1
}

def discover_sql_dags():
    if DAG is None:
        return []

    dags = []
    for dag_folder in os.listdir(TRANSFORM_ROOT):
        dag_path = os.path.join(TRANSFORM_ROOT, dag_folder)
        if not os.path.isdir(dag_path):
            continue

        config = load_config_for_dag(dag_path) if load_config_for_dag else {}
        dependencies = config.get("dependencies", [])
        dag_id = dag_folder
        dag = DAG(
            dag_id=dag_id,
            default_args=DEFAULT_ARGS,
            schedule_interval=config.get('schedule', None),
            catchup=False
        )

        sql_files = sorted([
            f for f in os.listdir(dag_path)
            if f.endswith('.sql')
        ])

        tasks = {}

        for sql_file in sql_files:
            task_id = sql_file.replace('.sql', '')
            file_path = os.path.join(dag_path, sql_file)

            task = PythonOperator(
                task_id=task_id,
                python_callable=execute_sql_with_jinja,
                op_kwargs={"file_path": file_path, **config},
                dag=dag
            )

            tasks[task_id] = task

        for dep in dependencies:
            after = dep["after"]
            before = dep["before"]
            if after in tasks and before in tasks:
                tasks[after] >> tasks[before]

        globals()[dag_id] = dag
        dags.append(dag)

    return dags

if DAG:
    discover_sql_dags()
