# Architecture

## Overview

This project implements an end-to-end data pipeline for HK Trade Event registrations,
moving data from raw file ingestion in Google Cloud Storage through to curated,
business-ready analytics in BigQuery and Looker Studio. The pipeline is orchestrated
by Apache Airflow and organized using a layered dataset architecture (raw, staging,
mart, reporting) to keep responsibilities clearly separated and easy to reason about.

## High-Level Data Flow
GCS (raw file drop)
│
▼
Airflow DAG: pipeline_orchestrator.py
│
▼
raw.hk_trade_registrations
│
▼
staging.hk_trade_registrations
│
▼
mart.dim_customer mart.dim_event mart.fct_registrations
│
▼
reporting.hk_trade_report reporting.customer_kpis reporting.v_dashboard_master
│
▼
Looker Studio Dashboard


## Layered Dataset Architecture

### raw

- **Purpose:** Landing zone for ingested source data, stored as close to the original
  file format as possible.
- **Table:** `raw.hk_trade_registrations`
- **Characteristics:** No business logic applied. Column names and types reflect the
  source file structure. Serves as the single source of truth if reprocessing is
  needed.

### staging

- **Purpose:** Cleaned and standardized data with corrected types, casts, and derived
  helper columns needed for downstream modeling.
- **Table:** `staging.hk_trade_registrations`
- **Characteristics:** Adds derived fields such as `discount_amount_hkd`,
  `customer_tenure_years`, and `attended_mismatch` for data quality flagging.
  This layer is also where data quality checks are executed before promotion
  to the mart layer.

### mart

- **Purpose:** Dimensional model built for analytical querying, following a star
  schema pattern.
- **Tables:**
  - `mart.dim_customer` — customer attributes (name, email, company, sector, region,
    tenure, returning customer flag)
  - `mart.dim_event` — event attributes (name, year, category, venue)
  - `mart.fct_registrations` — registration-level facts (fees, discounts, attendance,
    satisfaction score, lead source) joined to both dimensions via `customer_id` and
    `event_id`
- **Characteristics:** Optimized for joins and aggregation. This is the layer that
  supports KPI computation and scalable query design.

### reporting

- **Purpose:** Business-facing, consumption-ready outputs for dashboards and
  stakeholder reporting.
- **Tables/Views:**
  - `reporting.hk_trade_report` — flattened summary table for general reporting
  - `reporting.customer_kpis` — precomputed customer-level KPI metrics
  - `reporting.v_dashboard_master` — single master view joining
    `mart.fct_registrations`, `mart.dim_customer`, and `mart.dim_event`, used as the
    unified data source for all Looker Studio scorecards and charts
- **Characteristics:** No further transformation should be required downstream —
  this layer is designed to be queried directly by BI tools.

## Orchestration Layer

- **Tool:** Apache Airflow
- **DAG file:** `dags/pipeline_orchestrator.py`
- **DAG ID:** `pipeline_orchestrator`
- **Schedule:** Daily at 06:00 Asia/Hong_Kong (`schedule="0 6 * * *"`)
- **Key behaviors:**
  - `catchup=False` — prevents historical backfill runs
  - `max_active_runs=1` — prevents overlapping DAG runs
  - Uses a GCS sensor task to detect new source file drops before ingestion begins
  - Executes SQL transformation logic stored in `include/sql/` rather than embedding
    SQL directly in the DAG file, keeping orchestration and transformation concerns
    separate

### DAG Task Flow

1. `sense_raw_data` — waits for the source file to land in the GCS bucket
2. `validate_raw` — checks raw table assumptions
   (`include/sql/validate_raw.sql`)
3. `transform_to_staging` — standardizes types, derives helper columns
   (`include/sql/transform_staging.sql`)
4. `dq_check_staging` — runs data quality checks and logs failures to
   `staging.dq_failures` (`include/sql/dq_check_staging.sql`)
5. `transform_to_mart` — builds dimension and fact tables
   (`include/sql/transform_mart.sql`)
6. `publish_to_reporting` — refreshes reporting tables and views
   (`include/sql/publish_reporting.sql`)
7. `log_success` — records a successful pipeline completion

## Storage and Compute

- **File landing zone:** Google Cloud Storage bucket for raw file drops
- **Data warehouse:** BigQuery, organized into the four datasets described above
- **Compute:** BigQuery's serverless query engine executes all SQL transformations;
  no separate compute cluster is required

## Business Intelligence Layer

- **Tool:** Looker Studio
- **Data source:** `reporting.v_dashboard_master`
- **Design decision:** All scorecards and charts in the dashboard read from this
  single master view rather than multiple disconnected tables, which simplifies
  field management and avoids join mismatches inside Looker Studio itself

## Data Quality and Governance

- Null validation, duplicate detection, referential integrity, and business rule
  checks are implemented as SQL scripts under `include/sql/` and executed as part
  of the DAG
- Data quality failures are logged to `staging.dq_failures` for auditability
  rather than silently dropped or only failing the pipeline

## CI/CD and Version Control

- **Repository structure:** DAG code, SQL templates, tests, and documentation are
  version controlled together in a single repository
- **Continuous Integration:** GitHub Actions (`.github/workflows/ci.yml`) lints
  Python code, validates DAG syntax, and runs `pytest` on every push and pull
  request
- **Deployment packaging:** GitHub Actions (`.github/workflows/deploy.yml`)
  packages the `dags/`, `include/`, and `docs/` directories into a versioned
  artifact on manual trigger

## Design Principles

- **Separation of concerns:** Orchestration logic (Airflow) is kept separate from
  transformation logic (SQL files), which is kept separate from consumption logic
  (Looker Studio)
- **Idempotency:** Transformation and publishing steps are designed so that
  re-running the pipeline does not produce duplicate or inconsistent results
- **Single source of truth per layer:** Each dataset layer has one clear
  responsibility, avoiding logic duplication across the pipeline
- **Auditability:** Data quality issues are logged rather than silently discarded,
  supporting trust in downstream dashboards and reporting