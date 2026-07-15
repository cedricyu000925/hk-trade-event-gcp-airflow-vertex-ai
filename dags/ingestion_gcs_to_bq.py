import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

# ── Configuration ─────────────────────────────────────────────────────────────
GCP_PROJECT_ID  = "ID" # ← replace with your actual project ID
GCS_BUCKET      = "BUCKET" # ← replace with your actual bucket name
SOURCE_OBJECT   = "raw/hk_trade_event_registrations.csv"
DEST_OBJECT     = "processed/hk_trade_event_registrations_{{ ds_nodash }}.csv"
BQ_RAW_DATASET  = "raw"
BQ_MAIN_TABLE   = "hk_trade_registrations"
BQ_LOG_TABLE    = "ingestion_log"
SCHEMA_PATH     = "include/schemas/hk_trade_registrations_schema.json"

# ── Default args ──────────────────────────────────────────────────────────────
default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

# ── DAG definition ────────────────────────────────────────────────────────────
with DAG(
    dag_id="ingestion_gcs_to_bq",
    description="Senses CSV in GCS raw/, loads into BigQuery raw dataset, logs metadata, moves file to processed/",
    start_date=datetime(2024, 1, 1),
    schedule=None,         # Triggered manually or by simulate_drop.py
    catchup=False,
    default_args=default_args,
    tags=["ingestion", "gcs", "bigquery", "phase4"],
) as dag:

    # ── Task 1: Sense the file in GCS ─────────────────────────────────────────
    sense_file = GCSObjectExistenceSensor(
        task_id="sense_raw_file",
        bucket=GCS_BUCKET,
        object=SOURCE_OBJECT,
        mode="reschedule",          # Releases the worker slot between pokes — important for free-tier local setup
        poke_interval=30,           # Check every 30 seconds
        timeout=60 * 60,            # Give up after 1 hour
        google_cloud_conn_id="google_cloud_default",
    )

    # ── Task 2: Load CSV from GCS into BigQuery raw table ─────────────────────
    load_to_bq = GCSToBigQueryOperator(
        task_id="load_csv_to_bq_raw",
        bucket=GCS_BUCKET,
        source_objects=[SOURCE_OBJECT],
        destination_project_dataset_table=f"{GCP_PROJECT_ID}.{BQ_RAW_DATASET}.{BQ_MAIN_TABLE}",
        source_format="CSV",
        skip_leading_rows=1,                # Skip the CSV header row
        autodetect=True,
        write_disposition="WRITE_TRUNCATE", # Overwrite the table on each full load
        allow_jagged_rows=True,             # Tolerate rows with missing trailing columns
        allow_quoted_newlines=True,
        gcp_conn_id="google_cloud_default",
    )

    # ── Task 3: Write ingestion metadata to the log table ─────────────────────
    log_metadata = BigQueryInsertJobOperator(
    task_id="log_ingestion_metadata",
    configuration={
        "query": {
            "query": f"""
                INSERT INTO `{GCP_PROJECT_ID}.{BQ_RAW_DATASET}.{BQ_LOG_TABLE}`
                (log_id, dag_id, run_id, source_file, gcs_bucket, load_status, ingested_at, destination_table)
                VALUES (
                    GENERATE_UUID(),
                    '{{{{ dag.dag_id }}}}',
                    '{{{{ run_id }}}}',
                    '{SOURCE_OBJECT}',
                    '{GCS_BUCKET}',
                    'SUCCESS',
                    CURRENT_TIMESTAMP(),
                    '{GCP_PROJECT_ID}.{BQ_RAW_DATASET}.{BQ_MAIN_TABLE}'
                )
            """,
            "useLegacySql": False
        }
    },
    gcp_conn_id="google_cloud_default",
)

    # ── Task 4: Move file from raw/ to processed/ ─────────────────────────────
    move_to_processed = GCSToGCSOperator(
        task_id="move_file_to_processed",
        source_bucket=GCS_BUCKET,
        source_object=SOURCE_OBJECT,
        destination_bucket=GCS_BUCKET,
        destination_object=DEST_OBJECT,     # Appends run date to filename for traceability
        move_object=True,                   # Deletes the source after copy (true move)
        gcp_conn_id="google_cloud_default",
    )

    # ── Task dependency chain ─────────────────────────────────────────────────
    sense_file >> load_to_bq >> log_metadata >> move_to_processed