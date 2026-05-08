"""FastAPI app entry point.

Run:
    cd backend
    uvicorn main:app --reload
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent / ".env")

from api.score_endpoint import router as score_router  # noqa: E402

app = FastAPI(
    title="Website Quality & Conversion Gap Scorer",
    description="ML-driven website scoring with SHAP-based explainability",
    version="1.0.0",
)

allowed_origins = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(score_router)


@app.get("/health")
def health() -> dict:
    from ml.predict import _model_path
    return {
        "ok": True,
        "model_exists": _model_path().exists(),
        "version": "1.0.0",
    }


@app.get("/")
def root() -> dict:
    return {
        "name": "website-quality-scorer",
        "endpoints": {"POST /score": "Score a URL", "GET /health": "Health check"},
    }
