# vertex_ai/prompt_qa.py
# Demonstrates: prompt engineering, system instructions, context injection,
# few-shot prompting, and structured output formatting with Vertex AI Gemini.
 
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import bigquery
from config import PROJECT_ID, LOCATION, MODEL_NAME, BQ_VIEW_MASTER, init_vertex
 
init_vertex()
 
# ── 1. Pull a data context snapshot from BigQuery ──────────────────────────
def get_data_context() -> str:
    client = bigquery.Client(project=PROJECT_ID)
    sql = f"""
        SELECT
            event_name,
            event_year,
            business_sector,
            customer_region,
            COUNT(*)                          AS total_registrations,
            ROUND(AVG(final_fee_hkd), 0)      AS avg_fee_hkd,
            ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
            COUNTIF(attended = TRUE)          AS total_attended,
            COUNTIF(is_returning_customer)    AS returning_customers
        FROM `{BQ_VIEW_MASTER}`
        GROUP BY 1, 2, 3, 4
        ORDER BY total_registrations DESC
        LIMIT 30
    """
    df = client.query(sql).to_dataframe()
    return df.to_string(index=False)
 
 
# ── 2. System instruction — tells Gemini its role ─────────────────────────
SYSTEM_INSTRUCTION = """
You are a senior business analyst assistant for HK Trade Event Management Ltd.
You have access to curated event registration data covering customer participation,
fees, satisfaction scores, and attendance patterns across Hong Kong trade events.
 
Your role:
- Answer business questions using ONLY the data context provided.
- Be specific and cite numbers from the data.
- Format responses clearly with bullet points or short paragraphs.
- If the data does not support a conclusion, say so explicitly.
- Never fabricate statistics not present in the context.
"""
 
 
# ── 3. Few-shot examples — teach the model the expected style ─────────────
FEW_SHOT_EXAMPLES = """
Example Q: Which sector has the highest average satisfaction score?
Example A: Based on the data, the Finance sector records the highest average
satisfaction score of 4.21 out of 5, followed by Technology at 4.05.
This suggests Finance attendees find the most value in the current event format.
 
Example Q: What is the returning customer rate?
Example A: Of the registrations in the dataset, approximately 38% are from
returning customers, indicating strong repeat participation and event loyalty.
"""
 
 
# ── 4. Main Q&A function ──────────────────────────────────────────────────
def ask_business_question(question: str) -> str:
    data_context = get_data_context()
 
    prompt = f"""{FEW_SHOT_EXAMPLES}
 
--- DATA CONTEXT (live from BigQuery) ---
{data_context}
-----------------------------------------
 
Business Question: {question}
 
Please provide a clear, data-grounded answer in 3-5 sentences or bullet points.
"""
 
    model    = GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION)
    response = model.generate_content(prompt)
    return response.text
 
 
# ── 5. Demo run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "Which event year had the highest registration volumes and what drove it?",
        "Which customer region generates the most revenue from registration fees?",
        "What sectors show the highest attendance rate and lowest no-show rate?",
        "Are returning customers more satisfied than first-time attendees?",
    ]
 
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {ask_business_question(q)}")
        print("-" * 60)