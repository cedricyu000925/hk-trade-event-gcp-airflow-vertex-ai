CREATE OR REPLACE TABLE `{{ params.project_id }}.staging.dq_failures` AS

-- Null violations
SELECT
  'null_check'                          AS check_type,
  'registration_id'                     AS field_name,
  CAST(registration_id AS STRING)       AS offending_value,
  'registration_id is NULL'             AS failure_reason,
  CURRENT_TIMESTAMP()                   AS detected_at
FROM `{{ params.project_id }}.staging.hk_trade_registrations`
WHERE registration_id IS NULL

UNION ALL
SELECT 'null_check', 'customer_id', CAST(customer_id AS STRING),
  'customer_id is NULL', CURRENT_TIMESTAMP()
FROM `{{ params.project_id }}.staging.hk_trade_registrations`
WHERE customer_id IS NULL

UNION ALL
-- Business rule: fee below zero
SELECT 'business_rule', 'final_fee_hkd', CAST(final_fee_hkd AS STRING),
  'final_fee_hkd is negative', CURRENT_TIMESTAMP()
FROM `{{ params.project_id }}.staging.hk_trade_registrations`
WHERE final_fee_hkd < 0

UNION ALL
-- Business rule: satisfaction score out of range
SELECT 'business_rule', 'satisfaction_score', CAST(satisfaction_score AS STRING),
  'satisfaction_score outside 0-10 range', CURRENT_TIMESTAMP()
FROM `{{ params.project_id }}.staging.hk_trade_registrations`
WHERE satisfaction_score < 0 OR satisfaction_score > 10

UNION ALL
-- Duplicate registration_id
SELECT 'duplicate_check', 'registration_id', registration_id,
  CONCAT('registration_id appears ', CAST(cnt AS STRING), ' times'), CURRENT_TIMESTAMP()
FROM (
  SELECT registration_id, COUNT(*) AS cnt
  FROM `{{ params.project_id }}.staging.hk_trade_registrations`
  GROUP BY registration_id
  HAVING COUNT(*) > 1
);