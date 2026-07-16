"""Phase 2/3: resolve ONE business's website + company socials + founder + founder socials.

v3 (website-first): the company's own site is now the PRIMARY source of truth -- footer/header for
company socials, About/Team/Contact for the founder's name + personal socials. The `research` skill
(search) is a FALLBACK, used only when the website doesn't have what's needed. This inverts v2's order
after a live-verified batch showed search-first founder resolution kept attaching the wrong person: a
same-named stranger (an unrelated notary/business owner), someone in an unrelated past or
current role (a Chief Business Officer at a target company who founded a different, earlier company,
not this one), or a name that merely shares a token with a company whose own
brand name IS a common word (an agency named after a common word matched to an unrelated person of the
same name; another matched to an unrelated person instead of its real co-founder). See
references/how-it-works.md for the full writeup (names genericized there to keep real third parties out
of this public repo).

No confidence gate on a search result is bulletproof against those failure modes -- that's exactly why
website-sourced fields are trusted (they're the company's own published claim) while anything sourced
from search is always tagged for review rather than auto-written, even when it passes verification.

Usage:
  python resolve.py --business '<json from read_batch_main.py>'
  python resolve.py --selftest
Runs UNSANDBOXED (research + clutch + web-scraper need network/DNS). Website/Clutch/crawl4ai passes are
free-tier; only the search-based gap-fill and founder fallback spend research-skill API calls.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clutch_resolve  # noqa: E402
import scrape_socials  # noqa: E402  free http footer/contact/team pass
import url_filters  # noqa: E402

SKILLS = Path(__file__).resolve().parents[2]           # .claude/skills
RESEARCH_DIR = SKILLS / "research" / "scripts"
WEBSCRAPER = SKILLS / "web-scraper" / "scripts" / "scrape.py"
FOUNDER_SCHEMA = Path(__file__).resolve().parents[1] / "templates" / "founder_socials_schema.json"
PLATFORMS = ("instagram", "linkedin", "facebook")

# Generic agency-branding words stripped before checking whether a search candidate's context actually
# ties to THIS company. Several of these (top/best/leading/performance/pro) are ported directly from
# names that produced false-positive founder matches in the live run (e.g. "Top New York SEO", "9AM
# Performance Marketing Agency") -- when a company's name reduces to nothing but these, _company_core
# returns "" and the confidence gate below refuses to verify anything, which is the correct call: there's
# no way to distinguish "the founder of Top New York SEO" from any unrelated person mentioned nearby.
_STOPWORDS = {"agency", "marketing", "digital", "media", "group", "company", "the", "new", "york",
              "nyc", "seo", "llc", "inc", "co", "studio", "creative", "solutions", "consulting",
              "top", "best", "leading", "premier", "design", "branding", "concepts", "performance",
              "pro", "communications"}

_FOUNDER_WORDS = r"(?:founder|co-founder|owner|ceo|president|principal)"                       # use with re.I
_FOUNDER_WORDS_CASED = r"(?:[Ff]ounder|[Cc]o-[Ff]ounder|[Oo]wner|CEO|ceo|[Pp]resident|[Pp]rincipal)"  # name-capture context, no re.I


# --------------------------------------------------------------------------- research
def research(query: str, *, mode: str = "general", depth: str = "light",
             services: str = "serper,tavily,exa", num: int = 10, timeout: int = 120) -> dict:
    """Call the research skill's CLI (--json) from its own dir. Returns {} on failure (never raises).
    `answer` (Tavily's own synthesized answer, when tavily is in `services`) rides along even at light
    depth + --no-synth -- that flag only gates the separate multi-source LLM `report` used at medium/deep."""
    cmd = [sys.executable, "research.py", "--query", query, "--mode", mode, "--depth", depth,
           "--services", services, "--num", str(num), "--no-synth", "--json"]
    try:
        p = subprocess.run(cmd, cwd=str(RESEARCH_DIR), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"results": [], "_error": f"research timeout on: {query}"}
    if p.returncode != 0:
        return {"results": [], "_error": (p.stderr or "research failed")[:300]}
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"results": [], "_error": "research emitted non-JSON"}


def pick_socials(results: list[dict], *, allow_company: bool = False, verify_context: str = "") -> dict:
    """First valid profile per platform from research results (skips directory/review sites).
    `verify_context`, when given, requires the result's OWN title+snippet to mention that token too --
    a loose identity check used for founder-social lookups, where a same-named stranger (the Jamie Rourke
    failure mode: an unrelated notary/business owner) is the main risk."""
    out: dict[str, str] = {}
    vctx = verify_context.lower()
    for r in results:
        url = r.get("url", "")
        if url_filters.is_directory(url):
            continue
        if vctx and vctx not in f"{r.get('title','')} {r.get('snippet','')}".lower():
            continue
        hit = url_filters.social_profile(url, allow_company=allow_company)
        if hit:
            platform, cu = hit
            out.setdefault(platform, cu)
    return out


def _name_from_title(title: str) -> str:
    """LinkedIn result titles read 'Jane Doe - Founder at Acme | LinkedIn' -> 'Jane Doe'."""
    head = (title or "").split(" - ")[0].split(" | ")[0].split(" – ")[0].strip()
    return head if 2 <= len(head.split()) <= 4 else ""  # a plausible person name, not a company


def founder_candidates(results: list[dict]) -> list[dict]:
    """Person LinkedIn (/in/) hits with the name/title text, ranked by search order (not a verdict)."""
    cands, seen = [], set()
    for r in results:
        url = url_filters.clean(r.get("url", ""))
        if not url_filters.is_person_linkedin(url) or url in seen:
            continue
        seen.add(url)
        cands.append({"name": _name_from_title(r.get("title", "")),
                      "linkedin": url, "snippet": (r.get("snippet") or "")[:200],
                      "title_text": r.get("title", "")})
    return cands


def _company_core(company: str) -> str:
    """The company's most distinctive token: the FIRST non-generic word, since agency names are
    overwhelmingly '{Brand} {Category}' (e.g. "Meridian Rank", "Lark Studio") -- picking the longest
    token instead would favor a generic category word like "studio" over the actual brand "lark". Returns
    "" when the name is entirely generic (see _STOPWORDS docstring) -- callers must treat that as
    "cannot verify," not as a green light."""
    tokens = [w for w in re.split(r"\W+", (company or "").lower()) if len(w) > 2 and w not in _STOPWORDS]
    return tokens[0] if tokens else ""


def _verify_founder_context(company: str, ctx: str) -> bool:
    """Does ctx show a founder-type word within ~40 chars of the company's distinctive token, either
    order? Requires BOTH signals together -- a bare token-overlap check alone is exactly what let
    "Halstead Cole" (a person whose own name happens to contain the company's name, "Halstead") get
    accepted as its founder with no other evidence. Still not bulletproof (a coincidental nearby mention
    can pass) -- which is why anything through this path is tagged for review, never auto-written."""
    core = _company_core(company)
    if not core or not ctx:
        return False
    pat = re.compile(rf"{_FOUNDER_WORDS}.{{0,40}}{re.escape(core)}|{re.escape(core)}.{{0,40}}{_FOUNDER_WORDS}",
                     re.I)
    return bool(pat.search(ctx))


def _founder_from_answer(answer: str, company: str) -> dict:
    """Parse a research 'answer' string (Tavily's own synthesized answer) for an explicit
    'Name is/was the founder/CEO/... of ...' statement, then require the company's distinctive token to
    show up shortly after -- a name pattern alone proves nothing about WHICH company. Returns {} if
    nothing qualifies."""
    if not answer:
        return {}
    core = _company_core(company)
    if not core:
        return {}
    name_pat = re.compile(r"([A-Z][\w.'-]+(?:\s[A-Z][\w.'-]+){0,3})\s*(?:is|was|,)?\s*(?:the\s+)?"
                          + _FOUNDER_WORDS_CASED)
    for m in name_pat.finditer(answer):
        tail = answer[m.end(): m.end() + 60].lower()
        if core in tail:
            return {"name": m.group(1).strip(), "source_text": answer[:300]}
    return {}


# --------------------------------------------------------------------------- website resolution
def _is_clutch(url: str) -> bool:
    try:
        return "clutch.co" in urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    except ValueError:
        return False


def ensure_website(biz: dict, notes: list[str]) -> tuple[str, bool]:
    """Resolve a website for this business if one isn't already known. Returns (website, freshly_found).
    Priority: existing field -> Clutch redirect-extraction (if the directory link is a Clutch profile) ->
    one light research reverse-lookup as a last resort."""
    website = biz.get("website", "")
    if website:
        return website, False

    directory_link = biz.get("directory_link", "")
    if directory_link and _is_clutch(directory_link):
        result = clutch_resolve.resolve_website(directory_link)
        if result.get("website"):
            notes.append(f"website resolved via Clutch redirect: {result['website']}")
            return result["website"], True
        if result.get("error"):
            notes.append(f"Clutch website lookup failed: {result['error']}")

    loc = biz.get("location") or biz.get("experience") or ""
    r = research(f'{biz["company"]} {loc} official website', mode="general", depth="light",
                 services="serper,tavily", num=5)
    for res in r.get("results", []):
        url = res.get("url", "")
        if url and not url_filters.is_directory(url) and not url_filters.SOCIAL_RE.match(url):
            notes.append(f"website reverse-looked-up via search: {url}")
            return url, True
    return "", False


def webscrape_page(url: str, timeout: int = 60) -> dict:
    """One free-tier (crawl4ai) llm extraction of founder + socials from a page. {} on failure. 60s cap:
    crawl4ai renders most pages in 15-40s; a page that needs longer is a heavy/slow site better flagged
    for manual review than left to stall a 150+ row batch (the old 150s x 6-page budget was ~15 min/row
    worst case, which made a full reprocess intractable)."""
    cmd = [sys.executable, str(WEBSCRAPER), "--url", url, "--engine", "crawl4ai",
           "--extract", "llm", "--schema", str(FOUNDER_SCHEMA), "--out", "json"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        data = json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else []
        return data[0] if isinstance(data, list) and data else (data if isinstance(data, dict) else {})
    except Exception:  # noqa: BLE001 - fallback must never crash the resolve
        return {}


def website_fallback(website: str, gaps: list[str], want_founder: bool) -> dict:
    """Smart, free-tier-only website scrape: fast http (footer/contact/team) first, then crawl4ai llm on
    About/Team for the founder name + any still-missing socials. Never a full crawl. Reports a too-big
    site instead of crawling it. This is now called FIRST in resolve() for every business with a
    resolvable website, not as a last resort."""
    out: dict = {"company": {}, "founder": {}, "notes": []}
    if not website:
        out["notes"].append("no website to scrape")
        return out

    hit = scrape_socials.resolve_one(website)
    for p in PLATFORMS:
        if hit.get(p):
            out["company"][p] = hit[p]
    if hit.get("linkedin_candidates"):
        out["linkedin_candidates"] = hit["linkedin_candidates"]

    still_gap = [p for p in gaps if not out["company"].get(p)]
    if want_founder or still_gap:
        base = website if "://" in website else f"https://{website}"
        base = base.rstrip("/")
        # crawl4ai launches a fresh headless browser PER page, so each call is expensive (~15-40s, and a
        # heavy JS site like moburst.com can burn the full per-page timeout). Cap the page set to the few
        # highest-value ones: About/Team carry the founder bio. Add the home page only when the fast http
        # pass got NO socials at all (site likely Cloudflare-blocked http) -- crawl4ai gets past that. The
        # early-exit below stops as soon as the founder + all socials are in hand, so a founder on /about/
        # costs a single browser launch. This bounds a row to <=3 crawl4ai calls (see webscrape_page's
        # 60s cap) instead of the old 6, which is what made a full reprocess intractable.
        paths = ["", "/about/", "/team/"] if not out["company"] else ["/about/", "/team/", "/about-us/"]
        for path in paths:
            page = webscrape_page(base + path)
            if not page:
                continue
            if page.get("founder_name") and not out["founder"].get("name"):
                out["founder"]["name"] = page["founder_name"]
                out["founder"]["title"] = page.get("founder_title", "")
            for src, dst in (("company_instagram", "instagram"), ("company_linkedin", "linkedin"),
                             ("company_facebook", "facebook")):
                if page.get(src) and not out["company"].get(dst):
                    hit2 = url_filters.social_profile(page[src], allow_company=(dst == "linkedin"))
                    if hit2:
                        out["company"][dst] = hit2[1]
            for src, dst in (("founder_instagram", "instagram"), ("founder_linkedin", "linkedin"),
                             ("founder_facebook", "facebook")):
                if page.get(src) and not out["founder"].get(dst):
                    out["founder"][dst] = url_filters.clean(page[src])
            if out["founder"].get("name") and not [p for p in gaps if not out["company"].get(p)]:
                break
        else:
            if not out["founder"].get("name") and still_gap:
                out["notes"].append("standard About/Team/Contact pages did not resolve it -- "
                                    "if this is a large/custom site, flag it for a manual look "
                                    "rather than crawling the whole thing")
    return out


def founder_search_fallback(company: str, category: str, location: str) -> dict:
    """Search-based founder fallback -- ONLY reached when the company's own website didn't name a
    founder. Uses the natural-language query Aleem's own manual testing validated ('founder of X,
    category, location'), not the old boolean-OR shape, which matched anyone loosely associated with
    those role words at the company regardless of whether it was the actual founder of THIS business."""
    q = f"founder of {company} {category} {location}".strip()
    r = research(q, mode="entity", depth="light")
    candidates = founder_candidates(r.get("results", []))
    verified = [c for c in candidates
               if _verify_founder_context(company, f"{c.get('title_text','')} {c.get('snippet','')}")]
    answer_hit = _founder_from_answer(r.get("answer", "") or "", company)

    names = {c["name"] for c in verified if c.get("name")}
    if answer_hit.get("name"):
        names.add(answer_hit["name"])
    confidence = "ambiguous" if len(names) > 1 else ("low" if names else "none")

    return {"query": q, "error": r.get("_error", ""), "all_candidates": candidates,
            "verified_candidates": verified, "answer_hit": answer_hit, "confidence": confidence}


# --------------------------------------------------------------------------- orchestration
def resolve(biz: dict, *, do_founder: bool = True) -> dict:
    company = {p: biz.get(p, "") for p in PLATFORMS}
    founder = {"name": biz.get("founder", ""), "instagram": biz.get("founder_instagram", ""),
               "linkedin": biz.get("founder_linkedin", ""), "facebook": biz.get("founder_facebook", "")}
    loc = biz.get("location") or biz.get("experience") or ""
    category = biz.get("category", "")
    notes: list[str] = []
    provenance: dict[str, str] = {}
    founder_search: dict = {}

    # Step 1 -- ensure a website (existing field -> Clutch redirect -> reverse-lookup search).
    website, website_fresh = ensure_website(biz, notes)

    # Step 2 -- website extraction FIRST, unconditionally, whenever a website is known. This is now the
    # primary source for both company socials and the founder's name (see module docstring for why).
    if website:
        wf = website_fallback(website, [p for p in PLATFORMS if not company[p]],
                              do_founder and not founder["name"])
        for p in PLATFORMS:
            if wf["company"].get(p) and not company[p]:
                company[p] = wf["company"][p]
                provenance[p] = "website"
        if wf["founder"].get("name") and not founder["name"]:
            founder["name"] = wf["founder"]["name"]
            provenance["founder"] = "website"
            for p in PLATFORMS:
                if wf["founder"].get(p):
                    founder[p] = wf["founder"][p]
                    provenance[f"founder_{p}"] = "website"
        if wf.get("linkedin_candidates"):
            notes.append(f"team-page LinkedIn candidates (unconfirmed): {wf['linkedin_candidates']}")
        notes += wf.get("notes", [])

    # Step 3 -- search gap-fill for whatever company socials the website pass didn't have. Each result
    # is verified against the company's distinctive token (title/snippet must mention it) -- without this
    # a business whose own site links no Instagram gets whatever the top instagram.com search hit is,
    # which live-caught an unrelated handle landing on a target company. A missing social (falls
    # to review / stays blank) is safer than a wrong one that would get a stranger messaged. When the
    # name is fully generic (_company_core == "") there's no token to verify against, so this degrades to
    # the old unverified behavior for those rows only.
    core = _company_core(biz["company"])
    missing = [p for p in PLATFORMS if not company[p]]
    if missing:
        r = research(f'{biz["company"]} {loc} instagram OR linkedin OR facebook', mode="general", depth="light")
        if r.get("_error"):
            notes.append(r["_error"])
        found = pick_socials(r.get("results", []), allow_company=True, verify_context=core)
        for p in missing:
            if found.get(p):
                company[p] = found[p]
                provenance[p] = "search"
        for p in [q for q in missing if not company[q]]:
            r2 = research(f'{biz["company"]} {loc} site:{p}.com', mode="general", depth="light",
                          services="serper,tavily", num=8)
            f2 = pick_socials(r2.get("results", []), allow_company=(p == "linkedin"), verify_context=core)
            if f2.get(p):
                company[p] = f2[p]
                provenance[p] = "search"

    # Step 4 -- founder search fallback, only if the website didn't name one.
    if do_founder and not founder["name"]:
        founder_search = founder_search_fallback(biz["company"], category, loc)
        best_name = ""
        if founder_search["verified_candidates"]:
            best = founder_search["verified_candidates"][0]
            best_name, best_li = best["name"], best["linkedin"]
        elif founder_search["answer_hit"].get("name"):
            best_name, best_li = founder_search["answer_hit"]["name"], ""
        else:
            best_li = ""
        if best_name:
            founder["name"] = best_name
            founder["linkedin"] = founder["linkedin"] or best_li
            provenance["founder"] = "search_fallback"
            if best_li:
                provenance["founder_linkedin"] = "search_fallback"
        else:
            notes.append("no confident founder candidate on website or search -- needs manual lookup")

    # Step 6 -- founder's own socials, verified against the company's own distinctive token so a
    # same-named stranger's profile (the Jamie Rourke failure mode) doesn't get attached.
    if do_founder and founder["name"] and not (founder["instagram"] and founder["facebook"]):
        core = _company_core(biz["company"])
        r = research(f'{founder["name"]} {biz["company"]} instagram OR facebook',
                     mode="general", depth="light", services="serper,tavily", num=8)
        fs = pick_socials(r.get("results", []), verify_context=core)
        for p in ("instagram", "facebook"):
            if fs.get(p) and not founder[p]:
                founder[p] = fs[p]
                provenance.setdefault(f"founder_{p}", "search")

    needs_review = sorted({k for k, v in provenance.items()
                           if v == "search_fallback" or (k.startswith("founder_") and v == "search")})

    return {
        "row": biz.get("row"), "company_name": biz.get("company"), "location": loc,
        "website": website, "website_freshly_found": website_fresh,
        "company_socials": company, "founder": founder,
        "provenance": provenance, "needs_review": needs_review,
        "founder_search": founder_search,
        "unresolved": [p for p in PLATFORMS if not company[p]],
        "notes": notes,
    }


def demo():
    """Self-check: candidate filtering + the confidence-gate helpers (no network)."""
    results = [
        {"url": "https://www.clutch.co/profile/acme", "title": "Acme on Clutch"},          # directory: skip
        {"url": "https://instagram.com/acme.co", "title": "Acme"},                          # ig profile
        {"url": "https://instagram.com/p/xyz/", "title": "a post"},                         # junk
        {"url": "https://www.linkedin.com/company/acme", "title": "Acme | LinkedIn"},        # company page
        {"url": "https://www.linkedin.com/in/jane-doe", "title": "Jane Doe - Founder at Acme | LinkedIn"},
    ]
    socials = pick_socials(results, allow_company=True)
    assert socials.get("instagram") == "https://instagram.com/acme.co", socials
    assert socials.get("linkedin") == "https://www.linkedin.com/company/acme", socials  # company kept
    cands = founder_candidates(results)
    assert len(cands) == 1 and cands[0]["name"] == "Jane Doe", cands
    assert cands[0]["linkedin"] == "https://www.linkedin.com/in/jane-doe", cands

    # verify_context: same-named-stranger rejection (the Jamie Rourke failure mode).
    assert pick_socials(results, verify_context="acme").get("instagram") == "https://instagram.com/acme.co"
    assert not pick_socials(results, verify_context="wisecorp").get("instagram")

    # _company_core: brand-first, not longest-token; fully-generic names yield "" (refuse to guess).
    assert _company_core("Meridian Rank") == "meridian", _company_core("Meridian Rank")
    assert _company_core("Lark Studio") == "lark", _company_core("Lark Studio")
    assert _company_core("Top New York SEO Agency LLC") == "", _company_core("Top New York SEO Agency LLC")

    # _verify_founder_context: real co-occurrence passes; a coincidental name/company overlap with no
    # founder-word nearby does NOT (this is the exact "Halstead Cole" false positive being fixed).
    assert _verify_founder_context("Acme", "Jane Doe - Founder at Acme | LinkedIn")
    assert _verify_founder_context("Lark Studio", "Sofia Marek, Creative Principal and Co-Founder, Lark Studio")
    assert not _verify_founder_context("Halstead", "Halstead Cole - Social Media Strategist at Overlook")

    # _founder_from_answer: explicit statement + company co-occurrence required together.
    hit = _founder_from_answer("Hal Sanders is the founder of Halstead Communications, a PR agency.", "Halstead")
    assert hit.get("name") == "Hal Sanders", hit
    assert not _founder_from_answer("Halstead Cole works in social media.", "Halstead")

    print("resolve self-check OK")


def main():
    p = argparse.ArgumentParser(
        description="Resolve one business's website + socials + founder (website-first, search-fallback).")
    p.add_argument("--business", help="JSON dict from read_batch_main.py")
    p.add_argument("--no-founder", action="store_true", help="skip founder resolution")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        demo()
        return
    if not args.business:
        raise SystemExit("--business is required (or pass --selftest)")

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    biz = json.loads(args.business)
    report = resolve(biz, do_founder=not args.no_founder)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
