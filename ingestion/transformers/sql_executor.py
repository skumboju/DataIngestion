import os
from jinja2 import Template
from datetime import datetime

try:
    import snowflake.connector
    from cryptography.hazmat.primitives import serialization
    from dotenv import load_dotenv
except ModuleNotFoundError as e:
    print("Required modules are missing. Skipping execution in this environment.")
    snowflake = None
else:
    load_dotenv()

def run_sql(sql, context):
    if snowflake is None:
        print("Snowflake connector not available. Skipping SQL execution.")
        return

    private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    with open(private_key_path, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    private_key = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        private_key=private_key,
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    task_id = context.get('task_id', 'unknown_task')
    dag_id = context.get('dag_id', 'unknown_dag')
    ds = context.get('ds') or datetime.now().strftime('%Y-%m-%d')
    start_time = datetime.utcnow()

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            status = 'success'
    except Exception as e:
        status = 'failed'
        raise e
    finally:
        end_time = datetime.utcnow()
        try:
            with conn.cursor() as meta:
                meta.execute(f"""
                    INSERT INTO ingestion_metadata (dag_id, task_id, run_date, status, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (dag_id, task_id, ds, status, start_time, end_time))
        except Exception as log_err:
            print("⚠️ Failed to log metadata:", log_err)
        conn.close()

def execute_sql_with_jinja(file_path, **context):
    with open(file_path, 'r') as file:
        raw_sql = file.read()

    render_context = {
        'database': context.get('database') or os.getenv('SNOWFLAKE_DATABASE', 'MY_DB'),
        'schema': context.get('schema') or os.getenv('SNOWFLAKE_SCHEMA', 'RAW'),
        'ds': context.get('ds') or datetime.now().strftime('%Y-%m-%d')
    }

    template = Template(raw_sql)
    rendered_sql = template.render(render_context)

    print("Running SQL file:", file_path)
    return run_sql(rendered_sql, context)