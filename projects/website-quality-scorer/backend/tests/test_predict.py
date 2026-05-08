"""Smoke tests for ML inference + recommendations.

Skipped if no trained model exists. Run `python -m ml.train` first.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from features.extractor import FEATURE_NAMES
from ml.predict import _model_path
from ml.recommendations import generate_recommendations


pytestmark = pytest.mark.skipif(
    not _model_path().exists(),
    reason="Run `python -m ml.train` first to create the model.",
)


def _good_features() -> dict:
    """Strong website signals."""
    return {
        "ux_cta_total": 6, "ux_cta_above_fold": 2, "ux_nav_link_count": 8,
        "ux_form_field_count": 2, "ux_image_text_ratio": 0.5,
        "ux_whitespace_ratio": 0.18, "ux_viewport_meta": 1,
        "ux_responsive_breakpoints": 4, "ux_has_hero_section": 1,
        "ux_total_links": 25,
        "content_word_count": 850, "content_flesch_reading_ease": 65.0,
        "content_flesch_kincaid_grade": 8.0, "content_avg_sentence_length": 15.0,
        "content_heading_hierarchy_score": 0.95, "content_h1_count": 1,
        "content_h1_unique": 1, "content_paragraph_length_std": 50.0,
        "content_value_prop_detected": 1, "content_meta_description_length": 145,
        "tech_pagespeed_mobile": 92, "tech_pagespeed_desktop": 98,
        "tech_lcp_seconds": 1.2, "tech_cls": 0.02, "tech_tbt_seconds": 0.1,
        "tech_https": 1, "tech_schema_markup": 1, "tech_alt_text_coverage": 0.95,
        "tech_external_css_count": 2, "tech_external_js_count": 4,
        "tech_page_size_kb": 450,
        "trust_testimonials": 1, "trust_client_logos": 1,
        "trust_social_proof_count": 3, "trust_phone_visible": 1,
        "trust_email_visible": 1, "trust_address_visible": 1,
        "trust_privacy_link": 1, "trust_social_link_count": 4,
        "trust_has_video": 1, "trust_has_pricing": 1,
    }


def _weak_features() -> dict:
    """Weak signals — should produce a low score with many recommendations."""
    return {name: 0 for name in FEATURE_NAMES} | {
        "tech_pagespeed_mobile": 28, "tech_pagespeed_desktop": 41,
        "tech_lcp_seconds": 6.0, "tech_cls": 0.3, "tech_tbt_seconds": 1.8,
        "tech_alt_text_coverage": 0.1, "tech_page_size_kb": 3200,
        "content_word_count": 50, "content_flesch_reading_ease": 35.0,
        "content_flesch_kincaid_grade": 14.0,
    }


def test_predict_score_returns_complete_response():
    from ml.predict import predict_score
    result = predict_score(_good_features())
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert result["tier"] in ("Poor", "Average", "Good", "Excellent")
    assert set(result["sub_scores"].keys()) == {"ux", "content", "technical", "trust"}
    assert len(result["shap_values"]) > 0


def test_predict_score_higher_for_strong_features():
    from ml.predict import predict_score
    good = predict_score(_good_features())
    weak = predict_score(_weak_features())
    assert good["score"] > weak["score"], (
        f"Expected strong features to score higher: good={good['score']} weak={weak['score']}"
    )


def test_recommendations_generated_for_weak_site():
    from ml.predict import predict_score
    features = _weak_features()
    pred = predict_score(features)
    recs = generate_recommendations(pred["shap_values"], features)
    assert len(recs) > 0
    assert all("title" in r and "rationale" in r and "priority" in r for r in recs)
