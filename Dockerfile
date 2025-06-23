FROM apache/airflow:2.8.1-python3.10

COPY requirements.txt /requirements.txt

USER airflow
ENV PYTHONPATH="/opt/airflow"
ENV AIRFLOW_HOME="/opt/airflow"

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /requirements.txt
