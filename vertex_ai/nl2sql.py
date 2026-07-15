# vertex_ai/nl2sql.py
# Demonstrates: LangChain SQL agent, Text-to-SQL, BigQuery SQLAlchemy,
# agentic tool-use, natural language data access.
 
from langchain_google_vertexai import ChatVertexAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType
from sqlalchemy import create_engine
from config import PROJECT_ID, LOCATION, MODEL_NAME, init_vertex
 
init_vertex()
 
# ── Connect LangChain to BigQuery via SQLAlchemy ──────────────────────────
# Uses the sqlalchemy-bigquery dialect; reads from mart + reporting datasets
DATASETS_TO_INCLUDE = [
    "mart.fct_registrations",
    "mart.dim_customer",
    "mart.dim_event",
    "reporting.v_dashboard_master",
    "reporting.customer_kpis",
]
 
engine = create_engine(f"bigquery://{PROJECT_ID}")
db     = SQLDatabase(engine=engine, include_tables=DATASETS_TO_INCLUDE)
 
llm     = ChatVertexAI(model_name=MODEL_NAME, temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
 
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)
 
SYSTEM_PREFIX = """
You are a BigQuery SQL expert for HK Trade Event management data.
When asked a business question:
1. Generate a valid BigQuery Standard SQL query (NOT Legacy SQL).
2. Use fully qualified table names: project.dataset.table
3. Execute the query and interpret the result in plain business language.
4. Always format numbers clearly (e.g., HKD amounts with commas).
5. If a question is ambiguous, state your assumption before answering.
"""
 
 
def ask_data_question(question: str) -> str:
    full_question = SYSTEM_PREFIX + "\n\nBusiness Question: " + question
    result = agent.invoke({"input": full_question})
    return result["output"]
 
 
if __name__ == "__main__":
    questions = [
        "How many unique customers registered across all events?",
        "What is the total revenue collected from Finance sector customers?",
        "Which event had the highest average satisfaction score?",
        "What percentage of customers in the Southeast Asia region are returning customers?",
        "List the top 5 companies by total registration fees paid.",
    ]
 
    for q in questions:
        print(f"\n{'='*65}")
        print(f"Q: {q}")
        answer = ask_data_question(q)
        print(f"A: {answer}")