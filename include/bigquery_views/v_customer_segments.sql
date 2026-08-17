CREATE OR REPLACE VIEW `{{ params.project_id }}.reporting.v_customer_segments` AS
SELECT
  customer_id,
  customer_name,
  customer_region,
  business_sector,
  is_returning_customer,
  total_registrations,
  events_attended,
  lifetime_spend_hkd,
  avg_satisfaction,
  last_registration_date,
  CASE
    WHEN lifetime_spend_hkd >= 10000 THEN 'High Value'
    WHEN lifetime_spend_hkd >= 5000  THEN 'Mid Value'
    ELSE 'Standard'
  END AS customer_segment,
  CASE
    WHEN total_registrations >= 5 THEN 'Highly Engaged'
    WHEN total_registrations >= 2 THEN 'Moderately Engaged'
    ELSE 'Low Engagement'
  END AS engagement_tier
FROM `{{ params.project_id }}.reporting.customer_kpis`;