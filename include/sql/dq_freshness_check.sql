-- Freshness check: when was each layer last loaded?
SELECT 'staging.hk_trade_registrations' AS layer,
  MAX(_loaded_at) AS last_loaded_at,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_loaded_at), HOUR) AS hours_since_load
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT 'mart.fct_registrations',
  MAX(_loaded_at),
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_loaded_at), HOUR)
FROM `{{ params.project_id }}.mart.fct_registrations`

UNION ALL
SELECT 'reporting.hk_trade_report',
  MAX(_report_generated_at),
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_report_generated_at), HOUR)
FROM `{{ params.project_id }}.reporting.hk_trade_report`;