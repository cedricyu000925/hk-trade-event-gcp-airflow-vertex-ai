# vertex_ai/app.py
# Streamlit demo: all four AI modules in one interactive interface.
# Run with: streamlit run vertex_ai/app.py
 
import streamlit as st
from prompt_qa     import ask_business_question
from rag_pipeline  import rag_answer
from insight_agent import generate_executive_summary
from nl2sql        import ask_data_question
from config import PROJECT_ID
 
st.set_page_config(
    page_title="HK Trade Event AI Assistant",
    page_icon="🤖",
    layout="wide",
)
 
st.title("🤖 HK Trade Event — AI Engineering Demo")
st.markdown(
    "_Built with Vertex AI Gemini · BigQuery Vector Search · LangChain · RAG_"
)
st.divider()
 
# ── Sidebar: module selector ──────────────────────────────────────────────
st.sidebar.title("Select Module")
module = st.sidebar.radio(
    "Choose an AI capability:",
    [
        "📊 Business Q&A (Prompt Engineering)",
        "🔍 Semantic Search (RAG)",
        "💬 Natural Language to SQL",
        "📝 Executive Summary (Insight Agent)",
    ],
)
 
# ── MODULE 1: Prompt Engineering Q&A ─────────────────────────────────────
if module == "📊 Business Q&A (Prompt Engineering)":
    st.header("📊 Business Q&A — Prompt Engineering")
    st.info(
        "Ask any business question about event registrations, customers, and revenue. "
        "Answers are grounded in live BigQuery data via context injection."
    )
    question = st.text_input(
        "Your question:",
        placeholder="e.g. Which sector has the highest repeat attendance rate?"
    )
    if st.button("Ask Gemini") and question:
        with st.spinner("Generating answer..."):
            answer = ask_business_question(question)
        st.success("Answer")
        st.write(answer)
 
# ── MODULE 2: RAG Semantic Search ────────────────────────────────────────
elif module == "🔍 Semantic Search (RAG)":
    st.header("🔍 Semantic Search — RAG Pipeline")
    st.info(
        "Uses BigQuery vector search to find semantically similar registration records, "
        "then asks Gemini to answer based only on retrieved context."
    )
    query = st.text_input(
        "What are you looking for?",
        placeholder="e.g. High-value Finance customers who attended in 2023"
    )
    if st.button("Search & Answer") and query:
        with st.spinner("Embedding query and searching vector store..."):
            answer = rag_answer(query)
        st.success("RAG Answer")
        st.write(answer)
 
# ── MODULE 3: Text-to-SQL ────────────────────────────────────────────────
elif module == "💬 Natural Language to SQL":
    st.header("💬 Natural Language to SQL")
    st.info(
        "Type a business question in plain English. "
        "The agent writes a BigQuery SQL query, runs it, and explains the result."
    )
    nl_question = st.text_input(
        "Ask a data question:",
        placeholder="e.g. What is the total revenue from returning customers?"
    )
    if st.button("Query BigQuery") and nl_question:
        with st.spinner("Agent generating and executing SQL..."):
            result = ask_data_question(nl_question)
        st.success("Result")
        st.write(result)
 
# ── MODULE 4: Executive Summary ───────────────────────────────────────────
elif module == "📝 Executive Summary (Insight Agent)":
    st.header("📝 Executive Summary — LangChain Insight Agent")
    st.info(
        "Pulls live KPIs from BigQuery and generates a professional executive "
        "summary using LangChain and Gemini."
    )
    if st.button("Generate Executive Summary"):
        with st.spinner("Pulling KPIs from BigQuery and generating narrative..."):
            summary = generate_executive_summary()
        st.success("Executive Summary")
        st.write(summary)
        st.download_button(
            label="Download as .txt",
            data=summary,
            file_name="hk_trade_executive_summary.txt",
        )
 
st.sidebar.divider()
st.sidebar.caption(
    f"Stack: Vertex AI Gemini · BigQuery Vector Search · LangChain · Streamlit\n"
    f"Project: GCP Airflow Vertex AI Portfolio\n"
    f"Data: {PROJECT_ID}"
)