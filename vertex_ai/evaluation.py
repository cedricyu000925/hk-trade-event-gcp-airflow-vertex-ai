# vertex_ai/evaluation.py
# Demonstrates: Vertex AI Gen AI Evaluation SDK, custom metrics,
# PointwiseMetric, rubric design, evaluation dataset creation.
 
import pandas as pd
import vertexai
from vertexai.evaluation import EvalTask, PointwiseMetric, PointwiseMetricPromptTemplate
from google.cloud import aiplatform
from config import PROJECT_ID, LOCATION, init_vertex
from prompt_qa import ask_business_question
from rag_pipeline import rag_answer
 
init_vertex()
EXPERIMENT_NAME = "hk-trade-event-llm-eval"
 
 
# ── Define custom evaluation metrics ─────────────────────────────────────
groundedness_metric = PointwiseMetric(
    metric="groundedness",
    metric_prompt_template=PointwiseMetricPromptTemplate(
        criteria={
            "data_grounded": (
                "The response uses only facts and figures that are present in "
                "the data context or retrieved records provided. It does not "
                "introduce statistics or claims not found in the source data."
            ),
            "no_fabrication": (
                "The response does not hallucinate events, customer names, "
                "numbers, or conclusions that cannot be verified from the context."
            ),
        },
        rating_rubric={
            "1":  "Fully grounded — all claims traceable to provided context.",
            "0":  "Partially grounded — some unverified claims present.",
            "-1": "Not grounded — response contains fabricated information.",
        },
    ),
)
 
business_clarity_metric = PointwiseMetric(
    metric="business_clarity",
    metric_prompt_template=PointwiseMetricPromptTemplate(
        criteria={
            "clear_language": (
                "The response uses clear, professional business language "
                "that is easy to understand for a non-technical executive audience."
            ),
            "actionable": (
                "The response provides specific, actionable insights rather than "
                "vague or generic observations."
            ),
        },
        rating_rubric={
            "1":  "Excellent — clear, specific, and immediately actionable.",
            "0":  "Adequate — somewhat clear but lacks specificity.",
            "-1": "Poor — vague, technical jargon, or not actionable.",
        },
    ),
)
 
 
# ── Build evaluation dataset ──────────────────────────────────────────────
EVAL_QUESTIONS = [
    "Which customer region generates the highest registration revenue?",
    "What is the overall attendance rate across all events?",
    "Which business sector has the most returning customers?",
    "What is the average satisfaction score for events held in 2023?",
    "Which event category attracts the highest-value customers?",
]
 
def build_eval_dataset() -> pd.DataFrame:
    responses_prompt = [ask_business_question(q) for q in EVAL_QUESTIONS]
    responses_rag    = [rag_answer(q)             for q in EVAL_QUESTIONS]
 
    rows = []
    for q, r_prompt, r_rag in zip(EVAL_QUESTIONS, responses_prompt, responses_rag):
        rows.append({"question": q, "response": r_prompt, "source": "prompt_qa"})
        rows.append({"question": q, "response": r_rag,    "source": "rag_pipeline"})
    return pd.DataFrame(rows)
 
 
def run_evaluation():
    print("Building evaluation dataset (calling Gemini for each question)...")
    eval_df = build_eval_dataset()
 
    print(f"\nRunning Vertex AI evaluation on {len(eval_df)} responses...")
    eval_task = EvalTask(
        dataset=eval_df,
        metrics=[groundedness_metric, business_clarity_metric],
        experiment=EXPERIMENT_NAME,
    )
    result = eval_task.evaluate()
 
    print("\n── Evaluation Results ────────────────────────────────")
    print(result.summary_metrics)
    print("\n── Per-response scores ───────────────────────────────")
    print(result.metrics_table[
        ["question", "source", "groundedness/score", "business_clarity/score"]
    ].to_string(index=False))
 
    result.metrics_table.to_csv("evaluation_results.csv", index=False)
    print("\n✅ Full results saved to evaluation_results.csv")
    return result
 
 
if __name__ == "__main__":
    run_evaluation()