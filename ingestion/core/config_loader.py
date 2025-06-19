import os
import yaml

def load_config_for_dag(dag_folder):
    config_path = os.path.join(dag_folder, "config.yaml")
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)