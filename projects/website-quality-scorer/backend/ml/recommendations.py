"""Map SHAP values to actionable recommendation templates.

Each template targets a specific feature and is triggered when:
  1. The feature's SHAP contribution is sufficiently negative (hurting score)
  2. The raw feature value falls below a "weak" threshold

The top N most-negative recommendations are returned to the user.
"""

from __future__ import annotations

from typing import Optional

# Template format:
#   feature -> {
#       title: short imperative ("Add testimonials")
#       rationale: one-liner explaining the gap and impact
#       weak_when: lambda(raw_value) -> bool (True if recommendation should fire)
#   }

TEMPLATES = {
    # UX
    "ux_cta_above_fold": {
        "title": "Add a primary call-to-action above the fold",
        "rationale": "No clear CTA was detected in the hero section. Above-the-fold CTAs improve click-through by 20-40%.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "ux_cta_total": {
        "title": "Increase the number of clear calls-to-action",
        "rationale": "The page has very few action-oriented buttons. Strong landing pages typically have 3-6 CTAs.",
        "weak_when": lambda v: v is None or v < 2,
    },
    "ux_viewport_meta": {
        "title": "Add a mobile viewport meta tag",
        "rationale": "Missing viewport meta tag — the site won't render correctly on mobile. Add `<meta name='viewport' ...>`.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "ux_has_hero_section": {
        "title": "Build a clear hero section",
        "rationale": "No hero section detected. A focused hero with headline + value prop + CTA significantly improves conversion.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "ux_responsive_breakpoints": {
        "title": "Add responsive design breakpoints",
        "rationale": "Few or no media-query breakpoints detected. Add CSS breakpoints for mobile, tablet, and desktop.",
        "weak_when": lambda v: v is None or v < 2,
    },

    # Content
    "content_value_prop_detected": {
        "title": "State your value proposition clearly",
        "rationale": "No clear value-prop language detected. Lead with what you do, who it's for, and the outcome.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "content_h1_unique": {
        "title": "Use exactly one H1 tag with your primary message",
        "rationale": "Multiple H1s or no H1 detected. Search engines and accessibility tools expect one H1 per page.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "content_flesch_reading_ease": {
        "title": "Simplify your copy",
        "rationale": "Reading ease score is low. Aim for Flesch score 60+ — short sentences, common words, active voice.",
        "weak_when": lambda v: v is None or v < 50,
    },
    "content_word_count": {
        "title": "Add more substantive content",
        "rationale": "Page content is thin. Expand to 300-800 words covering benefits, use cases, and credibility.",
        "weak_when": lambda v: v is None or v < 200,
    },
    "content_meta_description_length": {
        "title": "Write a compelling meta description",
        "rationale": "Missing or short meta description. Target 140-160 characters with the value prop and a soft CTA.",
        "weak_when": lambda v: v is None or v < 50,
    },
    "content_heading_hierarchy_score": {
        "title": "Fix heading hierarchy",
        "rationale": "Heading levels are out of order or jumping. Use H1 → H2 → H3 sequentially for SEO and accessibility.",
        "weak_when": lambda v: v is None or v < 0.6,
    },

    # Technical
    "tech_pagespeed_mobile": {
        "title": "Improve mobile performance",
        "rationale": "Mobile PageSpeed score is low. Optimize images, defer JS, and minimize render-blocking CSS.",
        "weak_when": lambda v: v is None or v < 60,
    },
    "tech_lcp_seconds": {
        "title": "Reduce Largest Contentful Paint",
        "rationale": "LCP is too slow. Compress hero image, preload critical resources, and use a CDN.",
        "weak_when": lambda v: v is None or v > 2.5,
    },
    "tech_cls": {
        "title": "Fix layout shift issues",
        "rationale": "Cumulative Layout Shift is high. Reserve space for images and ads to prevent content jumping.",
        "weak_when": lambda v: v is not None and v > 0.1,
    },
    "tech_https": {
        "title": "Enable HTTPS",
        "rationale": "Site is not served over HTTPS. This hurts trust signals, conversions, and SEO ranking.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "tech_alt_text_coverage": {
        "title": "Add alt text to all images",
        "rationale": "Many images are missing alt attributes. Critical for accessibility and image SEO.",
        "weak_when": lambda v: v is None or v < 0.7,
    },
    "tech_schema_markup": {
        "title": "Add structured data (schema markup)",
        "rationale": "No structured data detected. Add JSON-LD schema for richer search results.",
        "weak_when": lambda v: v is None or v == 0,
    },

    # Trust
    "trust_testimonials": {
        "title": "Add testimonials or reviews",
        "rationale": "No testimonial section detected. Adding 2-3 client quotes can lift conversion 10-20%.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_client_logos": {
        "title": "Display client or partner logos",
        "rationale": "Missing social proof via client logos. A 'Trusted by' strip with 4-6 logos builds instant credibility.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_phone_visible": {
        "title": "Show a contact phone number",
        "rationale": "No phone number detected on the page. Even if you don't take calls, visible contact info builds trust.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_email_visible": {
        "title": "Show a contact email address",
        "rationale": "No contact email detected. Add at least one visible support or sales email.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_privacy_link": {
        "title": "Link to a privacy policy",
        "rationale": "No privacy policy link found. Required for GDPR compliance and a basic trust signal.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_has_pricing": {
        "title": "Add transparent pricing information",
        "rationale": "No pricing page or pricing language detected. Even ranges or 'starting at' anchors help qualify leads.",
        "weak_when": lambda v: v is None or v == 0,
    },
    "trust_social_proof_count": {
        "title": "Add specific social proof numbers",
        "rationale": "No quantitative social proof (e.g., '500+ customers'). Specific numbers outperform generic claims.",
        "weak_when": lambda v: v is None or v == 0,
    },
}


def _impact_label(shap_value: float) -> str:
    """Convert SHAP magnitude into a rough impact estimate."""
    abs_val = abs(shap_value)
    if abs_val < 0.5:
        return "+1 to +3 score points"
    if abs_val < 1.5:
        return "+3 to +6 score points"
    if abs_val < 3.0:
        return "+6 to +10 score points"
    return "+10 to +15 score points"


def generate_recommendations(
    shap_values: list[dict],
    features: dict,
    max_recommendations: int = 5,
) -> list[dict]:
    """Build a ranked list of recommendations from SHAP values.

    Logic: pick features with negative SHAP contribution where the raw value
    falls below the template's `weak_when` threshold. Rank by SHAP magnitude.
    """
    recs: list[tuple[float, dict]] = []

    for entry in shap_values:
        feature = entry["feature"]
        shap_val = entry["shap_value"]
        raw = features.get(feature)

        if shap_val >= 0:
            continue

        template = TEMPLATES.get(feature)
        if not template:
            continue

        try:
            if not template["weak_when"](raw):
                continue
        except Exception:
            continue

        recs.append((shap_val, {
            "feature": feature,
            "title": template["title"],
            "rationale": template["rationale"],
            "impact": _impact_label(shap_val),
            "dimension": entry.get("dimension"),
        }))

    recs.sort(key=lambda x: x[0])  # most negative first

    return [
        {**rec, "priority": idx + 1}
        for idx, (_, rec) in enumerate(recs[:max_recommendations])
    ]
