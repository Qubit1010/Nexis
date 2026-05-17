# EDA Report — `data/labeled/dataset.csv`

_Generated automatically by `scripts/eda.py` — re-run to refresh._

## 1. Dataset shape

- Rows: **221**
- Features: **41** (UX=10, Content=10, Technical=11, Trust=10)
- Numeric features: **27**, boolean features: **14**

## 2. Target statistics (`score_total`)

- Mean: **43.99** | Median: **44.46** | Std: **10.97**
- Min: **16.60** | Max: **71.01** | Range: **54.41**
- Skewness: **-0.195** | Kurtosis: **-0.601**

**Tier counts:**

- Poor (0-25): **11** (5.0%)
- Average (26-50): **138** (62.4%)
- Good (51-75): **72** (32.6%)
- Excellent (76-100): **0** (0.0%)

## 3. Missing-value summary

Total NaN cells in feature matrix: **612** / 9061 possible (6.75%).

Top 10 columns by missing %:

- `tech_pagespeed_desktop` — **56.1%** missing
- `tech_pagespeed_mobile` — **55.2%** missing
- `tech_cls` — **55.2%** missing
- `tech_tbt_seconds` — **55.2%** missing
- `tech_lcp_seconds` — **55.2%** missing

## 4. Constant / near-constant features

- `ux_viewport_meta`
- `ux_responsive_breakpoints`
- `tech_https`
- `tech_external_js_count`
- `trust_address_visible`

## 5. Top-15 features by |Pearson r| with `score_total`

| Rank | Feature | Dim | Pearson r | Spearman r |
|------|---------|-----|-----------|------------|
| 1 | `content_heading_hierarchy_score` | content | +0.617 | +0.585 |
| 2 | `content_h1_unique` | content | +0.570 | +0.578 |
| 3 | `trust_has_pricing` | trust | +0.541 | +0.542 |
| 4 | `trust_testimonials` | trust | +0.528 | +0.528 |
| 5 | `ux_cta_total` | ux | +0.509 | +0.601 |
| 6 | `content_value_prop_detected` | content | +0.506 | +0.511 |
| 7 | `content_paragraph_length_std` | content | +0.484 | +0.577 |
| 8 | `tech_pagespeed_mobile` | technical | +0.468 | +0.458 |
| 9 | `trust_client_logos` | trust | +0.414 | +0.400 |
| 10 | `ux_has_hero_section` | ux | +0.391 | +0.396 |
| 11 | `content_word_count` | content | +0.352 | +0.523 |
| 12 | `tech_tbt_seconds` | technical | -0.272 | -0.238 |
| 13 | `ux_cta_above_fold` | ux | +0.256 | +0.318 |
| 14 | `content_h1_count` | content | +0.255 | +0.483 |
| 15 | `trust_has_video` | trust | +0.252 | +0.259 |

## 6. High-correlation feature pairs (|r| > 0.85)

| Feature A | Feature B | Dim A | Dim B | Pearson r |
|-----------|-----------|-------|-------|-----------|
| `content_flesch_reading_ease` | `content_flesch_kincaid_grade` | content | content | -1.000 |

## 7. Skewness flags (|skew| > 1)

| Feature | Skew |
|---------|------|
| `content_flesch_reading_ease` | -14.86 |
| `content_flesch_kincaid_grade` | +14.86 |
| `ux_responsive_breakpoints` | +10.44 |
| `tech_external_css_count` | +7.70 |
| `trust_social_proof_count` | +7.50 |
| `ux_image_text_ratio` | +4.82 |
| `ux_form_field_count` | +4.71 |
| `content_avg_sentence_length` | +3.96 |
| `tech_cls` | +3.82 |
| `tech_lcp_seconds` | +3.68 |
| `content_h1_count` | +3.68 |
| `tech_page_size_kb` | -3.57 |
| `content_meta_description_length` | +3.45 |
| `trust_social_link_count` | +3.45 |
| `ux_whitespace_ratio` | +3.29 |
| `ux_cta_above_fold` | +2.51 |
| `content_word_count` | +2.25 |
| `ux_nav_link_count` | +2.05 |
| `tech_tbt_seconds` | +2.01 |
| `ux_total_links` | +1.94 |
| `ux_cta_total` | +1.72 |
| `content_paragraph_length_std` | +1.48 |

## 8. Outliers (IQR method, 1.5×IQR rule)

Top 15 continuous features by outlier count:

| Feature | Outlier count | Outlier % |
|---------|---------------|-----------|
| `content_meta_description_length` | 39 | 17.6% |
| `content_flesch_kincaid_grade` | 31 | 14.0% |
| `content_flesch_reading_ease` | 27 | 12.2% |
| `content_avg_sentence_length` | 23 | 10.4% |
| `ux_whitespace_ratio` | 22 | 10.0% |
| `ux_form_field_count` | 21 | 9.5% |
| `ux_cta_above_fold` | 19 | 8.6% |
| `ux_nav_link_count` | 18 | 8.1% |
| `tech_cls` | 17 | 17.2% |
| `ux_image_text_ratio` | 16 | 7.2% |
| `ux_total_links` | 9 | 4.1% |
| `content_paragraph_length_std` | 9 | 4.1% |
| `content_h1_count` | 8 | 3.6% |
| `tech_tbt_seconds` | 7 | 7.1% |
| `ux_cta_total` | 6 | 2.7% |

## 9. Sub-score inter-correlation

| | score_ux | score_content | score_technical | score_trust |
|---|---|---|---|---|
| **score_ux** | +1.00 | +0.27 | -0.10 | +0.24 |
| **score_content** | +0.27 | +1.00 | +0.13 | +0.45 |
| **score_technical** | -0.10 | +0.13 | +1.00 | +0.07 |
| **score_trust** | +0.24 | +0.45 | +0.07 | +1.00 |

## 10. Preprocessing recommendations

- **Missing values:** PageSpeed columns are >30% missing (tech_pagespeed_mobile (55%), tech_pagespeed_desktop (56%), tech_lcp_seconds (55%), tech_cls (55%), tech_tbt_seconds (55%)). Recommendation: keep as NaN — XGBoost handles missing natively (see [backend/ml/preprocessing.py](../../backend/ml/preprocessing.py)). If switching to a non-tree model, apply median imputation per column.

- **Skew correction:** 22 continuous features have |skew| > 1 — apply `np.log1p` before training:
  - `content_flesch_reading_ease` (skew=-14.86)
  - `content_flesch_kincaid_grade` (skew=14.86)
  - `ux_responsive_breakpoints` (skew=10.44)
  - `tech_external_css_count` (skew=7.70)
  - `trust_social_proof_count` (skew=7.50)
  - `ux_image_text_ratio` (skew=4.82)
  - `ux_form_field_count` (skew=4.71)
  - `content_avg_sentence_length` (skew=3.96)
  - `tech_cls` (skew=3.82)
  - `tech_lcp_seconds` (skew=3.68)
  - `content_h1_count` (skew=3.68)
  - `tech_page_size_kb` (skew=-3.57)
  - `content_meta_description_length` (skew=3.45)
  - `trust_social_link_count` (skew=3.45)
  - `ux_whitespace_ratio` (skew=3.29)
  - `ux_cta_above_fold` (skew=2.51)
  - `content_word_count` (skew=2.25)
  - `ux_nav_link_count` (skew=2.05)
  - `tech_tbt_seconds` (skew=2.01)
  - `ux_total_links` (skew=1.94)
  - `ux_cta_total` (skew=1.72)
  - `content_paragraph_length_std` (skew=1.48)

- **Multicollinearity:** No cross-dimension feature pair exceeds |r| > 0.85 — keep all features.

- **Constant/near-constant features:** `ux_viewport_meta`, `ux_responsive_breakpoints`, `tech_https`, `tech_external_js_count`, `trust_address_visible` — drop before training.

- **Class imbalance:** Poor (0-25), Excellent (76-100) tiers each hold <10% of samples. Recommendation: stratify train/test split on tier label and use stratified k-fold during CV (see [backend/ml/train.py:78](../../backend/ml/train.py#L78)).

- **Scaling:** Continuous features → StandardScaler; booleans → passthrough. XGBoost is scale-invariant so this is optional for the deployed model, but required if benchmarking against linear models or k-NN.

## Figures

All saved under [`figures/`](figures/):

- ![01_target_total_distribution](figures/01_target_total_distribution.png)
- ![02_subscore_distributions](figures/02_subscore_distributions.png)
- ![03_tier_pie](figures/03_tier_pie.png)
- ![04_missing_values](figures/04_missing_values.png)
- ![05a_ux_feature_distributions](figures/05a_ux_feature_distributions.png)
- ![05b_content_feature_distributions](figures/05b_content_feature_distributions.png)
- ![05c_technical_feature_distributions](figures/05c_technical_feature_distributions.png)
- ![05d_trust_feature_distributions](figures/05d_trust_feature_distributions.png)
- ![06_boolean_feature_counts](figures/06_boolean_feature_counts.png)
- ![07_correlation_heatmap](figures/07_correlation_heatmap.png)
- ![08_feature_target_correlation](figures/08_feature_target_correlation.png)
- ![09_top_features_scatter](figures/09_top_features_scatter.png)
- ![10_boxplots_continuous](figures/10_boxplots_continuous.png)
- ![11_subscore_pairplot](figures/11_subscore_pairplot.png)
- ![12_skewness_bars](figures/12_skewness_bars.png)
- ![13_pca_scatter](figures/13_pca_scatter.png)
- ![14_score_total_by_boolean](figures/14_score_total_by_boolean.png)
