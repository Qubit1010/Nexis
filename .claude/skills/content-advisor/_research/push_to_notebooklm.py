#!/usr/bin/env python3
"""Mirror the content-marketing corpus into NotebookLM, so the live-query tier can ask the
gathered evidence instead of re-searching the web.

    python push_to_notebooklm.py --plan     # show the split, create nothing
    python push_to_notebooklm.py            # create notebooks + import, resume-safe
    python push_to_notebooklm.py --status   # counts per notebook

Cloned from copywriting-advisor's. Five buckets rather than its three, because this corpus
is 560 sources and the observed per-notebook cap on this account is ~136 rather than the
300 the tier implies. Splitting topically also answers better: a notebook that only knows
about formats does not have to reason past the diffusion literature to answer a format
question. Same precedent as the SEO corpus, which lives in five scoped notebooks here.

THE CRAFT BUCKET IS A PHYSICAL QUARANTINE. Routing is by TIER first, then by pass, so a
craft teardown can never be returned as evidence by a notebook that only holds evidence.
That matters more here than it did for copywriting: this corpus has 140 craft sources
against its 75, because the craft register actually ran in practical mode this time.

FIRST-PARTY PLATFORM DOCS GET THEIR OWN BUCKET. They are practitioner-tier but they answer
a completely different question - what a platform requires or defines - and mixing them
into an evidence notebook invites exactly the [P*] misuse the tier exists to prevent.

Resume-safe: reads back what is already in each notebook and skips it, so a rerun after a
timeout or a rate-limit costs nothing. NEVER calls `source clean` or `source delete`;
per .claude/rules/research-backed-skills.md those need Aleem's explicit approval because
they can silently drop UUIDs that existing [sN] citations depend on.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parent
SOURCES = RESEARCH_DIR / "sources.json"
STATE = RESEARCH_DIR / "notebooklm-state.json"
LOG = RESEARCH_DIR / "notebooklm-push.log"

EXE = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "Scripts" / "notebooklm.exe"

# Which pass a source has to appear in to land in each notebook. A source carries several
# topics, so first match wins and the buckets stay disjoint.
BUCKETS = [
    (
        # How content is consumed and remembered: the multimedia-learning, attention and
        # visual-perception literature. This is the notebook that answers "how long", "what
        # structure", "does showing a face help".
        "Content 2026 - Format & Attention Evidence (NexusPoint)",
        "format_attention",
        ("q2_video_engagement_retention", "q3_short_form_video_feeds",
         "q4_podcast_audio_consumption", "q5_live_streaming_synchronous",
         "q6_visual_information_design", "q8_newsletter_owned_channel"),
    ),
    (
        # Why content spreads, who shares it, and what makes an audience trust the source.
        "Content 2026 - Diffusion & Audience Evidence (NexusPoint)",
        "diffusion_audience",
        ("q7_social_post_engagement", "q9_diffusion_cascades_virality",
         "q10_ugc_creative_asset", "q11_source_credibility_expertise",
         "q13_seeding_amplification_distribution", "q14_attention_decay_refresh"),
    ),
    (
        # The commercial and measurement half, plus AI-generated content. Kept together
        # because every question here is ultimately "can we prove it".
        "Content 2026 - Strategy, Measurement & AI (NexusPoint)",
        "strategy_measurement",
        ("q1_firm_generated_content_effects", "q12_message_frequency_scheduling",
         "q15_content_incrementality_attribution", "q16_ai_generated_content",
         "q17_folklore_provenance", "q18_metric_definitions"),
    ),
]

# The craft tier gets its OWN notebook, routed by TIER rather than by pass. Keeping it
# physically separate IS the quarantine: someone querying the craft notebook is asking
# "how do I make this", and cannot accidentally receive a teardown as though it were
# evidence. 140 sources here against copywriting's 75, because the craft register
# actually ran in practical mode this time.
CRAFT_BUCKET = ("Content 2026 - Craft & Examples (NexusPoint)", "craft")

# First-party platform documentation, also routed by a flag rather than by pass. Small
# (9 sources) but it answers a categorically different question - what a platform
# REQUIRES or DEFINES - and mixing it into an evidence notebook is how a spec gets
# returned as proof that something works.
PLATFORM_BUCKET = ("Content 2026 - Platform Specs (NexusPoint)", "platform_docs")


# How many consecutive add failures mean "this notebook is full" rather than "these
# particular URLs are unfetchable". 6 is comfortably past the longest run of genuinely
# bad URLs seen in the first import.
FULL_STREAK = 6


def _roman(n):
    return {2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}.get(n, str(n))


def log(msg):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def nb(*args, timeout=180):
    """Run the CLI and return (ok, parsed_or_text)."""
    if not EXE.exists():
        raise SystemExit(f"notebooklm CLI not found at {EXE}")
    r = subprocess.run([str(EXE), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    out = (r.stdout or "").strip()
    try:
        return r.returncode == 0, json.loads(out)
    except Exception:  # noqa: BLE001
        return r.returncode == 0, out or (r.stderr or "").strip()


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save_state(s):
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def plan():
    """Route by TIER first, then by pass.

    Craft is routed on tier so the quarantine is physical as well as logical. Sources
    already known to be unfetchable are dropped here rather than retried: they were
    added once, errored, and were cleaned out - re-adding them just recreates the
    corpses that filled 39 of the persuasion notebook's 136 slots.
    """
    data = json.loads(SOURCES.read_text(encoding="utf-8"))
    dead = set(load_state().get("known_unfetchable", []))

    buckets = {k: [] for _, k, _ in BUCKETS}
    buckets[CRAFT_BUCKET[1]] = []
    buckets[PLATFORM_BUCKET[1]] = []
    seen, skipped_dead = set(), 0

    for s in data["sources"]:
        if s["url"].strip().rstrip("/") in dead:
            skipped_dead += 1
            seen.add(s["index"])
            continue
        # Platform docs are checked BEFORE craft and before the pass buckets. They are
        # practitioner-tier, so without this they would scatter across the evidence
        # notebooks by whichever pass found them - which is precisely the [P*] misuse
        # the separate tier exists to prevent.
        if s.get("first_party"):
            buckets[PLATFORM_BUCKET[1]].append(s)
            seen.add(s["index"])
            continue
        if s["tier"] == "craft":
            buckets[CRAFT_BUCKET[1]].append(s)
            seen.add(s["index"])
            continue
        for _, key, topics in BUCKETS:
            if any(t in topics for t in s["topics"]) and s["index"] not in seen:
                buckets[key].append(s)
                seen.add(s["index"])
                break

    if skipped_dead:
        log(f"skipping {skipped_dead} source(s) known to be unfetchable by NotebookLM")
    orphans = [s for s in data["sources"] if s["index"] not in seen]
    return buckets, orphans


def all_buckets():
    """Push order: SMALLEST COMPLETE BUCKETS FIRST, then the evidence buckets.

    Platform specs (9) then craft (140), before the three evidence buckets. The reason is
    quota, and it was learned the expensive way on copywriting's first import: the large
    buckets overflow past the ~136-per-notebook cap and consume notebook-CREATION quota
    building continuations, and when that quota ran out mid-push the craft notebook -
    the one thing explicitly asked for - had never been created at all.

    Both leading buckets are quarantines, so if anything is going to survive a partial
    run it should be these two.
    """
    return [
        (PLATFORM_BUCKET[0], PLATFORM_BUCKET[1], ()),
        (CRAFT_BUCKET[0], CRAFT_BUCKET[1], ()),
    ] + list(BUCKETS)


def ensure_notebook(title, state, key):
    if state.get(key, {}).get("id"):
        return state[key]["id"]
    ok, res = nb("create", title, "--json")
    if not ok:
        raise SystemExit(f"create failed for {title!r}: {res}")
    # v0.8.1 wraps single objects: {"notebook": {"id": ...}}, the same way `list` returns
    # {"notebooks": [...]}. v0.7.1 returned the object bare. Accept both.
    nid = None
    if isinstance(res, dict):
        nid = res.get("id") or (res.get("notebook") or {}).get("id")
    if not nid:
        raise SystemExit(f"could not read notebook id from: {res}")
    state.setdefault(key, {})["id"] = nid
    state[key]["title"] = title
    save_state(state)
    log(f"created notebook {title!r} -> {nid}")
    return nid


def existing_urls(nid):
    ok, res = nb("source", "list", "-n", nid, "--json", timeout=300)
    if not ok or not isinstance(res, dict):
        return set()
    urls = set()
    for s in res.get("sources", []):
        for field in ("url", "source_url", "title"):
            if s.get(field):
                urls.add(str(s[field]).strip().rstrip("/"))
    return urls


def push(limit=None):
    buckets, orphans = plan()
    if orphans:
        log(f"WARN {len(orphans)} sources matched no bucket, appending to craft")
        buckets["craft"].extend(orphans)

    state = load_state()
    added = failed = skipped = 0

    for title, key, _ in all_buckets():
        srcs = buckets[key]
        nid = ensure_notebook(title, state, key)
        have = existing_urls(nid)
        log(f"=== {title} :: {len(srcs)} planned, {len(have)} already present ===")

        # A full notebook rejects EVERY add with the same generic rpc_code=9 that a
        # fetch failure gives, so the only way to tell them apart is the streak: a
        # paywalled URL fails alone, a full notebook fails on everything including
        # plain text. Observed cap on this account was 136, not the 300 the Pro tier
        # implies, so overflow is handled rather than assumed away.
        part, streak = 1, 0
        for s in srcs:
            if limit and added >= limit:
                log("hit --limit, stopping")
                return added, failed, skipped
            url = s["url"].strip()
            if url.rstrip("/") in have or s["title"].strip() in have:
                skipped += 1
                continue

            if streak >= FULL_STREAK:
                part += 1
                ckey = f"{key}_part{part}"
                ctitle = f"{title.replace(' (NexusPoint)', '')} {_roman(part)} (NexusPoint)"
                log(f"  notebook looks full after {streak} consecutive failures "
                    f"-> overflowing into {ctitle!r}")
                nid = ensure_notebook(ctitle, state, ckey)
                have = existing_urls(nid)
                streak = 0

            ok, res = nb("source", "add", url, "-n", nid, "--type", "url", timeout=180)

            # An expired session fails EVERY add, which the streak counter reads as a
            # full notebook - and it then spends the scarce notebook-creation quota
            # making a continuation nobody needs. That happened for real on the
            # 05:14 run, which created 'Persuasion Evidence II' for no reason and tried
            # to create III. Auth death is fatal and distinguishable, so check it first.
            if not ok and "Authentication expired" in str(res):
                log("ABORT: NotebookLM session expired. Run `notebooklm login`, then "
                    "re-run this script - it resumes from where it stopped.")
                return added, failed, skipped
            if ok:
                added += 1
                streak = 0
                have.add(url.rstrip("/"))
                if added % 10 == 0:
                    log(f"  added {added} (last: [s{s['index']}] {s['title'][:60]})")
            else:
                failed += 1
                streak += 1
                log(f"  FAIL [s{s['index']}] {str(res)[:140]} :: {url[:90]}")
            time.sleep(1.0)  # be polite; this is an unofficial API surface

    return added, failed, skipped


def status():
    state = load_state()
    for title, key, _ in all_buckets():
        nid = state.get(key, {}).get("id")
        if not nid:
            print(f"{title}: not created")
            continue
        ok, res = nb("source", "list", "-n", nid, "--json", timeout=300)
        n = len(res.get("sources", [])) if ok and isinstance(res, dict) else "?"
        print(f"{title}: {n} sources  [{nid}]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    if a.plan:
        b, o = plan()
        for title, key, _ in all_buckets():
            conf = sum(1 for s in b[key] if s["tier"] == "confirmed")
            print(f"{title}\n   {len(b[key])} sources ({conf} confirmed / "
                  f"{len(b[key]) - conf} practitioner)")
        print(f"orphans (no bucket): {len(o)}")
    elif a.status:
        status()
    else:
        A, F, S = push(a.limit)
        log(f"DONE added={A} failed={F} skipped={S}")
        # Exit non-zero on failures. The first run reported exit 0 with 144 of 314
        # sources missing, because the shell pipeline's status came from `tail`.
        sys.exit(1 if F else 0)
