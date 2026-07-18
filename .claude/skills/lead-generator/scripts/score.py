"""Lead quality score, 1-10, from a directory row's rating + review count.

Volume-weighted, per Aleem 2026-07-17: a high star rating on very few reviews is not trustworthy, so
review VOLUME must be able to overcome a small rating gap. A proven 4.8 with 92 reviews outranks both an
untested 5.0 with 2 reviews AND a 4.9 with only 40 reviews. Score blends two 0-10 components:

    rating_component = R / 5 * 10                                  # the raw star quality
    volume_component = min(log10(v+1) / log10(VOL_REF+1), 1) * 10  # log-scaled review count, capped
    score            = clamp(round(0.7*rating_component + 0.3*volume_component, 1), 1.0, 10.0)

R = rating (0-5), v = review count, VOL_REF = the review count that earns full volume credit (~100).
Log scale so the jump from 2->40 reviews matters far more than 200->240. A textbook Bayesian shrink toward
the batch mean was tried first but FAILED the requirement: when the batch mean (say 4.9) exceeds an
established agency's own rating (4.8), shrinking a thin 5.0 toward the mean still leaves it above the
4.8 -- so volume never wins. The explicit blend below makes volume a real, separate term. A row with no
rating can't be vouched for, so it floors to 1.0 rather than getting a fabricated number.
"""
from __future__ import annotations

import argparse
import math
import re


VOL_REF = 100.0     # review count that earns full (10/10) volume credit; more caps at 10
W_RATING = 0.7      # rating still dominates
W_VOLUME = 0.3      # but volume is a real, separate term (this is what sinks thin 5.0s)


def _num(val) -> float | None:
    """First number in a cell ('4.9', '52 reviews', '$5,000+') -> float, else None."""
    if val is None:
        return None
    m = re.search(r"\d+(?:\.\d+)?", str(val).replace(",", ""))
    return float(m.group(0)) if m else None


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def score_one(rating, reviews) -> float:
    """1-10 score for a single (rating, reviews) pair. No rating -> 1.0 (never invented)."""
    R = _num(rating)
    if R is None:
        return 1.0
    v = _num(reviews) or 0.0
    rating_component = R / 5.0 * 10.0
    volume_component = min(math.log10(v + 1) / math.log10(VOL_REF + 1), 1.0) * 10.0
    return _clamp(round(W_RATING * rating_component + W_VOLUME * volume_component, 1), 1.0, 10.0)


def score_batch(rows: list[dict], *, rating_key: str = "rating", reviews_key: str = "reviews",
                out_key: str = "score") -> list[dict]:
    """Attach a 1-10 `score` to each row in place (also returned)."""
    for row in rows:
        row[out_key] = score_one(row.get(rating_key), row.get(reviews_key))
    return rows


def demo():
    """Self-check: the locked ordering (volume beats a thin 5.0 and a lower-volume 4.9) + edges."""
    rows = [
        {"company": "Established", "rating": "4.8", "reviews": "92"},
        {"company": "Thin",        "rating": "5.0", "reviews": "2"},
        {"company": "Solid",       "rating": "4.9", "reviews": "40"},
        {"company": "NoRating",    "rating": "",    "reviews": ""},
    ]
    score_batch(rows)
    by = {r["company"]: r["score"] for r in rows}
    # The whole point: a proven 4.8/92 outranks BOTH an untested 5.0/2 and a lower-volume 4.9/40.
    assert by["Established"] > by["Solid"] > by["Thin"], by
    # No rating -> floored, never invented.
    assert by["NoRating"] == 1.0, by
    # All within the 1-10 band.
    assert all(1.0 <= r["score"] <= 10.0 for r in rows), by
    # More reviews at the same rating always scores at least as high.
    assert score_one("4.9", "200") >= score_one("4.9", "40") >= score_one("4.9", "3"), "monotonic in volume"
    # Parsing tolerates messy cells.
    assert _num("52 reviews") == 52.0 and _num("$5,000+") == 5000.0 and _num("") is None
    print("score self-check OK:", by)


def main():
    p = argparse.ArgumentParser(description="Volume-weighted 1-10 lead score from rating + reviews.")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--rating", type=str, help="ad-hoc: a rating to score")
    p.add_argument("--reviews", type=str, default="", help="ad-hoc: its review count")
    args = p.parse_args()
    if args.selftest:
        demo()
        return
    if args.rating is not None:
        print(score_one(args.rating, args.reviews))
        return
    p.error("pass --selftest or --rating")


if __name__ == "__main__":
    main()
