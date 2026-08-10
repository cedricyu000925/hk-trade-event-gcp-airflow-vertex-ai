# vertex_ai/insight_agent.py
# Demonstrates: LangChain chains, PromptTemplate, output parsing,
# LLM-based narrative generation, structured business insights.
 
from config import BQ_VIEW_MASTER, MODEL_NAME, PROJECT_ID, init_vertex
from google.cloud import bigquery
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import ChatVertexAI

init_vertex()
 
 
def get_kpi_summary() -> dict:
    """Pull aggregated KPIs from BigQuery for the insight agent."""
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
        SELECT
            COUNT(*)                                AS total_registrations,
            COUNTIF(attended)                       AS total_attended,
            ROUND(COUNTIF(attended) / COUNT(*) * 100, 1) AS attendance_rate_pct,
            ROUND(SUM(final_fee_hkd), 0)            AS total_revenue_hkd,
            ROUND(AVG(final_fee_hkd), 0)            AS avg_fee_hkd,
            ROUND(AVG(satisfaction_score), 2)       AS avg_satisfaction,
            COUNTIF(is_returning_customer)          AS returning_customers,
            COUNT(DISTINCT customer_id)             AS unique_customers,
            COUNT(DISTINCT event_id)                AS total_events
        FROM `{BQ_VIEW_MASTER}`
    """
    row = client.query(sql).to_dataframe().iloc[0].to_dict()
 
    # Top sector by registrations
    sql2 = f"""
        SELECT business_sector, COUNT(*) AS cnt
        FROM `{BQ_VIEW_MASTER}`
        GROUP BY 1 ORDER BY 2 DESC LIMIT 1
    """
    top_sector = client.query(sql2).to_dataframe().iloc[0]['business_sector']
    row['top_sector'] = top_sector
 
    # Top region by revenue
    sql3 = f"""
        SELECT customer_region, ROUND(SUM(final_fee_hkd), 0) AS revenue
        FROM `{BQ_VIEW_MASTER}`
        GROUP BY 1 ORDER BY 2 DESC LIMIT 1
    """
    top_region = client.query(sql3).to_dataframe().iloc[0]['customer_region']
    row['top_region'] = top_region
 
    return row
 
 
# ── LangChain prompt template ────────────────────────────────────────────
INSIGHT_TEMPLATE = PromptTemplate.from_template("""
You are a senior business analyst writing a monthly performance summary for
the HK Trade Event management team.
 
Below are the latest KPIs from the event registration database:
 
Total Registrations   : {total_registrations}
Total Attended        : {total_attended}
Attendance Rate       : {attendance_rate_pct}%
Total Revenue (HKD)   : {total_revenue_hkd}
Average Fee (HKD)     : {avg_fee_hkd}
Average Satisfaction  : {avg_satisfaction} / 5.0
Returning Customers   : {returning_customers}
Unique Customers      : {unique_customers}
Total Events          : {total_events}
Top Sector (volume)   : {top_sector}
Top Region (revenue)  : {top_region}
 
Write a professional executive summary (4–6 paragraphs) covering:
1. Overall performance headline
2. Revenue and registration highlights
3. Customer engagement and loyalty observations
4. Satisfaction and attendance quality
5. One key strategic recommendation
 
Use a professional business tone suitable for senior management.
Do not invent numbers not listed above.
""")
 
 
def generate_executive_summary() -> str:
    kpis  = get_kpi_summary()
    llm   = ChatVertexAI(model_name=MODEL_NAME, temperature=0.3)
    chain = INSIGHT_TEMPLATE | llm | StrOutputParser()
    return chain.invoke(kpis)
 
 
if __name__ == "__main__":
    print("Generating executive summary from live BigQuery KPIs...\n")
    summary = generate_executive_summary()
    print(summary)
    with open("output_executive_summary.txt", "w") as f:
        f.write(summary)
    print("\n✅ Summary saved to output_executive_summary.txt")