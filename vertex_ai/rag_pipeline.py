# vertex_ai/rag_pipeline.py
# Demonstrates: RAG architecture, BigQuery vector search, embedding-based retrieval,
# context injection, Gemini grounded generation.
 
import json

from config import MODEL_NAME, PROJECT_ID, init_vertex
from google.cloud import bigquery
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel

init_vertex()
 
EMBED_MODEL_NAME  = "text-embedding-004"
EMBEDDING_TABLE   = f"{PROJECT_ID}.reporting.registration_embeddings"
TOP_K             = 5   # number of similar records to retrieve
 
 
def embed_query(query_text: str) -> list:
    """Embed a user query using Vertex AI text-embedding-004."""
    model    = TextEmbeddingModel.from_pretrained(EMBED_MODEL_NAME)
    result   = model.get_embeddings([query_text])
    return result[0].values
 
 
def vector_search(query_embedding: list) -> str:
    """Use BigQuery VECTOR_SEARCH to find the most similar records."""
    client    = bigquery.Client(project=PROJECT_ID)
    embed_str = json.dumps(query_embedding)
    sql = f"""
        SELECT
            base.registration_id,
            base.record_text,
            distance
        FROM VECTOR_SEARCH(
            TABLE `{EMBEDDING_TABLE}`,
            'embedding',
            (SELECT {embed_str} AS embedding),
            top_k => {TOP_K},
            distance_type => 'COSINE'
        )
        ORDER BY distance ASC
    """
    df = client.query(sql).to_dataframe()
    context_parts = []
    for _, row in df.iterrows():
        context_parts.append(f"- {row['record_text']}")
    return "\n".join(context_parts)
 
 
def rag_answer(question: str) -> str:
    """Full RAG pipeline: embed → retrieve → generate."""
    print("[RAG] Embedding question...")
    query_embedding = embed_query(question)
 
    print("[RAG] Searching BigQuery vector store...")
    retrieved_context = vector_search(query_embedding)
 
    print("[RAG] Generating grounded answer...")
    prompt = f"""You are a business analyst assistant. Use only the following
retrieved records from our HK Trade Event registration database to answer
the question. Do not use any knowledge outside this context.
 
Retrieved Records:
{retrieved_context}
 
Question: {question}
 
Provide a concise, factual answer based strictly on the records above."""
 
    model    = GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text
 
 
if __name__ == "__main__":
    test_questions = [
        "Find me examples of high-value Finance sector customers who attended events.",
        "Which returning customers from Southeast Asia had high satisfaction scores?",
        "Show me cases where customers registered but did not attend.",
    ]
 
    for q in test_questions:
        print(f"\nQuestion: {q}")
        answer = rag_answer(q)
        print(f"Answer: {answer}")
        print("=" * 70)