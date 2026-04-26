"""Google PageSpeed Insights API client.

Adapted from `.claude/skills/website-audit-system/scripts/pagespeed.py`.
Returns Core Web Vitals + overall score for both mobile and desktop.
"""

from __future__ import annotations

import os
import re
from typing import Optional

import requests

PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT_SECONDS = 30


def _parse_seconds(display_value: str) -> Optional[float]:
    """Parse strings like '2.4 s', '450 ms', '1,234 ms' into seconds (float)."""
    if not display_value:
        return None
    s = display_value.replace(",", "").strip().lower()
    match = re.search(r"([\d.]+)\s*(ms|s)", s)
    if not match:
        return None
    value = float(match.group(1))
    if match.group(2) == "ms":
        value /= 1000.0
    return value


def _parse_float(display_value: str) -> Optional[float]:
    """Parse strings like '0.05' into a float."""
    if not display_value:
        return None
    match = re.search(r"[\d.]+", display_value)
    return float(match.group()) if match else None


def _fetch_strategy(url: str, strategy: str, api_key: str) -> dict:
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if api_key:
        params["key"] = api_key

    try:
        resp = requests.get(PAGESPEED_URL, params=params, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        return {"score": None, "error": str(exc)}

    if resp.status_code != 200:
        return {"score": None, "error": f"HTTP {resp.status_code}"}

    data = resp.json()
    lighthouse = data.get("lighthouseResult", {}) or {}
    perf = (lighthouse.get("categories", {}) or {}).get("performance", {}) or {}
    raw_score = perf.get("score")
    score = int(raw_score * 100) if isinstance(raw_score, (int, float)) else None

    audits = lighthouse.get("audits", {}) or {}

    def display(audit_id: str) -> str:
        return (audits.get(audit_id, {}) or {}).get("displayValue", "")

    return {
        "score": score,
        "lcp_seconds": _parse_seconds(display("largest-contentful-paint")),
        "cls": _parse_float(display("cumulative-layout-shift")),
        "tbt_seconds": _parse_seconds(display("total-blocking-time")),
        "fcp_seconds": _parse_seconds(display("first-contentful-paint")),
        "si_seconds": _parse_seconds(display("speed-index")),
    }


def fetch_pagespeed_metrics(url: str, api_key: Optional[str] = None) -> dict:
    """Fetch mobile + desktop PageSpeed metrics for a URL.

    Returns dict with `mobile` and `desktop` sub-dicts. If the API call fails
    for either strategy, that sub-dict's `score` will be None — the ML model
    handles missing values natively.
    """
    api_key = api_key or os.environ.get("PAGESPEED_API_KEY", "").strip()
    return {
        "mobile": _fetch_strategy(url, "mobile", api_key),
        "desktop": _fetch_strategy(url, "desktop", api_key),
    }
