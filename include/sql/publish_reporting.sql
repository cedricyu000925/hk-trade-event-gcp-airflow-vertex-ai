CREATE OR REPLACE TABLE `{{ params.project_id }}.reporting.hk_trade_report` AS
SELECT
  e.event_name,
  e.event_year,
  e.event_category,
  e.event_venue,
  c.customer_region,
  c.business_sector,
  COUNT(f.registration_id)                          AS total_registrations,
  COUNTIF(f.attended = TRUE)                        AS total_attended,
  ROUND(COUNTIF(f.attended = TRUE) /
        COUNT(f.registration_id) * 100, 2)          AS attendance_rate_pct,
  ROUND(AVG(f.final_fee_hkd), 2)                   AS avg_final_fee_hkd,
  ROUND(SUM(f.final_fee_hkd), 2)                   AS total_revenue_hkd,
  ROUND(AVG(f.satisfaction_score), 2)              AS avg_satisfaction_score,
  ROUND(AVG(f.sessions_attended), 2)               AS avg_sessions_attended,
  COUNTIF(c.is_returning_customer = TRUE)           AS returning_customers,
  CURRENT_TIMESTAMP()                               AS _report_generated_at
FROM `{{ params.project_id }}.mart.fct_registrations` f
JOIN `{{ params.project_id }}.mart.dim_event`    e USING (event_id)
JOIN `{{ params.project_id }}.mart.dim_customer` c USING (customer_id)
GROUP BY 1, 2, 3, 4, 5, 6;

CREATE OR REPLACE TABLE `{{ params.project_id }}.reporting.customer_kpis` AS
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_region,
  c.business_sector,
  c.is_returning_customer,
  COUNT(f.registration_id)                         AS total_registrations,
  COUNTIF(f.attended = TRUE)                       AS events_attended,
  ROUND(SUM(f.final_fee_hkd), 2)                  AS lifetime_spend_hkd,
  ROUND(AVG(f.satisfaction_score), 2)             AS avg_satisfaction,
  MAX(f.registration_date)                         AS last_registration_date
FROM `{{ params.project_id }}.mart.fct_registrations` f
JOIN `{{ params.project_id }}.mart.dim_customer` c USING (customer_id)
GROUP BY 1, 2, 3, 4, 5;