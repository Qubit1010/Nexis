"""AI visibility sampler: how often does an answer engine cite or name this brand?

The only genuinely new capability in the SEO skill family. Every sibling measures a page;
this measures an *engine's behaviour*, which is a distribution, not a value.

Why the multi-run protocol is not optional
------------------------------------------
Live spike, 2026-08-08, two runs of one prompt on ChatGPT seconds apart:

    run 1 -> "HubSpot CRM is the best all-around choice"   sources: 0
    run 2 -> "my top pick is Pipedrive"                    sources: 50
    cited-domain Jaccard overlap between the two runs:     0.00

Sampling once would have produced two opposite, equally confident, equally wrong reports.
arXiv 2604.07585 ("Don't Measure Once", Apr 2026) decomposed 12,933 responses: within-prompt
resampling is 34.8% of total variance; brand identity itself is 1.5%. Under 3 runs you are
measuring the sampler, not the brand. `--runs` below MIN_RUNS is refused.

What the spike also showed, which shapes the output
---------------------------------------------------
Stability is per-METRIC, not per-row. Across those same two runs the brand *set* was
identical while first-mention flipped and citations shared nothing. So `brand_named` earns
more confidence than `cited`, and `first_mention` earns least. The summary reports each
separately rather than collapsing them into one number.

`sources: []` arrived on a run with `#error: False`. "The engine cited nobody" is a real
answer and a different finding from "the engine cited others but not you". Kept distinct.

Cost. Tier-dependent and the gap is enormous: chatgpt-result-scraped is $0.20 on FREE and
$0.005 on BRONZE, a 40x difference. Prices are read live from the actor. The preflight
refuses to start a run it cannot finish, because a run that dies at prompt 7 of 10 leaves
three prompts at one sample - the exact non-measurement this script exists to prevent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
for _p in ("web-scraper", "research"):
    sys.path.insert(0, str(REPO / ".claude" / "skills" / _p / "scripts"))

ACTOR = "apify/google-search-scraper"
MIN_RUNS = 3
CACHE_DIR = SKILL_DIR / ".cache" / "aivis"

# Engine -> how to switch it on, where its payload lands, what it charges.
# `result` keys verified live for chatgpt and aio; the rest are the actor's documented
# naming and are resolved defensively at read time (see _payload_of).
ENGINES: dict[str, dict] = {
    "aio":        dict(param="aiOverview",       payload={"scrapeFullAiOverview": True},
                       result="aiOverview",            event="ai-overview-scraped",          label="Google AI Overview"),
    "ai_mode":    dict(param="aiModeSearch",     payload={"enableAiMode": True},
                       result="aiModeSearchResult",    event="ai-mode-result-scraped",       label="Google AI Mode"),
    "chatgpt":    dict(param="chatGptSearch",    payload={"enableChatGpt": True},
                       result="chatGptSearchResult",   event="chatgpt-result-scraped",       label="ChatGPT"),
    "perplexity": dict(param="perplexitySearch", payload={"enablePerplexity": True},
                       result="perplexitySearchResult", event="perplexity-ai-result-scraped", label="Perplexity"),
    "gemini":     dict(param="geminiSearch",     payload={"enableGemini": True},
                       result="geminiSearchResult",    event="gemini-result-scraped",        label="Gemini"),
    "copilot":    dict(param="copilotSearch",    payload={"enableCopilot": True},
                       result="copilotSearchResult",   event="copilot-result-scraped",       label="Copilot"),
}

# Charged on every actor call regardless of engine. Measured 2026-08-08 on FREE.
BASE_EVENTS = ("actor-start", "search-page-scraped")

# Fallback only. Live prices are fetched in price_table(); these are the measured FREE-tier
# numbers so --estimate still works offline and never silently reports $0.
FALLBACK_PRICES = {
    "actor-start": 0.0, "search-page-scraped": 0.0045, "ai-overview-scraped": 0.003,
    "ai-mode-result-scraped": 0.20, "chatgpt-result-scraped": 0.20,
    "perplexity-ai-result-scraped": 0.20, "gemini-result-scraped": 0.20,
    "copilot-result-scraped": 0.20,
}

CREDITS_SPENT_USD = 0.0
CACHE_HITS = 0
LIVE_RUNS = 0


# --------------------------------------------------------------------------- helpers

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _apify_keys() -> list[str]:
    from _env import get_keys
    return get_keys("APIFY_API_KEY")


def _api_get(url: str, token: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def account_tier_and_headroom() -> tuple[str, float, list[dict]]:
    """Summed remaining monthly budget across every configured key. Free to call."""
    tier, total, per_key = "UNKNOWN", 0.0, []
    for i, tok in enumerate(_apify_keys(), 1):
        try:
            d = _api_get("https://api.apify.com/v2/users/me/limits", tok)["data"]
            used = float(d["current"]["monthlyUsageUsd"])
            cap = float(d["limits"]["maxMonthlyUsageUsd"])
            head = max(cap - used, 0.0)
            total += head
            per_key.append({"key": i, "used_usd": round(used, 4), "cap_usd": cap,
                            "headroom_usd": round(head, 2)})
            if tier == "UNKNOWN":
                try:
                    tier = _api_get("https://api.apify.com/v2/users/me", tok)["data"]["plan"]["id"]
                except Exception:
                    pass
        except Exception as e:  # noqa: BLE001
            per_key.append({"key": i, "error": f"{type(e).__name__}: {e}"})
    return tier, round(total, 2), per_key


def price_table() -> tuple[dict[str, float], str]:
    """Live per-event prices for this account's tier. Falls back to measured constants."""
    try:
        keys = _apify_keys()
        d = _api_get(f"https://api.apify.com/v2/acts/{ACTOR.replace('/', '~')}", keys[0])["data"]
        tier = _api_get("https://api.apify.com/v2/users/me", keys[0])["data"]["plan"]["id"]
        events = (d.get("pricingInfos") or [])[-1]["pricingPerEvent"]["actorChargeEvents"]
        out = {}
        for name, spec in events.items():
            tiered = (spec.get("eventTieredPricingUsd") or {}).get(tier, {})
            price = tiered.get("tieredEventPriceUsd", spec.get("eventPriceUsd"))
            if price is not None:
                out[name] = float(price)
        if out:
            return out, tier
    except Exception:
        pass
    return dict(FALLBACK_PRICES), "FREE(assumed)"


def estimate_cost(prompts: int, engines: list[str], runs: int,
                  prices: dict[str, float]) -> tuple[float, dict[str, int]]:
    """Cost of the whole protocol.

    One actor call per (prompt, run, engine) - which is what run() does - so the base
    events scale with engines too. Counting them per (prompt, run) undercounts, and an
    undercount in a preflight is the one direction of error that matters: it lets through
    a run that cannot finish.
    """
    per_engine_calls = prompts * runs
    total_calls = per_engine_calls * len(engines)
    events: dict[str, int] = {e: total_calls for e in BASE_EVENTS}
    for eng in engines:
        ev = ENGINES[eng]["event"]
        events[ev] = events.get(ev, 0) + per_engine_calls
    total = sum(prices.get(name, FALLBACK_PRICES.get(name, 0.0)) * n for name, n in events.items())
    return round(total, 4), events


# --------------------------------------------------------------------------- matching

def _word_re(term: str) -> re.Pattern:
    """Word-boundary match so `Acme` never matches inside `Acmecorp`."""
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])", re.I)


def _registrable(host: str) -> str:
    return re.sub(r"^www\.", "", (host or "").lower())


def _domain_of(url: str) -> str:
    try:
        return _registrable(url.split("//", 1)[1].split("/", 1)[0])
    except Exception:  # noqa: BLE001
        return ""


def _matches_competitor(domain: str, competitors: list[str]) -> bool:
    """A competitor list mixes bare names ("Pipedrive") and domains ("pipedrive.com").

    Treat an entry with a dot as a domain and match it exactly or as a parent; treat one
    without as a brand name and match it against the domain's first label. Comparing a
    bare name to a full host is the obvious way to get silent false negatives here.
    """
    for c in competitors:
        c = _registrable((c or "").strip())
        if not c:
            continue
        if "." in c:
            if domain == c or domain.endswith("." + c):
                return True
        elif domain.split(".", 1)[0] == c:
            return True
    return False


def _payload_of(item: dict, engine: str) -> tuple[dict | None, str | None]:
    """Locate an engine's payload. Returns (payload, key_used).

    Returns (None, None) when it genuinely cannot be found, so the caller records
    `unknown` instead of a fabricated "not cited". The spike hit exactly this: a
    lookup that missed `chatGptSearchResult` reported two empty extractions as
    "identical" and concluded the engines were deterministic. A silent empty read
    is the most dangerous failure this script has.
    """
    want = ENGINES[engine]["result"]
    if isinstance(item.get(want), dict):
        return item[want], want
    # defensive: actor renamed the field. Match on the engine token rather than guess.
    token = engine.replace("_", "")
    for k, v in item.items():
        if isinstance(v, dict) and token in k.lower().replace("_", ""):
            return v, k
    return None, None


def _text_and_sources(payload: dict) -> tuple[str, list[dict]]:
    text = ""
    for k in ("text", "content", "answer", "answerText", "markdown"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            text = v
            break
    srcs = []
    for k in ("sources", "citations", "references", "links"):
        v = payload.get(k)
        if isinstance(v, list):
            for s in v:
                if isinstance(s, dict) and (s.get("url") or s.get("link")):
                    srcs.append({"url": s.get("url") or s.get("link"), "title": s.get("title") or ""})
                elif isinstance(s, str) and s.startswith("http"):
                    srcs.append({"url": s, "title": ""})
            if srcs:
                break
    return text, srcs


def match_brand(text: str, sources: list[dict], *, brand: str, aliases: list[str],
                domain: str, competitors: list[str]) -> dict:
    """Three independent signals, deliberately never collapsed into one.

    course/38 treats being named without a link as real brand exposure feeding the
    course/34 mention effect, so folding it into `cited=false` discards a finding the
    corpus says is real.
    """
    terms = [brand] + [a for a in aliases if a]
    named = any(_word_re(t).search(text or "") for t in terms)
    first_named = None
    if text:
        hits = [(m.start(), t) for t in terms
                for m in [_word_re(t).search(text)] if m]
        if hits:
            first_named = min(hits)[1]

    dom = _registrable(domain)
    src_domains = [_domain_of(s["url"]) for s in sources]
    cited = bool(dom) and any(d == dom or d.endswith("." + dom) for d in src_domains if d)

    comp_named = sorted({c for c in competitors if c and _word_re(c).search(text or "")})
    comp_cited = sorted({d for d in src_domains if d and _matches_competitor(d, competitors)})

    return {
        "cited": cited,
        "brand_named": named,
        "first_named_brand": first_named,
        "engine_cited_nobody": len(sources) == 0,   # distinct from "cited others, not you"
        "cited_urls": [s["url"] for s in sources
                       if dom and (_domain_of(s["url"]) == dom
                                   or _domain_of(s["url"]).endswith("." + dom))],
        "source_count": len(sources),
        "competitors_named": comp_named,
        "competitors_cited": comp_cited,
    }


# --------------------------------------------------------------------------- stats

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval. Correct at n=3 where the normal approximation is not."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(max(p * (1 - p) / n + z * z / (4 * n * n), 0.0)) / d
    return (round(max(c - m, 0.0), 3), round(min(c + m, 1.0), 3))


def _stability(values: list) -> str:
    """Per-metric, because the spike showed they diverge sharply within one prompt."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return "insufficient"
    return "stable" if len(set(map(str, vals))) == 1 else "unstable"


def summarize(samples: list[dict], runs: int) -> list[dict]:
    by: dict[tuple, list[dict]] = {}
    for s in samples:
        by.setdefault((s["prompt"], s["engine"]), []).append(s)

    out = []
    for (prompt, engine), group in by.items():
        ok = [g for g in group if g.get("status") == "ok"]
        n = len(ok)
        cited_n = sum(1 for g in ok if g["cited"])
        named_n = sum(1 for g in ok if g["brand_named"])
        lo, hi = wilson(cited_n, n)
        comp = sorted({c for g in ok for c in g["competitors_cited"]})
        row = {
            "prompt": prompt, "engine": engine,
            "runs_requested": runs, "runs_ok": n,
            "runs_failed": len(group) - n,
            "cited_runs": cited_n, "named_runs": named_n,
            "citation_rate": round(cited_n / n, 3) if n else None,
            "mention_rate": round(named_n / n, 3) if n else None,
            "ci_low": lo, "ci_high": hi,
            # three stabilities, not one - the spike's core lesson
            "stability_cited": _stability([g["cited"] for g in ok]),
            "stability_named": _stability([g["brand_named"] for g in ok]),
            "stability_first": _stability([g["first_named_brand"] for g in ok]),
            "runs_where_engine_cited_nobody": sum(1 for g in ok if g["engine_cited_nobody"]),
            "competitors_cited": comp,
            "cited_urls": sorted({u for g in ok for u in g["cited_urls"]}),
        }
        if n < MIN_RUNS:
            row["citation_rate"] = None
            row["mention_rate"] = None
            row["note"] = (f"only {n} successful run(s); under {MIN_RUNS} no rate is reported. "
                           "A single sample measures the sampler, not the brand.")
        out.append(row)
    return sorted(out, key=lambda r: (r["engine"], r["prompt"]))


# --------------------------------------------------------------------------- sampling

def _cache_path(engine: str, prompt: str, gl: str, run_ix: int) -> Path:
    # run index is IN the key: three runs must be three entries, never one collapsed hit
    h = hashlib.sha1(f"{engine}|{prompt.strip().lower()}|{gl}|{run_ix}".encode()).hexdigest()
    return CACHE_DIR / f"{h}.json"


def sample_once(prompt: str, engine: str, run_ix: int, *, gl: str, hl: str,
                refresh: bool = False, cache: bool = True) -> dict:
    global CREDITS_SPENT_USD, CACHE_HITS, LIVE_RUNS
    cp = _cache_path(engine, prompt, gl, run_ix)
    if cache and not refresh and cp.exists():
        try:
            d = json.loads(cp.read_text(encoding="utf-8"))
            d["cached"] = True
            CACHE_HITS += 1
            return d
        except (json.JSONDecodeError, OSError):
            pass

    from engines.apify_engine import run_actor
    spec = ENGINES[engine]
    run_input = {"queries": prompt, "maxPagesPerQuery": 1, "countryCode": gl,
                 "languageCode": hl, spec["param"]: dict(spec["payload"])}

    rec: dict = {"prompt": prompt, "engine": engine, "run": run_ix, "gl": gl,
                 "fetched_at": _now(), "source": f"apify:{ACTOR}", "cached": False}
    try:
        items = run_actor(ACTOR, run_input, max_items=5, timeout_secs=420)
        LIVE_RUNS += 1
    except Exception as e:  # noqa: BLE001
        rec.update(status="error", error=f"{type(e).__name__}: {e}")
        return rec

    if not items:
        rec.update(status="error", error="actor returned no items")
        return rec

    payload, key_used = _payload_of(items[0], engine)
    if payload is None:
        rec.update(status="unknown", error=(
            f"no payload for engine {engine!r}; expected key {spec['result']!r}. "
            f"item keys: {sorted(items[0].keys())[:20]}. "
            "Treated as unknown, never as 'not cited'."))
        return rec

    text, sources = _text_and_sources(payload)
    rec.update(status="ok", payload_key=key_used, answer_chars=len(text),
               fan_out=len(payload.get("queryFanOut") or []),
               answer_text=text[:4000], sources=sources[:60])
    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return rec


def run(prompts: list[str], engines: list[str], runs: int, *, brand: str, aliases: list[str],
        domain: str, competitors: list[str], gl: str, hl: str, refresh: bool) -> dict:
    samples = []
    total = len(prompts) * len(engines) * runs
    i = 0
    for engine in engines:
        for prompt in prompts:
            for r in range(1, runs + 1):
                i += 1
                print(f"[aivis] {i}/{total}  {engine}  run {r}  {prompt[:52]!r}",
                      file=sys.stderr, flush=True)
                rec = sample_once(prompt, engine, r, gl=gl, hl=hl, refresh=refresh)
                if rec.get("status") == "ok":
                    rec.update(match_brand(rec.get("answer_text", ""), rec.get("sources", []),
                                           brand=brand, aliases=aliases, domain=domain,
                                           competitors=competitors))
                samples.append(rec)
    return {"brand": brand, "domain": domain, "engines": engines, "runs": runs,
            "prompts": len(prompts), "generated_at": _now(),
            "samples": samples, "summary": summarize(samples, runs)}


# --------------------------------------------------------------------------- selftest

def _selftest() -> None:
    import copy
    print("aivis selftest")

    # 1. under-3 runs is refused, and the refusal carries the evidence
    try:
        _guard_runs(2)
        raise AssertionError("runs=2 must be refused")
    except SystemExit as e:
        msg = str(e)
        assert "34.8" in msg and "1.5" in msg, f"refusal must cite the variance split: {msg}"
    print("  ok  --runs 2 refused, refusal cites 34.8% vs 1.5%")

    # 2. cost arithmetic on the measured FREE table
    usd, ev = estimate_cost(10, ["chatgpt", "perplexity"], 3, FALLBACK_PRICES)
    assert ev["chatgpt-result-scraped"] == 30 and ev["perplexity-ai-result-scraped"] == 30
    # base events bill per ACTOR CALL, and there is one per (prompt, run, engine).
    # Counting them per (prompt, run) undercounts by len(engines) - a preflight that
    # undercounts admits a run it cannot finish, which is the failure mode this guards.
    assert ev["search-page-scraped"] == 60, f"base events must scale with engines: {ev}"
    assert abs(usd - (60 * 0.20 + 60 * 0.0045)) < 1e-6, usd
    print(f"  ok  10 prompts x 3 runs x 2 engines on FREE = ${usd:.2f} (base events x{2})")
    one, _ = estimate_cost(10, ["chatgpt"], 3, FALLBACK_PRICES)
    two, _ = estimate_cost(10, ["chatgpt", "perplexity"], 3, FALLBACK_PRICES)
    assert abs(two - 2 * one) < 1e-6, "cost must be linear in engines, not sublinear"
    usd4, _ = estimate_cost(10, ["chatgpt", "perplexity", "gemini", "copilot"], 3, FALLBACK_PRICES)
    assert usd4 > 15.89, "the 4-engine protocol must exceed the measured headroom"
    print(f"  ok  4-engine protocol = ${usd4:.2f}, exceeds $15.89 headroom -> preflight refuses")

    # 3. matcher edge cases
    m = match_brand("Acmecorp is great", [], brand="Acme", aliases=[], domain="acme.com",
                    competitors=[])
    assert not m["brand_named"], "word boundary: Acme must not match inside Acmecorp"
    m = match_brand("We like Acme.", [{"url": "https://acme.com/x", "title": ""}],
                    brand="Acme", aliases=[], domain="acme.com", competitors=[])
    assert m["cited"] and m["brand_named"] and not m["engine_cited_nobody"]
    m = match_brand("Acme is fine.", [{"url": "https://other.com/a", "title": ""}],
                    brand="Acme", aliases=[], domain="acme.com", competitors=[])
    assert m["brand_named"] and not m["cited"] and not m["engine_cited_nobody"], \
        "named-without-link must survive as its own signal"
    m = match_brand("Nothing relevant.", [], brand="Acme", aliases=[], domain="acme.com",
                    competitors=[])
    assert m["engine_cited_nobody"] and not m["cited"], \
        "'engine cited nobody' is distinct from 'cited others, not you'"
    # competitor lists mix bare names and domains; both must resolve
    m = match_brand("Use Pipedrive.", [{"url": "https://www.pipedrive.com/", "title": ""}],
                    brand="Acme", aliases=[], domain="acme.com", competitors=["Pipedrive"])
    assert m["competitors_named"] == ["Pipedrive"], m["competitors_named"]
    assert m["competitors_cited"] == ["pipedrive.com"], m["competitors_cited"]
    m = match_brand("x", [{"url": "https://blog.hubspot.com/a", "title": ""}],
                    brand="Acme", aliases=[], domain="acme.com", competitors=["hubspot.com"])
    assert m["competitors_cited"] == ["blog.hubspot.com"], "subdomain of a competitor counts"
    m = match_brand("x", [{"url": "https://notpipedrive.com/a", "title": ""}],
                    brand="Acme", aliases=[], domain="acme.com", competitors=["Pipedrive"])
    assert m["competitors_cited"] == [], "a bare name must not match a lookalike host"
    print("  ok  matcher: boundaries, cited/named split, cited-nobody, competitors")

    # 4. payload locator never returns a silent empty  (the bug the live spike hit)
    item = {"chatGptSearchResult": {"text": "hi", "sources": []}}
    p, k = _payload_of(item, "chatgpt")
    assert p is not None and k == "chatGptSearchResult"
    p, k = _payload_of({"organicResults": []}, "chatgpt")
    assert p is None and k is None, "a miss must be None, not {}"
    p, k = _payload_of({"chatGPT_Search_Result": {"text": "x"}}, "chatgpt")
    assert p is not None, "renamed field must still resolve via the engine token"
    print("  ok  payload locator resolves, renames, and fails loudly")

    # 5. summary refuses a rate under MIN_RUNS and reports per-metric stability
    base = dict(prompt="p", engine="chatgpt", status="ok", cited=True, brand_named=True,
                first_named_brand="Acme", engine_cited_nobody=False, cited_urls=[],
                competitors_cited=[], source_count=1)
    two = [copy.deepcopy(base), copy.deepcopy(base)]
    assert summarize(two, 3)[0]["citation_rate"] is None, "under 3 ok runs -> no rate"
    assert "measures the sampler" in summarize(two, 3)[0]["note"]
    three = [copy.deepcopy(base) for _ in range(3)]
    three[1]["cited"] = False
    three[1]["first_named_brand"] = "Rival"
    s = summarize(three, 3)[0]
    assert s["runs_ok"] == 3 and s["cited_runs"] == 2 and s["citation_rate"] == 0.667
    assert s["stability_cited"] == "unstable" and s["stability_named"] == "stable" \
        and s["stability_first"] == "unstable", s
    assert s["ci_low"] < 0.3 and s["ci_high"] > 0.9, f"n=3 interval must be wide: {s}"
    print(f"  ok  n=3, 2 cited -> rate {s['citation_rate']}, 95% CI "
          f"[{s['ci_low']}, {s['ci_high']}], stability split per metric")

    # 6. cache key includes the run index
    a = _cache_path("chatgpt", "q", "us", 1)
    b = _cache_path("chatgpt", "q", "us", 2)
    assert a != b, "run index must be part of the cache key"
    assert _cache_path("chatgpt", " Q ", "us", 1) == a, "key normalises case and space"
    print("  ok  cache: run index in key, query normalised")

    print("ALL PASS")


def _guard_runs(runs: int) -> None:
    if runs < MIN_RUNS:
        raise SystemExit(
            f"refusing --runs {runs}: minimum is {MIN_RUNS}.\n"
            "arXiv 2604.07585 decomposed 12,933 LLM brand answers: within-prompt resampling\n"
            "accounts for 34.8% of total variance, while brand identity - the thing you are\n"
            "trying to measure - is 1.5%. Measured here 2026-08-08, two ChatGPT runs of one\n"
            "prompt seconds apart returned different winners (HubSpot vs Pipedrive) and\n"
            "0.00 Jaccard overlap on cited domains.\n"
            "Under 3 runs you are measuring the sampler. Use --runs 3 or more.")


# --------------------------------------------------------------------------- cli

def main() -> None:
    ap = argparse.ArgumentParser(description="Sample answer engines for brand citation and mention.")
    ap.add_argument("--prompts", help="file with one prompt per line")
    ap.add_argument("--prompt", action="append", default=[], help="a single prompt (repeatable)")
    ap.add_argument("--brand", help="brand name as it would be written in prose")
    ap.add_argument("--brand-aliases", default="", help="comma separated")
    ap.add_argument("--domain", default="", help="client domain, for the citation test")
    ap.add_argument("--competitors", default="", help="comma separated names or domains")
    ap.add_argument("--engines", default="aio",
                    help=f"comma separated from {','.join(ENGINES)} (default: aio, the cheap tier)")
    ap.add_argument("--runs", type=int, default=MIN_RUNS)
    ap.add_argument("--gl", default="us")
    ap.add_argument("--hl", default="en")
    ap.add_argument("--estimate", action="store_true", help="print cost and headroom, spend nothing")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--yes", action="store_true", help="skip the spend confirmation")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return

    engines = [e.strip() for e in a.engines.split(",") if e.strip()]
    bad = [e for e in engines if e not in ENGINES]
    if bad:
        raise SystemExit(f"unknown engine(s): {bad}. choose from {sorted(ENGINES)}")

    prompts = list(a.prompt)
    if a.prompts:
        prompts += [ln.strip() for ln in Path(a.prompts).read_text(encoding="utf-8").splitlines()
                    if ln.strip() and not ln.startswith("#")]
    if not prompts:
        raise SystemExit("no prompts. use --prompts FILE or --prompt TEXT")

    _guard_runs(a.runs)

    prices, tier = price_table()
    usd, events = estimate_cost(len(prompts), engines, a.runs, prices)
    _, headroom, per_key = account_tier_and_headroom()

    print(f"account tier   : {tier}")
    print(f"prompts x runs x engines : {len(prompts)} x {a.runs} x {len(engines)} "
          f"= {len(prompts) * a.runs * len(engines)} calls")
    for name, n in sorted(events.items()):
        print(f"  {name:32s} {n:5d} x ${prices.get(name, 0):.4f} = ${n * prices.get(name, 0):.2f}")
    print(f"ESTIMATED COST : ${usd:.2f}")
    print(f"HEADROOM       : ${headroom:.2f} across {len(per_key)} key(s)")

    if usd > headroom:
        msg = (f"\nREFUSING TO START: ${usd:.2f} needed, ${headroom:.2f} available.\n"
               "A run that dies part way leaves some prompts at one sample, which is not a\n"
               "measurement and is worse than not running.\n"
               "Options: fewer prompts or engines, --engines aio (the $0.003 tier), or\n"
               "upgrade one key to BRONZE where these events cost $0.005 instead of $0.20 - "
               "a 40x reduction.")
        if a.estimate:
            print(msg)
            return
        raise SystemExit(msg)

    if a.estimate:
        print("\n--estimate: nothing spent.")
        return

    if usd > 0.50 and not a.yes:
        resp = input(f"\nSpend ${usd:.2f}? [y/N] ").strip().lower()
        if resp != "y":
            raise SystemExit("aborted, nothing spent.")

    res = run(prompts, engines, a.runs,
              brand=a.brand or "", aliases=[s.strip() for s in a.brand_aliases.split(",") if s.strip()],
              domain=a.domain, competitors=[s.strip() for s in a.competitors.split(",") if s.strip()],
              gl=a.gl, hl=a.hl, refresh=a.refresh)
    res["cost"] = {"estimated_usd": usd, "tier": tier, "events": events,
                   "live_runs": LIVE_RUNS, "cache_hits": CACHE_HITS,
                   "headroom_before_usd": headroom}

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {a.out}", file=sys.stderr)
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False))

    print(f"\n[aivis] live={LIVE_RUNS} cached={CACHE_HITS}", file=sys.stderr)
    for r in res["summary"]:
        rate = "n/a" if r["citation_rate"] is None else f"{r['cited_runs']}/{r['runs_ok']} runs"
        print(f"  {r['engine']:11s} cited {rate:12s} named {r['named_runs']}/{r['runs_ok']}  "
              f"[{r['stability_cited']}]  {r['prompt'][:44]!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
