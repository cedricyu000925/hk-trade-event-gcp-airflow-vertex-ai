# Data Governance: HK Trade Event Pipeline

## Data Ownership

| Dataset | Owner Role | Description |
|---|---|---|
| raw.hk_trade_registrations | Data Engineer | Source of truth; never modified after ingestion |
| staging.hk_trade_registrations | Data Engineer | Cleaned and typed; refreshed on every pipeline run |
| mart.dim_customer | Data Engineer | Customer dimension; rebuilt from staging |
| mart.dim_event | Data Engineer | Event dimension; rebuilt from staging |
| mart.fct_registrations | Data Engineer | Registration fact table; rebuilt from staging |
| reporting.hk_trade_report | Analytics | Pre-aggregated KPI table for dashboard consumption |
| reporting.customer_kpis | Analytics | Customer-level metric rollup for segmentation |

## Data Lineage
GCS (raw CSV)
└ raw.hk_trade_registrations [ingestion_gcs_to_bq]
└ staging.hk_trade_registrations [transform_to_staging]
├ staging.dq_failures [dq_check_staging]
├ mart.dim_customer [transform_to_mart]
├ mart.dim_event [transform_to_mart]
└ mart.fct_registrations [transform_to_mart]
├ reporting.hk_trade_report [publish_to_reporting]
└ reporting.customer_kpis [publish_to_reporting]

## Access Patterns

| Consumer | Dataset(s) Accessed | Access Type |
|---|---|---|
| Airflow pipeline service account | All datasets | Read/Write via BigQuery job |
| Looker Studio dashboard | reporting.* | Read-only |
| Data engineer (developer) | All datasets | Read/Write (BigQuery Studio) |
| Analyst | staging.*, mart.*, reporting.* | Read-only (BigQuery Console) |

## Freshness SLA

| Layer | Expected refresh cadence | Staleness threshold |
|---|---|---|
| Raw | On file drop to GCS | N/A |
| Staging | Within 30 min of raw load | 24 hours |
| Mart | Within 5 min of staging | 24 hours |
| Reporting | Within 5 min of mart | 24 hours |

## Known Data Quality Anomalies

- `attended_mismatch`: Up to ~2% of records may show `attended = FALSE` but `sessions_attended > 0`. This is a known source system quirk and is flagged but not removed.
- `satisfaction_score`: Nullable by design — not all attendees submit a satisfaction rating.