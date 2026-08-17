SELECT
  COUNT(*) AS total_rows,
  COUNTIF(registration_id IS NULL) AS null_registration_id,
  COUNTIF(event_name IS NULL) AS null_event_name,
  COUNTIF(registration_date IS NULL) AS null_registration_date
FROM `{{ params.project_id }}.raw.hk_trade_registrations`
HAVING
  total_rows = 0
  OR null_registration_id / total_rows > 0.10
  OR null_event_name / total_rows > 0.10