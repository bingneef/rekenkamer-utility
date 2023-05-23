import base64
import time

import requests
from src.util.logger import logger
import os

AIRFLOW_BASE_URL = os.getenv("AIRFLOW_BASE_URL", "http://localhost:8080")
AIRFLOW_USERNAME = os.getenv("AIRFLOW_USERNAME", "airflow")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "airflow")


def _headers():
    auth_base64 = base64.standard_b64encode(
        f"{AIRFLOW_USERNAME}:{AIRFLOW_PASSWORD}".encode()
    ).decode()

    return {"Authorization": f"Basic {auth_base64}"}


def create_custom_source_job(source: str) -> bool:
    response = requests.post(
        url=f"{AIRFLOW_BASE_URL}/api/v1/dags/source_custom/dagRuns",
        json={
            "dag_run_id": str(time.time()),
            "conf": {"single_custom_source_name": source},
        },
        headers=_headers(),
    )

    print(f"Created Airflow job, status code = {response.status_code}")

    return response.json()["dag_run_id"]


def check_custom_source_running(source: str) -> bool:
    response = requests.get(
        url=f"{AIRFLOW_BASE_URL}/api/v1/dags/source_custom/dagRuns?state=queued,running",
        headers=_headers(),
    )

    running_jobs = response.json()["dag_runs"]
    for job in running_jobs:
        # This means all sources are handled in this job
        if "conf" not in job or "single_custom_source_name" not in job["conf"]:
            return True
        if job["conf"]["single_custom_source_name"] == source:
            return True

    return False


def check_custom_source_scheduled(source: str) -> bool:
    response = requests.get(
        url=f"{AIRFLOW_BASE_URL}/api/v1/dags/source_custom/dagRuns?state=scheduled",
        headers=_headers(),
    )

    running_jobs = response.json()["dag_runs"]
    for job in running_jobs:
        # This means all sources are handled in this job
        if "conf" not in job or "single_custom_source_name" not in job["conf"]:
            return True
        if job["conf"]["single_custom_source_name"] == source:
            return True

    return False


def get_source_status(source: str) -> bool:
    response = requests.get(
        url=f"{AIRFLOW_BASE_URL}/api/v1/dags/source_{source.replace('-','_')}/dagRuns?limit=1&order_by=-start_date",
        headers=_headers(),
    )

    data = response.json()
    logger.info(data)

    jobs = data["dag_runs"]
    if len(jobs) == 0:
        return "PREPARING"

    job = jobs[0]
    if job["state"] == "running" or job["state"] == "queued":
        return "RUNNING"

    if job["state"] == "success":
        return "DONE"

    if job["state"] == "failed":
        return "FAILED"

    return "PREPARING"
