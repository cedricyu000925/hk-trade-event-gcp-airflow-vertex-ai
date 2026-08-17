CREATE OR REPLACE VIEW `{{ params.project_id }}.reporting.v_lead_source_analysis` AS
SELECT
  f.lead_source,
  COUNT(f.registration_id)                                       AS total_registrations,
  COUNTIF(f.attended = TRUE)                                     AS total_attended,
  ROUND(COUNTIF(f.attended = TRUE) / COUNT(f.registration_id) * 100, 2) AS attendance_rate_pct,
  ROUND(SUM(f.final_fee_hkd), 2)                                AS total_revenue_hkd,
  ROUND(AVG(f.final_fee_hkd), 2)                                AS avg_fee_hkd,
  ROUND(AVG(f.satisfaction_score), 2)                           AS avg_satisfaction_score
FROM `{{ params.project_id }}.mart.fct_registrations` f
GROUP BY f.lead_source
ORDER BY total_revenue_hkd DESC;