CREATE OR REPLACE TABLE `{{ params.project_id }}.mart.dim_customer` AS
SELECT DISTINCT
  customer_id,
  customer_name,
  customer_email,
  company_name,
  business_sector,
  customer_region,
  customer_since,
  is_returning_customer
FROM `{{ params.project_id }}.staging.hk_trade_registrations`;

CREATE OR REPLACE TABLE `{{ params.project_id }}.mart.dim_event` AS
SELECT DISTINCT
  event_id,
  event_name,
  event_year,
  event_category,
  event_venue
FROM `{{ params.project_id }}.staging.hk_trade_registrations`;

CREATE OR REPLACE TABLE `{{ params.project_id }}.mart.fct_registrations` AS
SELECT
  registration_id,
  customer_id,
  event_id,
  registration_date,
  attended,
  registration_fee_hkd,
  discount_rate,
  discount_amount_hkd,
  final_fee_hkd,
  participation_goal,
  satisfaction_score,
  sessions_attended,
  lead_source,
  customer_tenure_years,
  attended_mismatch,
  _loaded_at
FROM `{{ params.project_id }}.staging.hk_trade_registrations`;