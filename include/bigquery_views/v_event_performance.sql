CREATE OR REPLACE VIEW `{{ params.project_id }}.reporting.v_event_performance` AS
SELECT
  event_name,
  event_year,
  event_category,
  event_venue,
  SUM(total_registrations)                                    AS total_registrations,
  SUM(total_attended)                                         AS total_attended,
  ROUND(SUM(total_attended) / SUM(total_registrations) * 100, 2) AS attendance_rate_pct,
  ROUND(SUM(total_revenue_hkd), 2)                           AS total_revenue_hkd,
  ROUND(AVG(avg_satisfaction_score), 2)                      AS avg_satisfaction_score,
  ROUND(AVG(avg_sessions_attended), 2)                       AS avg_sessions_attended
FROM `{{ params.project_id }}.reporting.hk_trade_report`
GROUP BY event_name, event_year, event_category, event_venue
ORDER BY total_revenue_hkd DESC;