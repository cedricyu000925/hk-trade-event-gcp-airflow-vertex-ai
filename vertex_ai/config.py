import os

import vertexai

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LOCATION = "us-central1"
MODEL_NAME = "gemini-1.5-flash"

BQ_DATASET_MART = "mart"
BQ_DATASET_REPORTING = "reporting"
BQ_TABLE_FACT = f"{PROJECT_ID}.mart.fct_registrations"
BQ_TABLE_CUSTOMER = f"{PROJECT_ID}.mart.dim_customer"
BQ_TABLE_EVENT = f"{PROJECT_ID}.mart.dim_event"
BQ_VIEW_MASTER = f"{PROJECT_ID}.reporting.v_dashboard_master"

def init_vertex():

    vertexai.init(project=PROJECT_ID, location=LOCATION)