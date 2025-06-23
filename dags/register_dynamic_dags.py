import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dags.gen_dags import discover_sql_dags

for dag in discover_sql_dags():
    globals()[dag.dag_id] = dag
