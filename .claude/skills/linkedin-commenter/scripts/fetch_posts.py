"""Recent posts from a target profile list -> a dated markdown file with empty comment slots.

Aleem opens the file, reads each post, pastes the drafted comment on LinkedIn. Nothing here
automates the commenting itself, and no LinkedIn session or cookie is ever used: the Apify actor
runs on Apify's own infrastructure, so his account is never touched.

The comments are NOT written here. Claude drafts them in-session by editing the file this script
produces (see SKILL.md). That split is deliberate. leads-to-crm/scripts/messages.py documents two
separate incidents where a fixed API prompt made a whole batch of generated copy converge on one
shape, and comments are shorter and more public than DMs, so they get the higher-quality path.

How the ranking works, and why it is a score rather than a threshold:
  - comment count is a COMPETITION signal. Being reply #250 on a 700-comment post is worth
    nothing; being #6 on a post still climbing is the whole play.
  - so the score is attention VELOCITY divided by how crowded the comment section already is.
    A hard "drop anything past 40 comments" cutoff was tried first and returned almost nothing
    on a list of large creators (measured 2026-07-31: of 9 posts, comment counts ran 28 to 650,
    and only one cleared 40). Scoring instead of cutting means the run always surfaces the best
    available targets and lets the ranking say how good they actually are.
  - dividing by comment count also does the audience-size normalisation that follower counts
    would have done. Big accounts have high likes AND high comments, so they self-normalise.
    This matters because the actor returns no follower count at all (verified 2026-07-31).
  - a 96h window guarantees the last few days' posts reappear on the next run, so a seen-ledger is
    load-bearing, not a nicety.

Usage:
    python fetch_posts.py                          # the daily run
    python fetch_posts.py --dry-run                # print the ranked table, write nothing
    python fetch_posts.py --dry-run --limit-profiles 3   # cheap schema check
    python fetch_posts.py --max-age-h 168          # after a 5+ day gap (168h is the actor's own cap)
    python fetch_posts.py --ignore-seen            # re-surface posts already shown

Profiles file (default `docs/linkedin-profiles-posts.txt`, gitignored):
    one profile URL per line, blanks ignored, ?lipi= tracking suffixes stripped.
    A line may optionally be CSV: url,tier,followers
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # scripts/ -> linkedin-commenter/ -> skills/ -> .claude/ -> repo
sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))

from _env import load_env  # noqa: E402
from engines.apify_engine import run_actor  # noqa: E402

# _env loads lazily inside get_keys(), which fires too late for argparse defaults to see anything
# it sets. Load at import time so flag defaults and the Apify key lookup agree.
load_env()

ACTOR = "harvestapi/linkedin-profile-posts"
DEFAULT_PROFILES = REPO / "docs" / "linkedin-profiles-posts.txt"
OUT_DIR = REPO / "docs" / "linkedin-comments"
SEEN_PATH = OUT_DIR / ".seen.json"
SEEN_KEEP = 1500  # a few months of runs; keeps the ledger from growing without bound


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def _clean_profile_url(raw: str) -> str:
    """Strip LinkedIn's ?lipi= / ?mini= tracking suffix and normalise the trailing slash.

    Aleem copies these straight out of the feed, so every URL arrives with a tracking blob
    attached. Two copies of the same profile with different blobs would otherwise be scraped twice.
    """
    url = raw.strip().split("?", 1)[0].rstrip("/")
    return url


def load_targets(path: Path) -> list[dict]:
    """One dict per profile. Accepts a plain URL per line, or `url,tier` CSV form.

    The plain form is what Aleem actually maintains, so it is the path that must not break. The CSV
    form is supported so the older references/linkedin-comment-targets.csv still parses if this is
    ever pointed at it; its third column (followers) is read and ignored, since the ranking no
    longer needs it.
    """
    if not path.exists():
        sys.exit(f"No profiles file at {path}. Add one LinkedIn profile URL per line, then re-run.")

    seen, rows = set(), []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        url = _clean_profile_url(parts[0])
        if "linkedin.com/in/" not in url.lower():
            continue  # header rows ("url,tier,followers") and stray text fall out here
        if url.lower() in seen:
            continue
        seen.add(url.lower())
        rows.append({
            "url": url,
            "handle": url.rstrip("/").split("/")[-1].lower(),
            "tier": (parts[1].lower() if len(parts) > 1 and parts[1] else "?"),
        })

    if not rows:
        sys.exit(f"{path} has no usable LinkedIn profile URLs yet.")
    return rows


# ---------------------------------------------------------------------------
# Seen ledger
# ---------------------------------------------------------------------------

def load_seen() -> set[str]:
    if not SEEN_PATH.exists():
        return set()
    try:
        return set(json.loads(SEEN_PATH.read_text(encoding="utf-8")).get("urls", []))
    except (json.JSONDecodeError, OSError):
        return set()  # a corrupt ledger costs one day of repeats, never a crashed run


def save_seen(urls: set[str], last_run: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_PATH.write_text(
        json.dumps({"last_run": last_run, "urls": sorted(urls)[-SEEN_KEEP:]}, indent=1),
        encoding="utf-8",
    )


def days_since_last_run() -> float | None:
    """How long since the last real run, so the caller can widen the age window after a gap."""
    if not SEEN_PATH.exists():
        return None
    try:
        stamp = json.loads(SEEN_PATH.read_text(encoding="utf-8")).get("last_run", "")
        return (datetime.now() - datetime.fromisoformat(stamp)).total_seconds() / 86400
    except (json.JSONDecodeError, OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Fetch + score
# ---------------------------------------------------------------------------

def fetch_posts(targets: list[dict], per_profile: int, timeout: int) -> list[dict]:
    """One actor run for all profiles. Returns raw dataset items."""
    return run_actor(
        ACTOR,
        {
            "targetUrls": [t["url"] for t in targets],
            "maxPosts": per_profile,
            "postedLimit": "week",          # narrowed further by the age window below
            "includeReposts": False,        # the original author isn't in a repost's comments
            "includeQuotePosts": False,
            "scrapeReactions": False,       # counts come free; the full lists cost extra
            "scrapeComments": False,
        },
        max_items=per_profile * len(targets) + 10,
        timeout_secs=timeout,
    )


def _int(val) -> int:
    m = re.search(r"\d+", str(val or "").replace(",", ""))
    return int(m.group(0)) if m else 0


# Smoothing added to the comment count before dividing. Without it a post with 0 comments divides
# by zero, and a post with 1 comment and 3 likes would outrank everything on a technicality. 10 is
# roughly "the number of comments by which a section stops feeling empty", so below that the score
# is dominated by real attention rather than by the crowding term.
_CROWDING_FLOOR = 10


def score_posts(items: list[dict], targets: list[dict], args, seen: set[str]) -> tuple[list[dict], dict]:
    """Filter, score, sort. Returns (kept_rows, drop_counts)."""
    by_handle = {t["handle"]: t for t in targets}
    now_ms = time.time() * 1000
    drops = {"not_post": 0, "no_timestamp": 0, "age": 0, "saturated": 0, "seen": 0, "no_url": 0}
    out = []

    for it in items:
        if it.get("type") != "post":
            drops["not_post"] += 1
            continue

        url = it.get("linkedinUrl") or ""
        if not url:
            drops["no_url"] += 1
            continue
        if url in seen:
            drops["seen"] += 1
            continue

        ts = (it.get("postedAt") or {}).get("timestamp")
        if not ts:
            drops["no_timestamp"] += 1
            continue
        age_h = (now_ms - float(ts)) / 3_600_000
        if not (args.min_age_h <= age_h <= args.max_age_h):
            drops["age"] += 1
            continue

        eng = it.get("engagement") or {}
        likes, comments, shares = _int(eng.get("likes")), _int(eng.get("comments")), _int(eng.get("shares"))
        if comments > args.max_comments:
            drops["saturated"] += 1     # the comment would be buried
            continue

        author = it.get("author") or {}
        handle = (author.get("publicIdentifier") or "").lower()
        tgt = by_handle.get(handle, {})

        # Attention flowing in per hour, divided by how many people are already talking. A share
        # weighs more than a like because it is higher intent. Clamping age at 1h stops a
        # 20-minute-old post with 3 likes from posting an absurd velocity.
        velocity = (likes + 3 * shares) / max(age_h, 1.0)
        score = round(velocity / (comments + _CROWDING_FLOOR), 2)

        out.append({
            "tier": tgt.get("tier", "?"),
            "author": author.get("name") or handle or "unknown",
            "headline": (author.get("info") if isinstance(author.get("info"), str) else "") or "",
            "age_h": age_h,
            "likes": likes, "comments": comments, "shares": shares,
            "velocity": round(velocity, 1),
            "score": score,
            "url": url,
            "text": (it.get("content") or "").strip(),
        })

    out.sort(key=lambda r: r["score"], reverse=True)
    return out[: args.top], drops


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _quote(text: str) -> str:
    """Post body as a markdown blockquote, blank lines kept so the original shape survives."""
    if not text:
        return "> (no text content, likely an image or video post)"
    return "\n".join(f"> {ln}" if ln.strip() else ">" for ln in text.splitlines())


def render(rows: list[dict], args) -> str:
    today = date.today().isoformat()
    head = [
        f"# LinkedIn comment targets, {today}",
        "",
        f"{len(rows)} posts, ranked best-first by attention velocity divided by how crowded the "
        f"comment section already is. Age window {args.min_age_h:g}-{args.max_age_h:g}h.",
        "",
        "Draft each comment against `references/comment-craft.md`, then read the whole batch "
        "together before posting. Delete any slot where there is nothing true and specific to say: "
        "a skipped post costs nothing, a filler comment costs credibility.",
        "",
        "---",
        "",
    ]
    body = []
    for i, r in enumerate(rows, 1):
        meta = f"{int(r['age_h'])}h  |  {r['likes']} likes / {r['comments']} comments"
        if r["shares"]:
            meta += f" / {r['shares']} shares"
        meta += f"  |  score {r['score']}"
        body += [
            f"## {i}. {r['author']}",
            f"{meta}  |  [open the post]({r['url']})",
            "",
            _quote(r["text"]),
            "",
            "**Comment draft:**",
            "",
            "",
            "---",
            "",
        ]
    return "\n".join(head + body)


def print_table(rows: list[dict]) -> None:
    print(f"  {'#':>3} {'score':>6} {'author':<26} {'age':>5} {'likes':>6} {'cmts':>5}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>3} {r['score']:>6} {r['author'][:26]:<26} {int(r['age_h']):>4}h "
              f"{r['likes']:>6} {r['comments']:>5}  {r['url']}")


# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    # 1h, not the 6h this was inherited with. Measured 2026-07-31: a large creator's post carried
    # 28 comments at 4.9h and 76 by 10.4h, so a 6h floor was excluding exactly the window where
    # being early is still possible. Being early is the entire play.
    p.add_argument("--min-age-h", type=float, default=1.0)
    # 96h (4 days), widened from 48h/2 days 2026-08-03 so profiles that post every 3-4 days still
    # surface instead of aging out. Still well inside the actor's own "week" postedLimit below.
    p.add_argument("--max-age-h", type=float, default=96.0)
    # A safety valve for the genuinely hopeless, not the main filter: crowding is priced into the
    # score, so a 250-comment post can still surface if nothing better exists, and will rank last.
    p.add_argument("--max-comments", type=int, default=400)
    p.add_argument("--per-profile", type=int, default=3)
    # 25, widened from 12 2026-08-03 alongside the age window so the wider pool actually reaches
    # more of the drafted batch instead of being cut off at the old ceiling.
    p.add_argument("--top", type=int, default=25)
    p.add_argument("--timeout", type=int, default=280)
    p.add_argument("--limit-profiles", type=int, default=0, help="only scrape the first N (cheap check)")
    p.add_argument("--ignore-seen", action="store_true", help="re-surface posts already shown")
    p.add_argument("--dry-run", action="store_true", help="print the ranking, write nothing")
    args = p.parse_args()

    targets = load_targets(args.profiles)
    if args.limit_profiles:
        targets = targets[: args.limit_profiles]
    print(f"[targets] {len(targets)} profiles from {args.profiles}")

    gap = days_since_last_run()
    if gap is not None and gap * 24 > args.max_age_h:
        print(f"[note] last run was {gap:.1f} days ago, wider than the {args.max_age_h:g}h window. "
              f"Consider --max-age-h {min(gap * 24, 168):.0f} to cover the gap.")

    seen = set() if args.ignore_seen else load_seen()
    items = fetch_posts(targets, args.per_profile, args.timeout)
    print(f"[apify] {len(items)} items fetched (~${len(items) * 0.002:.2f})")

    rows, drops = score_posts(items, targets, args, seen)
    dropped = ", ".join(f"{k}={v}" for k, v in drops.items() if v)
    print(f"[filter] {len(rows)} kept" + (f" | dropped: {dropped}" if dropped else ""))
    if not rows:
        print("Nothing passed the filters. Try --max-age-h 168 (the actor's own cap), a higher "
              "--max-comments, or --ignore-seen if everything recent was already surfaced.")
        return

    print_table(rows)

    if args.dry_run:
        print("\n[dry-run] nothing written.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{date.today().isoformat()}.md"
    out_path.write_text(render(rows, args), encoding="utf-8")
    save_seen(seen | {r["url"] for r in rows}, datetime.now().isoformat(timespec="seconds"))
    print(f"\n[write] {len(rows)} posts -> {out_path}")
    print("Next: draft a comment under each post, then review the batch together.")


if __name__ == "__main__":
    main()
