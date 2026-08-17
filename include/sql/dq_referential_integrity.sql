-- Check for orphaned customer_id in fct_registrations
SELECT
  'orphaned_customer_id' AS check_name,
  COUNT(*) AS failing_rows
FROM `{{ params.project_id }}.mart.fct_registrations` f
LEFT JOIN `{{ params.project_id }}.mart.dim_customer` c USING (customer_id)
WHERE c.customer_id IS NULL

UNION ALL

-- Check for orphaned event_id in fct_registrations
SELECT
  'orphaned_event_id',
  COUNT(*)
FROM `{{ params.project_id }}.mart.fct_registrations` f
LEFT JOIN `{{ params.project_id }}.mart.dim_event` e USING (event_id)
WHERE e.event_id IS NULL;