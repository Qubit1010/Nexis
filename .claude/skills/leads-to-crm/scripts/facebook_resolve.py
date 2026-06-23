"""Facebook lead preprocessing — figure out WHO posted before the push.

Facebook is the odd channel: many scraped rows are *group posts* whose URL holds
the group, not the author (facebook.com/groups/<g>/posts/<id>/). For those the
person is buried in the scraped Name (post title) + Note (self-introduction)
text. This module turns every source row into a resolved author:

  - profile           facebook.com/<slug>/                 -> author = slug
  - profile id        facebook.com/profile.php?id=<n>      -> author = id:<n>
  - page/profile post facebook.com/<slug>/posts|videos/... -> author = slug
  - group post        facebook.com/groups/<g>/posts/<id>/  -> RESOLVE the author

Resolution order for group/page posts (cheap -> expensive, both optional):
  1. LLM-extract {name, first_name, role, company, location, profile_url} from the
     Name+Note text already in the sheet (OpenAI gpt-5.4-mini -> Claude fallback).
  2. Firecrawl the post URL as a backup to recover the real profile link (most FB
     group posts are login-walled, so this usually fails — that's expected).

Results are written to an idempotent cache (scripts/.cache/facebook_resolved.json)
keyed by the source URL, so the expensive LLM/scrape work runs once per URL.

Run standalone to preview:  python facebook_resolve.py --dry-run --limit 15
Or it runs automatically as FacebookChannel.preprocess() inside push.py.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import messages as msg
import sheets


CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_FILE = CACHE_DIR / "facebook_resolved.json"

SOURCE_SHEET_ID = "1ao7_Aam6bsI6D4xk-Mfc-EM54WZYivN9petcZU2P68U"
SOURCE_TAB = "Sheet1"

# URL path segments that are never a person/page slug.
_FB_SYSTEM = {
    "groups", "profile.php", "watch", "pages", "events", "marketplace", "photo",
    "photo.php", "story.php", "sharer", "sharer.php", "login", "help", "settings",
    "friends", "messages", "notifications", "reel", "reels", "share", "permalink",
    "permalink.php", "media", "hashtag", "public", "l.php", "home.php", "people",
    "bookmarks", "gaming", "live", "biz", "ads", "business",
}


# ---------------------------------------------------------------------------
# URL helpers — the identity primitives (shared with channels.FacebookChannel)
# ---------------------------------------------------------------------------

def fb_norm(slug):
    """Normalize a candidate slug: lowercase, strip query/trailing slash."""
    s = (slug or "").strip().lower()
    if "?" in s:
        s = s.split("?")[0]
    s = s.strip("/")
    return s


def fb_slug(url):
    """The first path segment of a facebook URL if it's a real slug, else ''."""
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^(www|web|m|mobile|business|free|d)\.facebook\.com", "facebook.com", u)
    m = re.search(r"facebook\.com/([^/?#]+)", u)
    if not m:
        return ""
    seg = m.group(1)
    if seg in _FB_SYSTEM:
        return ""
    return fb_norm(seg)


def fb_profile_id(url):
    """profile.php?id=<n> -> 'id:<n>', else ''."""
    m = re.search(r"profile\.php\?id=(\d+)", (url or "").lower())
    return f"id:{m.group(1)}" if m else ""


def fb_group_key(url):
    """groups/<g>/posts/<id> -> 'post:<g>/<id>' (stable per-post fallback key)."""
    m = re.search(r"facebook\.com/groups/([^/?#]+)/posts/([^/?#]+)", (url or "").lower())
    if m:
        return f"post:{m.group(1)}/{m.group(2)}"
    m = re.search(r"facebook\.com/groups/([^/?#]+)/permalink/([^/?#]+)", (url or "").lower())
    if m:
        return f"post:{m.group(1)}/{m.group(2)}"
    return ""


def fb_classify(url):
    """Return one of: 'profile', 'profile_id', 'page_post', 'group_post', 'unknown'."""
    if not url:
        return "unknown"
    u = url.strip().lower()
    if "profile.php?id=" in u:
        return "profile_id"
    if "/groups/" in u:
        return "group_post"
    slug = fb_slug(u)
    if not slug:
        return "unknown"
    # slug present: a bare profile/page, or a post/video/photo under that slug
    if re.search(rf"facebook\.com/{re.escape(slug)}/(posts|videos|photos|reels?|media)/", u):
        return "page_post"
    return "profile"


def profile_url_from_identity(identity):
    """Build a canonical profile URL from a resolved slug/id identity ('' if not a URL key)."""
    if not identity:
        return ""
    if identity.startswith("id:"):
        return f"https://www.facebook.com/profile.php?id={identity[3:]}"
    if identity.startswith(("name:", "post:")):
        return ""
    return f"https://www.facebook.com/{identity}/"


# ---------------------------------------------------------------------------
# LLM extraction from the scraped Name + Note text
# ---------------------------------------------------------------------------

_EXTRACT_SYSTEM = """You extract the author of a Facebook post from messy scraped text.
The text is a post title plus a body snippet, often a self-introduction in a business group
("Hi, I'm Mary, I run a digital marketing agency..."). Identify the PERSON who wrote it.

Return ONLY a JSON object, no prose, with these keys:
  "name":        full name of the author, or "" if no real person name is present
  "first_name":  their first name, or ""
  "role":        their job title/role if stated (e.g. "Founder", "CEO"), else ""
  "company":     their company/agency name if stated, else ""
  "location":    their location if stated, else ""
  "profile_url": a facebook.com profile URL ONLY if one literally appears in the text, else ""

Rules: Do not invent a name. If the text is only a generic title with no personal
introduction ("Introduction to Digital Marketing Agency CEO"), return "" for name. Never
guess a profile_url. Output must be valid JSON."""


def _extract_json(text):
    if not text:
        return {}
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text).rstrip("`").strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


def llm_extract_author(gen, name_text, note_text):
    """Use the message Generator's providers to extract author fields. {} on failure."""
    if gen is None or not gen.available:
        return {}
    user = (
        f"Post title: {name_text or '(none)'}\n"
        f"Post body: {(note_text or '(none)')[:900]}\n\n"
        "Extract the author as JSON."
    )
    # Reuse the Generator's provider chain (OpenAI primary -> Claude fallback).
    if gen.openai:
        try:
            raw = gen._via_openai(_EXTRACT_SYSTEM, user, 300)
            data = _extract_json(raw)
            if data:
                return data
        except Exception as e:
            print(f"    extract openai failed: {str(e)[:90]}", flush=True)
    if gen.anthropic:
        try:
            raw = gen._via_anthropic(_EXTRACT_SYSTEM, user, 300)
            data = _extract_json(raw)
            if data:
                return data
        except Exception as e:
            print(f"    extract claude failed: {str(e)[:90]}", flush=True)
    return {}


# ---------------------------------------------------------------------------
# Firecrawl backup — best-effort author profile link recovery
# ---------------------------------------------------------------------------

# Firecrawl blanket-blocks facebook.com ("Website Not Supported"), so once we see
# that we stop trying for the rest of the run instead of burning ~200 doomed calls.
_FIRECRAWL_DISABLED = False


def firecrawl_author_url(post_url):
    """Try to recover an author profile URL by scraping the post. '' if unavailable."""
    global _FIRECRAWL_DISABLED
    if _FIRECRAWL_DISABLED:
        return ""
    key = msg._load_key("FIRECRAWL_API_KEY")
    if not key:
        return ""
    try:
        from firecrawl import Firecrawl
    except ImportError:
        return ""
    try:
        app = Firecrawl(api_key=key)
        res = app.scrape(post_url, formats=["markdown", "html"], timeout=25000,
                         only_main_content=False)
        if isinstance(res, dict):
            blob = (res.get("markdown") or "") + "\n" + (res.get("html") or "")
        else:
            blob = (getattr(res, "markdown", "") or "") + "\n" + (getattr(res, "html", "") or "")
        # Prefer a real /<slug>/ or profile.php link that isn't the group itself.
        for m in re.finditer(r"facebook\.com/(profile\.php\?id=\d+|[A-Za-z0-9.\-]+)", blob):
            cand = m.group(0)
            if "/groups/" in cand:
                continue
            if "profile.php?id=" in cand:
                return "https://www.facebook.com/" + cand.split("facebook.com/")[1]
            slug = fb_slug("https://" + cand)
            if slug:
                return f"https://www.facebook.com/{slug}/"
    except Exception as e:
        emsg = str(e)
        if "not supported" in emsg.lower() or "no longer supported" in emsg.lower():
            _FIRECRAWL_DISABLED = True
            print("    firecrawl: facebook.com not supported — disabling backup for this run",
                  flush=True)
        else:
            print(f"    firecrawl failed: {emsg[:90]}", flush=True)
    return ""


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Resolve one row -> a record dict (the thing the cache stores)
# ---------------------------------------------------------------------------

def _clean_name_handle(raw_name):
    """'Matthew Capala (@matt.capala)' -> ('Matthew Capala', 'matt.capala')."""
    m = re.search(r"\(@([^)]+)\)", raw_name or "")
    handle = m.group(1).strip().lower() if m else ""
    clean = re.sub(r"\s*\(@[^)]+\)", "", raw_name or "").strip()
    return clean, handle


def resolve_row(url, name_text, note_text, location_raw, company_raw, gen,
                use_firecrawl=True):
    """Return a resolved record for one source URL."""
    kind = fb_classify(url)
    rec = {
        "type": kind, "name": "", "first_name": "", "company": company_raw or "",
        "role": "", "location": location_raw or "", "profile_url": "", "note": note_text or "",
        "identity": "", "status": "New",
    }

    if kind in ("profile", "page_post", "profile_id"):
        ident = fb_profile_id(url) if kind == "profile_id" else fb_slug(url)
        rec["identity"] = ident
        rec["profile_url"] = profile_url_from_identity(ident) or url
        rec["status"] = "New"
        clean, handle = _clean_name_handle(name_text)
        # A bare profile usually carries the real person name in Name. A page_post's
        # Name is a post title, so LLM-extract the person for those.
        if kind == "profile":
            rec["name"] = clean
        if kind == "page_post" or not rec["name"]:
            data = llm_extract_author(gen, name_text, note_text)
            if data.get("name"):
                rec["name"] = data["name"]
                rec["first_name"] = data.get("first_name", "")
                rec["role"] = data.get("role", "") or rec["role"]
                rec["company"] = data.get("company", "") or rec["company"]
                rec["location"] = data.get("location", "") or rec["location"]
        if not rec["name"]:
            rec["name"] = clean or handle or ident
        if not rec["first_name"]:
            rec["first_name"] = (rec["name"].split()[0] if rec["name"] and " " in rec["name"]
                                 else (rec["name"] if rec["name"] and not any(
                                     c in rec["name"] for c in ".-_") else ""))
        return rec

    if kind == "group_post":
        data = llm_extract_author(gen, name_text, note_text)
        rec["name"] = data.get("name", "")
        rec["first_name"] = data.get("first_name", "")
        rec["role"] = data.get("role", "") or rec["role"]
        rec["company"] = data.get("company", "") or rec["company"]
        rec["location"] = data.get("location", "") or rec["location"]
        prof = data.get("profile_url", "")
        if not prof and use_firecrawl:
            prof = firecrawl_author_url(url)
        if prof:
            slug = fb_profile_id(prof) or fb_slug(prof)
            if slug:
                rec["identity"] = slug
                rec["profile_url"] = profile_url_from_identity(slug) or prof
                rec["status"] = "New"
                if not rec["first_name"] and rec["name"]:
                    rec["first_name"] = rec["name"].split()[0]
                return rec
        # Full name but no profile URL -> name-key identity (dedups the same person
        # posting across multiple groups) and push flagged so Aleem grabs the link.
        rec["status"] = "Find Profile"
        if rec["name"] and " " in rec["name"].strip():
            rec["identity"] = "name:" + fb_norm(re.sub(r"[^a-z0-9]+", "-", rec["name"].lower())).strip("-")
            if not rec["first_name"]:
                rec["first_name"] = rec["name"].split()[0]
            return rec
        # Only a first name (or a single token): too collision-prone to dedup on, so
        # key on the unique post URL but still show the first name in the CRM.
        if rec["first_name"] or rec["name"]:
            rec["name"] = rec["name"] or rec["first_name"]
            rec["first_name"] = rec["first_name"] or rec["name"]
            rec["identity"] = fb_group_key(url)
            return rec
        # Nothing usable: keep the post key so exact-dup posts still dedup.
        rec["identity"] = fb_group_key(url)
        return rec

    # unknown
    rec["identity"] = ""
    rec["status"] = "Needs Review"
    return rec


# ---------------------------------------------------------------------------
# Build / refresh the cache over the whole source sheet
# ---------------------------------------------------------------------------

def build_cache(dry_run=False, limit=0, refresh=False, use_firecrawl=True, verbose=True):
    import channels as ch  # local import to avoid a cycle at module load
    channel = ch.CHANNELS["facebook"]

    src = sheets.read_values(SOURCE_SHEET_ID, SOURCE_TAB)
    if not src:
        tab = sheets.first_tab_title(SOURCE_SHEET_ID)
        src = sheets.read_values(SOURCE_SHEET_ID, tab)
    if not src:
        print("No Facebook source data.")
        return {}
    header, rows = src[0], src[1:]
    col_map = ch.build_col_map(header, channel.source_aliases)
    status_idx = sheets.header_index(header, channel.status_header_names)

    cache = {} if refresh else load_cache()
    gen = msg.get_client()

    counts = {"profile": 0, "page_post": 0, "profile_id": 0, "group_post": 0, "unknown": 0}
    resolved_url = 0
    name_only = 0
    processed = 0

    for row in rows:
        if not any(c.strip() for c in row):
            continue
        status = row[status_idx].strip().lower() if status_idx is not None and status_idx < len(row) else ""
        if status == "added":
            continue
        url, raw_name = ch.split_url_and_name(row, col_map)
        if not url:
            continue
        if url in cache:
            counts[cache[url].get("type", "unknown")] = counts.get(cache[url].get("type", "unknown"), 0) + 1
            continue
        if limit and processed >= limit:
            break

        note = ch.cell(row, col_map, "bio")
        location_raw = ch.cell(row, col_map, "location")
        company_raw = ch.cell(row, col_map, "company")
        rec = resolve_row(url, raw_name, note, location_raw, company_raw, gen,
                          use_firecrawl=use_firecrawl)
        cache[url] = rec
        counts[rec["type"]] = counts.get(rec["type"], 0) + 1
        if rec["profile_url"] and rec["status"] == "New":
            resolved_url += 1
        elif rec["status"] == "Find Profile":
            name_only += 1
        processed += 1
        if verbose:
            tag = rec["name"] or "(no name)"
            print(f"  [{rec['type']:<11}] {str(tag)[:34]:<34} id={rec['identity'][:36]:<36} "
                  f"{rec['status']}", flush=True)

    if verbose:
        print(f"\n  types: {counts}")
        print(f"  resolved to a profile URL: {resolved_url} | name-only (Find Profile): {name_only}")
        print(f"  newly processed this run: {processed}")

    if not dry_run:
        save_cache(cache)
        if verbose:
            print(f"  cache written: {CACHE_FILE}")
    elif verbose:
        print("  [DRY RUN] cache not written")
    return cache


def main():
    p = argparse.ArgumentParser(description="Resolve Facebook group-post authors before the push.")
    p.add_argument("--dry-run", action="store_true", help="Resolve + preview, do not write the cache")
    p.add_argument("--limit", type=int, default=0, help="Cap newly-resolved rows (test runs)")
    p.add_argument("--refresh", action="store_true", help="Ignore the existing cache and rebuild")
    p.add_argument("--no-firecrawl", action="store_true", help="Skip the Firecrawl backup (Note text only)")
    args = p.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=== facebook_resolve ===")
    build_cache(dry_run=args.dry_run, limit=args.limit, refresh=args.refresh,
                use_firecrawl=not args.no_firecrawl)


if __name__ == "__main__":
    main()
