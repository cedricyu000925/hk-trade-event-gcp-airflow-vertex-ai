CREATE OR REPLACE VIEW `{{ params.project_id }}.reporting.v_dashboard_master` AS
SELECT
  -- Registration facts
  f.registration_id,
  f.registration_date,
  f.attended,
  f.registration_fee_hkd,
  f.discount_rate,
  f.discount_amount_hkd,
  f.final_fee_hkd,
  f.participation_goal,
  f.satisfaction_score,
  f.sessions_attended,
  f.lead_source,
  f.customer_tenure_years,
  f.attended_mismatch,
  
  -- Customer dimension
  c.customer_id,
  c.customer_name,
  c.customer_email,
  c.company_name,
  c.business_sector,
  c.customer_region,
  c.customer_since,
  c.is_returning_customer,

  -- Event dimension
  e.event_id,
  e.event_name,
  e.event_year,
  e.event_category,
  e.event_venue

FROM `{{ params.project_id }}.mart.fct_registrations` f
JOIN `{{ params.project_id }}.mart.dim_customer` c USING (customer_id)
JOIN `{{ params.project_id }}.mart.dim_event`    e USING (event_id);