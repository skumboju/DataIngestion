
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from ingestion.core.config_loader import load_config_for_dag


TRANSFORM_ROOT = "/opt/airflow/transform"
DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1
}

def discover_sql_dags():
    if DAG is None:
        return []

    print("🚀 Starting DAG discovery...")
    dags = []
    for dag_folder in os.listdir(TRANSFORM_ROOT):
        dag_path = os.path.join(TRANSFORM_ROOT, dag_folder)
        if not os.path.isdir(dag_path):
            continue

        print(f"✅ Found DAG folder: {dag_folder}")
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
        print(f"🧩 SQL Files in {dag_folder}: {sql_files}")

        tasks = {}

        for sql_file in sql_files:
            task_id = sql_file.replace('.sql', '')
            file_path = os.path.join(dag_path, sql_file)

            task = DummyOperator(
                task_id=task_id,
                dag=dag
            )

            tasks[task_id] = task

        for dep in dependencies:
            after = dep["after"]
            before = dep["before"]
            if after in tasks and before in tasks:
                tasks[after] >> tasks[before]

        dags.append(dag)
        print(f"🔁 Registered DAG: {dag_id} with {len(tasks)} tasks")

    print(f"✅ Total DAGs registered: {len(dags)}")
    return dags

if DAG:
    print("👀 DAG registration starting...")

    discovered = discover_sql_dags()

    print(f"📦 Discovered {len(discovered)} DAGs")
    for dag in discovered:
        print(f"📌 Registering DAG: {dag.dag_id}")
        globals()[dag.dag_id] = dag

