"""Master feature extraction pipeline.

Combines UX, content, technical, and trust feature extractors into a single
40-feature dictionary used by the ML model.
"""

from __future__ import annotations

from . import content_features, technical_features, trust_features, ux_features

# Canonical feature schema. Order matters — used to build the feature vector
# fed to the ML model. Any additions/removals must update train.py and predict.py
# in sync.
FEATURE_SCHEMA: dict[str, dict] = {
    # UX dimension (10)
    "ux_cta_total":              {"dim": "ux", "type": "num"},
    "ux_cta_above_fold":         {"dim": "ux", "type": "num"},
    "ux_nav_link_count":         {"dim": "ux", "type": "num"},
    "ux_form_field_count":       {"dim": "ux", "type": "num"},
    "ux_image_text_ratio":       {"dim": "ux", "type": "num"},
    "ux_whitespace_ratio":       {"dim": "ux", "type": "num"},
    "ux_viewport_meta":          {"dim": "ux", "type": "bool"},
    "ux_responsive_breakpoints": {"dim": "ux", "type": "num"},
    "ux_has_hero_section":       {"dim": "ux", "type": "bool"},
    "ux_total_links":            {"dim": "ux", "type": "num"},
    # Content dimension (10)
    "content_word_count":               {"dim": "content", "type": "num"},
    "content_flesch_reading_ease":      {"dim": "content", "type": "num"},
    "content_flesch_kincaid_grade":     {"dim": "content", "type": "num"},
    "content_avg_sentence_length":      {"dim": "content", "type": "num"},
    "content_heading_hierarchy_score":  {"dim": "content", "type": "num"},
    "content_h1_count":                 {"dim": "content", "type": "num"},
    "content_h1_unique":                {"dim": "content", "type": "bool"},
    "content_paragraph_length_std":     {"dim": "content", "type": "num"},
    "content_value_prop_detected":      {"dim": "content", "type": "bool"},
    "content_meta_description_length":  {"dim": "content", "type": "num"},
    # Technical dimension (11 — pagespeed split)
    "tech_pagespeed_mobile":     {"dim": "technical", "type": "num"},
    "tech_pagespeed_desktop":    {"dim": "technical", "type": "num"},
    "tech_lcp_seconds":          {"dim": "technical", "type": "num"},
    "tech_cls":                  {"dim": "technical", "type": "num"},
    "tech_tbt_seconds":          {"dim": "technical", "type": "num"},
    "tech_https":                {"dim": "technical", "type": "bool"},
    "tech_schema_markup":        {"dim": "technical", "type": "bool"},
    "tech_alt_text_coverage":    {"dim": "technical", "type": "num"},
    "tech_external_css_count":   {"dim": "technical", "type": "num"},
    "tech_external_js_count":    {"dim": "technical", "type": "num"},
    "tech_page_size_kb":         {"dim": "technical", "type": "num"},
    # Trust dimension (10)
    "trust_testimonials":        {"dim": "trust", "type": "bool"},
    "trust_client_logos":        {"dim": "trust", "type": "bool"},
    "trust_social_proof_count":  {"dim": "trust", "type": "num"},
    "trust_phone_visible":       {"dim": "trust", "type": "bool"},
    "trust_email_visible":       {"dim": "trust", "type": "bool"},
    "trust_address_visible":     {"dim": "trust", "type": "bool"},
    "trust_privacy_link":        {"dim": "trust", "type": "bool"},
    "trust_social_link_count":   {"dim": "trust", "type": "num"},
    "trust_has_video":           {"dim": "trust", "type": "bool"},
    "trust_has_pricing":         {"dim": "trust", "type": "bool"},
}

FEATURE_NAMES = list(FEATURE_SCHEMA.keys())


def features_by_dimension(dimension: str) -> list[str]:
    return [name for name, info in FEATURE_SCHEMA.items() if info["dim"] == dimension]


def extract_all(crawl_data: dict, pagespeed_data: dict) -> dict:
    """Run all feature extractors and return a flat dict matching FEATURE_SCHEMA.

    Missing values remain as None — XGBoost handles NaN natively.
    """
    features: dict = {}
    features.update(ux_features.extract(crawl_data))
    features.update(content_features.extract(crawl_data))
    features.update(technical_features.extract(crawl_data, pagespeed_data))
    features.update(trust_features.extract(crawl_data))

    for name in FEATURE_NAMES:
        features.setdefault(name, None)

    return {name: features[name] for name in FEATURE_NAMES}
