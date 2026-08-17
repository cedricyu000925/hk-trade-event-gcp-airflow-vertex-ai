CREATE OR REPLACE VIEW `{{ params.project_id }}.reporting.v_regional_demand` AS
SELECT
  customer_region,
  business_sector,
  SUM(total_registrations)                                        AS total_registrations,
  SUM(total_attended)                                             AS total_attended,
  ROUND(SUM(total_attended) / SUM(total_registrations) * 100, 2) AS attendance_rate_pct,
  ROUND(SUM(total_revenue_hkd), 2)                               AS total_revenue_hkd,
  SUM(returning_customers)                                        AS returning_customers,
  ROUND(SUM(returning_customers) / SUM(total_registrations) * 100, 2) AS returning_rate_pct
FROM `{{ params.project_id }}.reporting.hk_trade_report`
GROUP BY customer_region, business_sector
ORDER BY total_revenue_hkd DESC;