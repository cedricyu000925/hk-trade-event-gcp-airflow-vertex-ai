-- Null check across critical fields in staging.hk_trade_registrations
SELECT
  'registration_id'   AS field, COUNTIF(registration_id IS NULL)   AS null_count FROM `{{ params.project_id }}.staging.hk_trade_registrations`
UNION ALL
SELECT 'customer_id',           COUNTIF(customer_id IS NULL)        FROM `{{ params.project_id }}.staging.hk_trade_registrations`
UNION ALL
SELECT 'event_id',              COUNTIF(event_id IS NULL)           FROM `{{ params.project_id }}.staging.hk_trade_registrations`
UNION ALL
SELECT 'registration_date',     COUNTIF(registration_date IS NULL)  FROM `{{ params.project_id }}.staging.hk_trade_registrations`
UNION ALL
SELECT 'final_fee_hkd',         COUNTIF(final_fee_hkd IS NULL)      FROM `{{ params.project_id }}.staging.hk_trade_registrations`
UNION ALL
SELECT 'satisfaction_score',    COUNTIF(satisfaction_score IS NULL) FROM `{{ params.project_id }}.staging.hk_trade_registrations`;