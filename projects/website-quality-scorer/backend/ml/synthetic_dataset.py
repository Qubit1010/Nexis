"""Generate synthetic training data for cold-start XGBoost training.

Creates feature vectors with plausible distributions, then labels them with
the heuristic scorer. The XGBoost model learns to approximate the heuristic
on tabular features — this gives us a deployable v1 model before we collect
real labeled data.

Once 100+ real labels exist, replace this with the real dataset in train.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from features.extractor import FEATURE_NAMES, FEATURE_SCHEMA
from ml.heuristic_label import heuristic_score

_RNG = np.random.default_rng(42)


def _sample_value(name: str) -> float:
    """Sample a plausible value for a given feature."""
    info = FEATURE_SCHEMA[name]
    if info["type"] == "bool":
        return float(_RNG.choice([0, 1], p=[0.4, 0.6]))

    # Per-feature plausible ranges
    ranges = {
        "ux_cta_total": (0, 12),
        "ux_cta_above_fold": (0, 4),
        "ux_nav_link_count": (3, 25),
        "ux_form_field_count": (0, 8),
        "ux_image_text_ratio": (0.0, 5.0),
        "ux_whitespace_ratio": (0.05, 0.4),
        "ux_responsive_breakpoints": (0, 6),
        "ux_total_links": (5, 100),
        "content_word_count": (50, 3000),
        "content_flesch_reading_ease": (10.0, 90.0),
        "content_flesch_kincaid_grade": (4.0, 16.0),
        "content_avg_sentence_length": (5.0, 35.0),
        "content_heading_hierarchy_score": (0.0, 1.0),
        "content_h1_count": (0, 4),
        "content_paragraph_length_std": (0.0, 200.0),
        "content_meta_description_length": (0, 200),
        "tech_pagespeed_mobile": (15, 100),
        "tech_pagespeed_desktop": (30, 100),
        "tech_lcp_seconds": (0.5, 8.0),
        "tech_cls": (0.0, 0.4),
        "tech_tbt_seconds": (0.0, 3.0),
        "tech_alt_text_coverage": (0.0, 1.0),
        "tech_external_css_count": (0, 15),
        "tech_external_js_count": (0, 30),
        "tech_page_size_kb": (50, 4000),
        "trust_social_proof_count": (0, 5),
        "trust_social_link_count": (0, 8),
    }
    lo, hi = ranges.get(name, (0, 10))
    if isinstance(lo, int) and isinstance(hi, int):
        return float(_RNG.integers(lo, hi + 1))
    return float(_RNG.uniform(lo, hi))


def generate(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate n_samples synthetic feature vectors with heuristic labels."""
    global _RNG
    _RNG = np.random.default_rng(seed)

    rows = []
    for _ in range(n_samples):
        features = {name: _sample_value(name) for name in FEATURE_NAMES}
        # Inject 3% missing values per feature to simulate real-world crawl failures
        for name in FEATURE_NAMES:
            if _RNG.random() < 0.03:
                features[name] = None
        score = heuristic_score(features)
        rows.append({**features, "score": score})

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate(1000)
    print(f"Generated {len(df)} samples")
    print(f"Score distribution: mean={df['score'].mean():.1f}, std={df['score'].std():.1f}")
    print(f"Score quantiles: {df['score'].quantile([0.1, 0.25, 0.5, 0.75, 0.9]).to_dict()}")
