"""POST /score endpoint.

Pipeline: validate URL -> crawl -> PageSpeed -> features -> ML -> SHAP -> recommendations.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from crawler import crawl, fetch_pagespeed_metrics, normalize_url
from crawler.firecrawl_client import CrawlError
from features import extract_all
from ml import generate_recommendations, predict_score

router = APIRouter()


class ScoreRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048)

    @field_validator("url")
    @classmethod
    def normalize(cls, v: str) -> str:
        return normalize_url(v)


class ScoreResponse(BaseModel):
    ok: bool
    data: dict | None = None
    error: str | None = None


@router.post("/score", response_model=ScoreResponse)
async def score_url(req: ScoreRequest) -> ScoreResponse:
    started = time.perf_counter()

    try:
        crawl_data = crawl(req.url)
    except CrawlError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        pagespeed_data = fetch_pagespeed_metrics(req.url)
    except Exception:
        pagespeed_data = {"mobile": {}, "desktop": {}}

    features = extract_all(crawl_data, pagespeed_data)

    try:
        prediction = predict_score(features)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    recommendations = generate_recommendations(prediction["shap_values"], features)
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return ScoreResponse(
        ok=True,
        data={
            "url": crawl_data.get("url") or req.url,
            "score": prediction["score"],
            "tier": prediction["tier"],
            "sub_scores": prediction["sub_scores"],
            "shap_values": prediction["shap_values"],
            "recommendations": recommendations,
            "model_version": prediction["model_version"],
            "elapsed_ms": elapsed_ms,
        },
    )
