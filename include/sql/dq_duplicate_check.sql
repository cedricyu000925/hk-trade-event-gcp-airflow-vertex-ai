-- Duplicate registration_id detection in staging
SELECT
  registration_id,
  COUNT(*) AS occurrence_count
FROM `{{ params.project_id }}.staging.hk_trade_registrations`
GROUP BY registration_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;

-- Duplicate check on mart.fct_registrations
SELECT
  registration_id,
  COUNT(*) AS occurrence_count
FROM `{{ params.project_id }}.mart.fct_registrations`
GROUP BY registration_id
HAVING COUNT(*) > 1;