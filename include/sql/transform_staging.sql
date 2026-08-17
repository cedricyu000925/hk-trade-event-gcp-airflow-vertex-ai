CREATE OR REPLACE TABLE `{{ params.project_id }}.staging.hk_trade_registrations` AS
SELECT
  registration_id,
  customer_id,
  TRIM(UPPER(customer_name))                                     AS customer_name,
  LOWER(customer_email)                                          AS customer_email,
  TRIM(company_name)                                             AS company_name,
  TRIM(UPPER(business_sector))                                   AS business_sector,
  TRIM(UPPER(customer_region))                                   AS customer_region,
  CAST(customer_since AS DATE)                                   AS customer_since,
  event_id,
  TRIM(event_name)                                               AS event_name,
  CAST(event_year AS INT64)                                      AS event_year,
  TRIM(UPPER(event_category))                                    AS event_category,
  TRIM(event_venue)                                              AS event_venue,
  CAST(registration_date AS DATE)                                AS registration_date,
  CAST(attended AS BOOL)                                         AS attended,
  CAST(registration_fee_hkd AS FLOAT64)                          AS registration_fee_hkd,
  CAST(discount_rate AS FLOAT64)                                 AS discount_rate,
  CAST(final_fee_hkd AS FLOAT64)                                 AS final_fee_hkd,
  ROUND(registration_fee_hkd - final_fee_hkd, 2)                AS discount_amount_hkd,
  TRIM(participation_goal)                                       AS participation_goal,
  CAST(satisfaction_score AS FLOAT64)                            AS satisfaction_score,
  CAST(sessions_attended AS INT64)                               AS sessions_attended,
  TRIM(UPPER(lead_source))                                       AS lead_source,
  CAST(is_returning_customer AS BOOL)                            AS is_returning_customer,
  DATE_DIFF(CAST(registration_date AS DATE),
            CAST(customer_since AS DATE), YEAR)                  AS customer_tenure_years,
  CASE
    WHEN attended = FALSE AND CAST(sessions_attended AS INT64) > 0
    THEN TRUE ELSE FALSE
  END                                                            AS attended_mismatch,
  CURRENT_TIMESTAMP()                                            AS _loaded_at
FROM `{{ params.project_id }}.raw.hk_trade_registrations`
WHERE registration_id IS NOT NULL
  AND customer_id IS NOT NULL;