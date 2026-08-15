#!/usr/bin/env python3
"""Mirror the copywriting corpus into NotebookLM, so the live-query tier can ask the
gathered evidence instead of re-searching the web.

    python push_to_notebooklm.py --plan     # show the split, create nothing
    python push_to_notebooklm.py            # create notebooks + import, resume-safe
    python push_to_notebooklm.py --status   # counts per notebook

Why two notebooks and not one: the corpus is 314 sources and a NotebookLM notebook caps
at 300 on this account (observed: "Marketing 2026 - What Works" holds 251). Splitting
also follows the precedent already in this account, where the SEO corpus lives in five
topically-scoped notebooks rather than one - a notebook that only knows about persuasion
mechanisms answers better than one that also holds advertising law.

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

EXE = Path(os.environ.get("APPDATA", "")) / "Python" / "Python314" / "Scripts" / "notebooklm.exe"

# Which pass a source has to appear in to land in each notebook. A source carries several
# topics, so first match wins and the buckets stay disjoint.
BUCKETS = [
    (
        "Copywriting 2026 - Persuasion Evidence (NexusPoint)",
        "persuasion",
        ("q1_headline_evidence", "q2_cta_button_copy", "q3_landing_page_structure",
         "q5_ad_copy_effectiveness", "q6_message_framing", "q7_social_proof_testimonials",
         "q8_scarcity_urgency_guarantees", "q9_readability_fluency_specificity",
         "q10_copy_length", "q11_voice_of_customer_language",
         "q12_benefits_features_construal", "q13_emotional_appeals",
         "q19_reading_scanning_eye_tracking",
         # Evidence-tier sources that happened to surface via the craft passes. They are
         # NOT craft (tier_of promoted them on domain), so they belong with the evidence.
         "q21_landing_page_teardowns", "q22_headline_hook_formulas",
         "q23_email_sequence_craft", "q24_ad_copy_craft_by_platform",
         "q25_cta_microcopy_craft", "q26_product_description_craft",
         "q28_copywriting_2026_technique_shifts"),
    ),
    (
        "Copywriting 2026 - AI Search, Law & Folklore (NexusPoint)",
        "aisearch_law",
        ("q14_aeo_geo_copy_2026", "q15_platform_format_conventions_2026",
         "q16_folklore_provenance_replication", "q4_email_copy_subject_lines",
         "q17_email_field_experiments", "q18_experiment_validity_replication",
         "q20_endorsement_disclosure_law",
         # platform-format passes belong with q15, which is already here
         "q27_platform_format_conventions_craft", "q29_platform_character_specs"),
    ),
]

# The craft tier gets its OWN notebook, routed by tier rather than by pass. Keeping it
# physically separate is the same quarantine the tier itself is: someone querying the
# craft notebook is asking "how do I write this", and cannot accidentally receive a
# teardown blog as though it were evidence.
CRAFT_BUCKET = ("Copywriting 2026 - Craft & Examples (NexusPoint)", "craft")


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
    seen, skipped_dead = set(), 0

    for s in data["sources"]:
        if s["url"].strip().rstrip("/") in dead:
            skipped_dead += 1
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
    """Push order: CRAFT FIRST, then the evidence buckets.

    Craft leads deliberately. It is 66 sources and fits one notebook, whereas the
    persuasion bucket is ~234 against a ~136 cap and therefore consumes
    notebook-CREATION quota overflowing into continuations. On the first attempt that
    quota ran out during persuasion and the craft notebook was never created at all -
    the one thing that had been explicitly asked for. Smallest complete bucket first.
    """
    return [(CRAFT_BUCKET[0], CRAFT_BUCKET[1], ())] + list(BUCKETS)


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
        log(f"WARN {len(orphans)} sources matched no bucket, appending to persuasion")
        buckets["persuasion"].extend(orphans)

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
