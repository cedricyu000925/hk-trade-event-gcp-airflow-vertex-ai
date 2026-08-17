-- Business rule violations in staging.hk_trade_registrations
SELECT
  'fee_below_zero'             AS rule,
  COUNTIF(final_fee_hkd < 0)  AS violations
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT
  'discount_exceeds_fee',
  COUNTIF(discount_amount_hkd > registration_fee_hkd)
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT
  'satisfaction_out_of_range',
  COUNTIF(satisfaction_score < 0 OR satisfaction_score > 10)
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT
  'future_registration_date',
  COUNTIF(registration_date > CURRENT_DATE())
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT
  'attended_mismatch_flag',
  COUNTIF(attended_mismatch = TRUE)
FROM `{{ params.project_id }}.staging.hk_trade_registrations`

UNION ALL
SELECT
  'sessions_without_attendance',
  COUNTIF(attended = FALSE AND sessions_attended > 0)
FROM `{{ params.project_id }}.staging.hk_trade_registrations`;