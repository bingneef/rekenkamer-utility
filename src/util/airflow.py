import base64
import time

import requests
import os

AIRFLOW_BASE_URL = os.getenv("AIRFLOW_BASE_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")


def _headers():
    auth_base64 = base64.standard_b64encode(f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode()).decode()

    return {
        'Authorization': f'Basic {auth_base64}'
    }


def create_custom_source_job(source: str) -> bool:
    response = requests.post(
        url=f"{AIRFLOW_BASE_URL}/api/v1/dags/source_custom/dagRuns",
        json={
            "dag_run_id": str(time.time()),
            "conf": {
                'single_custom_source_name': source
            }
        },
        headers=_headers()
    )

    print(f"Created Airflow job, status code = {response.status_code}")

    return response.json()['dag_run_id']
