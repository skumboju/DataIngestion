# Ingestion Framework for Snowflake (SQL-Driven)

This is a modular, config-driven data ingestion and transformation framework built for Snowflake and Airflow.

## Features

- 🔄 YAML-configured SQL pipelines
- 🔑 Key pair authentication with Snowflake
- 📊 Metadata logging for task executions
- 🧱 Folder-based DAG generation
- ☁️ Ready for AWS MWA or local Docker Airflow

## Structure

```
ingestion/
├── core/
│   └── config_loader.py
├── transformers/
│   └── sql_executor.py
dags/
├── dag_builder.py
transform/
├── your_dag_folder/
│   ├── 01_task.sql
│   ├── 02_task.sql
│   └── config.yaml
```

## Setup

1. Create a `.env` file with Snowflake connection details
2. Ensure `ingestion_metadata` table exists
3. Run via Airflow DAG or directly for testing

## Environment Variables

```env
SNOWFLAKE_USER=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
SNOWFLAKE_PRIVATE_KEY_PATH=
```

## License

MIT