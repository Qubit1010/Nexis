"""Unified Apify actor runner.

Starts an actor run, polls until complete, returns dataset items.
Consistent with the existing cold-outreach/linkedin-outreach patterns.
"""

import os
import time

import requests

APIFY_BASE = "https://api.apify.com/v2"
DEFAULT_TIMEOUT = 120  # 2 minutes per actor run


def get_api_key():
    key = os.environ.get("APIFY_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "APIFY_API_KEY not set. Add it to your .env file."
        )
    return key


def apify_run(actor_id: str, input_data: dict, timeout: int = DEFAULT_TIMEOUT, api_key: str = None) -> list:
    """Start an Apify actor run, wait for completion, return dataset items as list of dicts.

    Args:
        actor_id: Apify actor ID or slug (e.g. "hKByXkMQaC5Qt9UMN" or "harvestapi~linkedin-profile-search")
        input_data: Actor input payload dict
        timeout: Max seconds to wait before aborting (default 600)
        api_key: Apify API key — if None, reads from APIFY_API_KEY env var

    Returns:
        List of dataset item dicts

    Raises:
        RuntimeError: If actor fails or API request fails
    """
    if api_key is None:
        api_key = get_api_key()

    params = {"token": api_key}
    headers = {"Content-Type": "application/json"}

    # Start the actor run
    resp = requests.post(
        f"{APIFY_BASE}/acts/{actor_id}/runs",
        headers=headers,
        params=params,
        json=input_data,
        timeout=30,
    )
    resp.raise_for_status()

    run_data = resp.json()["data"]
    run_id = run_data["id"]
    print(f"  Apify run started: {run_id} (actor: {actor_id})", flush=True)

    # Poll until finished
    status = "RUNNING"
    deadline = time.time() + timeout
    status_resp = None

    last_status = None
    while time.time() < deadline:
        time.sleep(5)
        try:
            status_resp = requests.get(
                f"{APIFY_BASE}/actor-runs/{run_id}",
                params=params,
                timeout=15,
            )
            status_resp.raise_for_status()
            status = status_resp.json()["data"]["status"]
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code >= 500:
                continue
            raise

        if status != last_status:
            print(f"  Status: {status}", flush=True)
            last_status = status
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break

    if status == "FAILED":
        raise RuntimeError(f"Apify run {run_id} failed.")

    if status == "RUNNING":
        # Still running at deadline — abort and collect partial results
        print("  Timeout reached — aborting, using partial results...", flush=True)
        requests.post(f"{APIFY_BASE}/actor-runs/{run_id}/abort", params=params, timeout=10)
        time.sleep(3)
        status_resp = requests.get(f"{APIFY_BASE}/actor-runs/{run_id}", params=params, timeout=15)

    # Fetch dataset items
    dataset_id = status_resp.json()["data"]["defaultDatasetId"]
    limit = input_data.get("maxResults", input_data.get("maxJobs", input_data.get("limit", 100)))

    items_resp = requests.get(
        f"{APIFY_BASE}/datasets/{dataset_id}/items",
        params={**params, "format": "json", "clean": "true", "limit": limit},
        timeout=30,
    )
    items_resp.raise_for_status()

    items = items_resp.json()
    if not isinstance(items, list):
        items = []

    print(f"  Retrieved {len(items)} items.", flush=True)
    return items
