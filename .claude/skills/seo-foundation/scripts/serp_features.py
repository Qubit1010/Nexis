"""Turn a cached SERP into the observable half of the difficulty read.

The division of labour here is deliberate and it is the most important thing about this
file. `course/07` asks six questions to judge difficulty. Four are mechanical and this
script answers them. Two ("do the ranking pages actually answer the query" and "could you
be clearly better") need judgment, and a script that faked them would be worse than one
that admits it cannot.

So: **this script proposes evidence, Claude decides.** Every output is either a measured
number or an explicit `unknown`. The winnability score is a starting position to be
overridden by a human read, not a verdict.

What Serper genuinely cannot tell us (measured 2026-08-06 across 5 query shapes):
  - AI Overview presence. Never returned, at all. This is half of the click-availability
    test in `course/05`, so click availability comes back `unknown` with its observable
    components listed, and the report tells the user to check it in incognito.
  - answerBox. Effectively never returned, absent even on "what is a crm".
  - Publication dates on most results (0-5 of 10). Freshness is best-effort.

Reporting a partial answer honestly is the whole point. A fabricated "click availability:
healthy" would silently poison every downstream priority score.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import serp  # noqa: E402

# A forum or UGC result on page one is, per course/07, "the strongest opportunity signal
# there is" - Google could not find a good page. This list is the detector for that.
UGC_DOMAINS = {
    "reddit.com", "quora.com", "stackexchange.com", "stackoverflow.com", "medium.com",
    "answers.yahoo.com", "forum.", "forums.", "community.", "discussions.", "tripadvisor.com",
    "mumsnet.com", "warriorforum.com", "indiehackers.com", "producthunt.com", "substack.com",
}
# Platforms that occupy a slot without being a competitor you could displace with a page.
PLATFORM_DOMAINS = {
    "youtube.com", "wikipedia.org", "amazon.com", "facebook.com", "instagram.com",
    "linkedin.com", "pinterest.com", "twitter.com", "x.com", "tiktok.com", "apple.com",
    "play.google.com", "g2.com", "capterra.com", "trustpilot.com", "yelp.com", "glassdoor.com",
}

_LISTICLE = re.compile(r"\b(best|top|\d+\s+(best|top|great|essential|\w+\s+ideas)|vs\.?|versus|compared?|alternatives?|round ?up)\b", re.I)
# Deliberately broad. A narrow pattern buckets most of page one as "other", which makes the
# content-type mix useless for reading intent - the whole reason it is computed.
_GUIDE = re.compile(
    r"\b(how to|how do|guide|tutorial|what is|what to (wear|bring|expect|know|do)|"
    r"why|explained|tips|steps|checklist|do'?s and don'?ts|first[- ]?time[rs]?|"
    r"beginner'?s?|everything you need|faq|questions)\b", re.I)
_COMMERCIAL_PATH = re.compile(r"/(pricing|plans|buy|shop|product|services?|book|order|quote|tickets?|admission)(/|$)", re.I)
_EDITORIAL_PATH = re.compile(r"/(blog|articles?|resources?|learn|guides?|insights?|news)(/|$)", re.I)


def domain_of(url: str) -> str:
    try:
        host = (urlparse(url).netloc or "").lower()
        return host[4:] if host.startswith("www.") else host
    except ValueError:
        return ""


def _is_ugc(d: str) -> bool:
    return any(u in d for u in UGC_DOMAINS)


def _is_platform(d: str) -> bool:
    return any(p == d or d.endswith("." + p) for p in PLATFORM_DOMAINS)


def _content_type(title: str, url: str) -> str:
    """What shape of page is this? Counting these across page one is how course/04 reads
    intent: 8 of 10 listicles means a service page cannot rank here, whatever you write.

    UGC is checked first, before any title pattern. A Reddit thread titled "best ren faire
    in New England?" is a forum question, not a listicle - reading it as editorial content
    inverts the difficulty signal, because a forum on page one means Google could not find
    a good page rather than that a strong publisher owns the slot.
    """
    d = domain_of(url)
    if _is_ugc(d):
        return "forum/UGC"
    # Social and directory profiles are a distinct shape. A page one carrying several of
    # them is a brand or navigational SERP, which is a different planning problem from a
    # page one of articles - you claim those profiles rather than write a page.
    if _is_platform(d):
        return "profile/listing"
    if _LISTICLE.search(title):
        return "listicle/comparison"
    if _GUIDE.search(title):
        return "guide/how-to"
    if _COMMERCIAL_PATH.search(url):
        return "commercial page"
    if _EDITORIAL_PATH.search(url):
        return "editorial"
    path = urlparse(url).path.strip("/")
    return "homepage" if not path else "other"


def _parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip()
    m = re.match(r"(\d+)\s+(day|week|month|year)s?\s+ago", raw, re.I)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        days = {"day": 1, "week": 7, "month": 30, "year": 365}[unit] * n
        return datetime.now(timezone.utc).fromtimestamp(
            datetime.now(timezone.utc).timestamp() - days * 86400, tz=timezone.utc)
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def analyze(query: str, data: dict, *, client_domain: str | None = None) -> dict:
    """One SERP -> the evidence row. Nothing here is a guess; unknown stays unknown."""
    organic = (data.get("organic") or [])[:10]
    urls = [r.get("link", "") for r in organic if r.get("link")]
    domains = [domain_of(u) for u in urls if u]
    n = len(domains)

    unique = sorted(set(d for d in domains if d))
    diversity = round(len(unique) / n, 2) if n else 0.0

    ugc_positions = [i + 1 for i, d in enumerate(domains) if _is_ugc(d)]
    ugc_top5 = [p for p in ugc_positions if p <= 5]
    platform_count = sum(1 for d in domains if _is_platform(d))

    # Sitelinks are Google volunteering that it considers a result a known destination.
    # Not authority per se, but the closest observable proxy for "big recognizable brand".
    sitelinked = sum(1 for r in organic if r.get("sitelinks"))

    types = Counter(_content_type(r.get("title", ""), r.get("link", "")) for r in organic)
    dominant_type, dominant_n = (types.most_common(1)[0] if types else ("unknown", 0))

    dates = [_parse_date(r.get("date")) for r in organic]
    dated = [d for d in dates if d]
    if dated:
        now = datetime.now(timezone.utc)
        median_age_days = int(sorted((now - d).days for d in dated)[len(dated) // 2])
        freshness = (f"{len(dated)}/{n} dated, median {median_age_days}d old"
                     if n else "no results")
    else:
        median_age_days, freshness = None, f"0/{n} results carry a date - freshness unknown"

    paa = data.get("peopleAlsoAsk") or []
    related = data.get("relatedSearches") or []

    # ---- winnability, 1-5, from the four mechanical questions of course/07 ----
    # Calibrated against a live 10-query run where the first version pinned 7 of 10 at 5.0.
    # In community-heavy niches UGC appears on almost every SERP, so a flat large bonus
    # stops discriminating exactly where the score is supposed to be most useful. The
    # signal is now position-weighted and depth-weighted: one forum result at #8 is a
    # different fact from four of them in the top five.
    score, reasons = 2.5, []
    if ugc_positions:
        first = ugc_positions[0]
        if first <= 3:
            score += 1.25; reasons.append(f"UGC at position {first} - strongest opportunity signal")
        elif first <= 5:
            score += 0.9; reasons.append(f"UGC at position {first}, inside the top five")
        else:
            score += 0.5; reasons.append(f"UGC on page one at position {first}")
        extra = min(len(ugc_positions) - 1, 3) * 0.25
        if extra:
            score += extra
            reasons.append(f"{len(ugc_positions)} UGC results on page one - Google is "
                           f"struggling to find authoritative pages here")
    if diversity >= 0.9:
        score += 0.5; reasons.append(f"open SERP, {len(unique)} distinct domains")
    elif diversity and diversity <= 0.6:
        score -= 1.0; reasons.append(f"consolidated, only {len(unique)} domains across {n} slots")
    elif diversity and diversity <= 0.75:
        score -= 0.5; reasons.append(f"semi-consolidated, {len(unique)} domains across {n} slots")
    if sitelinked >= 4:
        score -= 1.0; reasons.append(f"{sitelinked}/{n} results carry sitelinks - brand-heavy")
    elif sitelinked <= 1 and n:
        score += 0.25; reasons.append("few sitelinks - not a brand-dominated SERP")
    if platform_count >= 4:
        score -= 0.5; reasons.append(f"{platform_count} slots held by major platforms")
    if median_age_days is not None and median_age_days > 730:
        score += 0.5; reasons.append(f"stale page one, median {median_age_days}d")
    winnability = max(1.0, min(5.0, round(score * 2) / 2))

    # Whether the client already ranks changes the question entirely - from "can we win
    # this" to "are we defending it". Without this, a query the client already owns at #1
    # scores like a fresh opportunity and gets planned as new content.
    client_pos = None
    if client_domain:
        cd = client_domain.lower().replace("www.", "")
        for i, d in enumerate(domains):
            if d and (d == cd or d.endswith("." + cd) or cd in d):
                client_pos = i + 1
                break

    return {
        "query": query,
        "results_analyzed": n,
        "top_domains": unique[:6],
        "domain_diversity": diversity,
        "ugc_on_page1": bool(ugc_positions),
        "ugc_positions": ugc_positions,
        "platform_slots": platform_count,
        "sitelinked_results": sitelinked,
        "dominant_content_type": f"{dominant_type} ({dominant_n}/{n})" if n else "unknown",
        "content_type_mix": dict(types),
        "freshness": freshness,
        "median_age_days": median_age_days,
        "paa_count": len(paa),
        "paa_questions": [p.get("question", "") for p in paa if p.get("question")],
        "related_searches": [r.get("query", "") for r in related if r.get("query")],
        "answer_box": bool(data.get("answerBox")),
        # Honest unknowns. See the module docstring for why these are not guessed.
        "ai_overview": "unknown - not returned by this data source, check manually in incognito",
        "click_availability": "unknown - requires an AI Overview check; see observable_signals",
        "observable_signals": {
            "paa_blocks": len(paa),
            "related_blocks": len(related),
            "answer_box_present": bool(data.get("answerBox")),
            "note": "Feature blocks push organic down. 3+ means organic is a minority of the page.",
        },
        "winnability_1_5": winnability,
        "winnability_reasons": reasons,
        "client_position": client_pos,
        "client_status": (None if not client_domain else
                          f"already ranking at position {client_pos} - defend, do not rebuild"
                          if client_pos else "not on page one"),
        "needs_human_read": [
            "Do the ranking pages actually answer the query?",
            "Could you be clearly better, not marginally?",
        ],
        "cached": bool(data.get("_meta", {}).get("cached")),
    }


def analyze_many(queries: list[str], *, gl: str = "us", hl: str = "en",
                 refresh: bool = False, client_domain: str | None = None) -> list[dict]:
    serps = serp.fetch_many(queries, gl=gl, hl=hl, refresh=refresh)
    return [analyze(q, serps[q], client_domain=client_domain) for q in queries if q in serps]


def main() -> int:
    ap = argparse.ArgumentParser(description="Read SERP features and a difficulty proxy.")
    ap.add_argument("query", nargs="?")
    ap.add_argument("--file", help="text file, one query per line")
    ap.add_argument("--gl", default="us"); ap.add_argument("--hl", default="en")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--client-domain", help="flag queries the client already ranks for")
    ap.add_argument("--out", help="write JSON results here")
    args = ap.parse_args()

    if args.file:
        queries = [l.strip() for l in Path(args.file).read_text(encoding="utf-8").splitlines() if l.strip()]
    elif args.query:
        queries = [args.query]
    else:
        ap.error("query or --file required")

    rows = analyze_many(queries, gl=args.gl, hl=args.hl, refresh=args.refresh,
                        client_domain=args.client_domain)
    payload = json.dumps(rows, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"wrote {len(rows)} rows -> {args.out}")
    else:
        print(payload)
    print(f"\n{serp.cost_report()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
