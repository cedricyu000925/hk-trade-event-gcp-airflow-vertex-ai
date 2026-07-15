import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.standard.operators.python import BranchPythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

import os

def load_sql(filename: str, project_id: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_path = os.path.join(base_dir, "include", "sql", filename)
    with open(sql_path, "r") as f:
        return f.read().replace("{{ params.project_id }}", project_id)

# ── Config ────────────────────────────────────────────────────────────────────
GCP_PROJECT_ID  = "ID"          # ← replace with your actual project ID
GCS_BUCKET      = "BUCKET"         # ← replace with your actual bucket name
SOURCE_OBJECT   = "raw/hk_trade_event_registrations.csv"
BQ_CONN         = "google_cloud_default"

PARAMS = {"project_id": GCP_PROJECT_ID}

# ── Default args (applies to every task) ─────────────────────────────────────
def on_failure_alert(context):
    """Fires on any task failure — logs a structured failure record."""
    logging.error(
        json.dumps({
            "event":    "task_failed",
            "dag_id":   context["dag"].dag_id,
            "task_id":  context["task_instance"].task_id,
            "run_id":   context["run_id"],
            "reason":   str(context.get("exception", "unknown")),
        })
    )

default_args = {
    "owner":              "data-engineering",
    "depends_on_past":    False,
    "retries":            2,
    "retry_delay":        timedelta(minutes=3),
    "retry_exponential_backoff": True,
    "on_failure_callback": on_failure_alert,
    "execution_timeout":  timedelta(minutes=30),
}

# ── DAG definition ────────────────────────────────────────────────────────────
import pendulum

with DAG(
    dag_id="pipeline_orchestrator",
    description="End-to-end HK Trade Event pipeline: ingest → validate → transform → publish",
    schedule="0 6 * * *",  # run daily at 06:00
    start_date=pendulum.datetime(2026, 1, 1, 6, 0, tz="Asia/Hong_Kong"),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["orchestration", "bigquery", "phase5", "scheduled"],
    params=PARAMS,
    doc_md="""
    ## HK Trade Event Pipeline — Orchestrator DAG
    Runs the full pipeline from raw GCS file through to the reporting layer in BigQuery.
    Scheduled daily at 06:00 Asia/Hong_Kong for refresh, validation, transformation,
    and reporting publication.
    """,
) as dag:

    # ── Task 1: Sense raw file in GCS ─────────────────────────────────────────
    sense_raw = GCSObjectExistenceSensor(
        task_id="sense_raw_data",
        bucket=GCS_BUCKET,
        object=SOURCE_OBJECT,
        mode="reschedule",
        poke_interval=30,
        timeout=60 * 30,
        google_cloud_conn_id=BQ_CONN,
    )

    # ── Task 2: Validate raw data ─────────────────────────────────────────────
    validate_raw = BigQueryInsertJobOperator(
        task_id="validate_raw",
        configuration={
            "query": {
                "query": load_sql("validate_raw.sql", GCP_PROJECT_ID),
                "useLegacySql": False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    # ── Task 3: Transform raw → staging ──────────────────────────────────────
    transform_staging = BigQueryInsertJobOperator(
        task_id="transform_to_staging",
        configuration={
            "query": {
                "query": load_sql("transform_staging.sql", GCP_PROJECT_ID),
                "useLegacySql": False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    # ── Task 4: Data quality check on staging ─────────────────────────────────
    def check_dq_results(**context):
        from google.cloud import bigquery
        client = bigquery.Client(project=GCP_PROJECT_ID)
        query = f"SELECT COUNT(*) AS failure_count FROM `{GCP_PROJECT_ID}.staging._dq_failures`"
        result = client.query(query).result()
        for row in result:
            if row.failure_count > 0:
                logging.warning(f"DQ failures found: {row.failure_count} rows")
                return "dq_failed"
        logging.info("All DQ checks passed.")
        return "transform_to_mart"
    
    dq_check_staging = BigQueryInsertJobOperator(
        task_id='dq_check_staging',
        configuration={
            'query': {
                'query': load_sql('dq_check_staging.sql', GCP_PROJECT_ID),
                'useLegacySql': False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    dq_branch = BranchPythonOperator(
        task_id="dq_branch",
        python_callable=check_dq_results,
    )

    dq_failed = EmptyOperator(
        task_id="dq_failed",
    )

    # ── Task 5: Transform staging → mart ─────────────────────────────────────
    transform_mart = BigQueryInsertJobOperator(
        task_id="transform_to_mart",
        configuration={
            "query": {
                "query": load_sql("transform_mart.sql", GCP_PROJECT_ID),
                "useLegacySql": False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    # ── Task 6: Publish mart → reporting ─────────────────────────────────────
    publish_reporting = BigQueryInsertJobOperator(
        task_id="publish_to_reporting",
        configuration={
            "query": {
                "query": load_sql("publish_reporting.sql", GCP_PROJECT_ID),
                "useLegacySql": False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    # ── Task 7: Log success to ingestion_log ─────────────────────────────────
    log_success = BigQueryInsertJobOperator(
        task_id="notify_success",
        configuration={
            "query": {
                "query": f"""
                    INSERT INTO `{GCP_PROJECT_ID}.raw.ingestion_log`
                    (log_id, dag_id, run_id, source_file, gcs_bucket,
                     load_status, ingested_at, destination_table)
                    VALUES (
                        GENERATE_UUID(),
                        '{{{{ dag.dag_id }}}}',
                        '{{{{ run_id }}}}',
                        '{SOURCE_OBJECT}',
                        '{GCS_BUCKET}',
                        'SUCCESS',
                        CURRENT_TIMESTAMP(),
                        '{GCP_PROJECT_ID}.reporting.hk_trade_report'
                    )
                """,
                "useLegacySql": False,
            }
        },
        gcp_conn_id=BQ_CONN,
    )

    # ── Task Dependencies ─────────────────────────────────────────────────────
    (
        sense_raw
        >> validate_raw
        >> transform_staging
        >> dq_check_staging
        >> dq_branch
        >> [transform_mart, dq_failed]
    )
    transform_mart >> publish_reporting >> log_success