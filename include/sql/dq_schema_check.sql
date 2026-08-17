-- Schema check: assert all expected columns exist in staging.hk_trade_registrations
DECLARE missing_columns ARRAY<STRING>;

SET missing_columns = (
  SELECT ARRAY_AGG(expected_col)
  FROM UNNEST([
    'registration_id', 'customer_id', 'customer_name', 'customer_email',
    'company_name', 'business_sector', 'customer_region', 'customer_since',
    'event_id', 'event_name', 'event_year', 'event_category', 'event_venue',
    'registration_date', 'attended', 'registration_fee_hkd', 'discount_rate',
    'final_fee_hkd', 'discount_amount_hkd', 'participation_goal',
    'satisfaction_score', 'sessions_attended', 'lead_source',
    'is_returning_customer', 'customer_tenure_years', 'attended_mismatch'
  ]) AS expected_col
  WHERE expected_col NOT IN (
    SELECT column_name
    FROM `{{ params.project_id }}.staging.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'hk_trade_registrations'
  )
);

SELECT
  CASE
    WHEN ARRAY_LENGTH(missing_columns) = 0
    THEN 'PASS: All expected columns present'
    ELSE CONCAT('FAIL: Missing columns — ', ARRAY_TO_STRING(missing_columns, ', '))
  END AS schema_check_result;