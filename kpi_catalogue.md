# KPI Catalogue: HK Trade Event Analytics

| KPI Name | Definition | Source Table | Business Use |
|---|---|---|---|
| Total Registrations | COUNT DISTINCT of registration_id | reporting.v_dashboard_master | Event planning capacity |
| Attendance Rate | Total Attended / Total Registrations × 100 | reporting.v_dashboard_master | Event engagement quality |
| Average Final Fee (HKD) | AVG(final_fee_hkd) | reporting.v_dashboard_master | Revenue per registration |
| Total Revenue (HKD) | SUM(final_fee_hkd) | reporting.v_dashboard_master | Event financial performance |
| Average Satisfaction Score | AVG(satisfaction_score) | reporting.v_dashboard_master | Attendee experience quality |
| Returning Customer Rate | Returning Customers / Total Registrations × 100 | reporting.v_dashboard_master | Customer loyalty |
| Average Sessions Attended | AVG(sessions_attended) | reporting.v_dashboard_master | Content engagement depth |
| Customer Lifetime Spend (HKD) | SUM(final_fee_hkd) per customer | reporting.v_dashboard_master | High-value customer identification |
| Events per Customer | COUNT DISTINCT registration_id per customer | reporting.v_dashboard_master | Customer engagement frequency |