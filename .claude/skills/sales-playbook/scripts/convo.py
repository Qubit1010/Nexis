"""Conversation memory for the sales-playbook skill.

Per-prospect conversation state in Supabase (table: conversations, see schema.sql).
Stdlib only; talks to the Supabase REST API (PostgREST) with urllib.

Usage (always prints JSON to stdout):
  python convo.py get <channel> <identity_or_url>
  python convo.py upsert <channel> <identity_or_url> [--name N] [--profile P]
                  [--stage S] [--meeting M] [--thread-file F] [--last-draft D]
  python convo.py list [--channel X]
  python convo.py delete <channel> <identity_or_url>

Env: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (repo .env or environment).
"""

import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

CHANNELS = ("linkedin", "instagram", "facebook")
STAGES = ("qualify", "label", "deepen", "proof", "objection", "ask", "booked", "dead")
MEETING_STATUSES = ("none", "asked", "booked", "declined", "ghosted")


# --- identity normalizers ---------------------------------------------------
# Copied from leads-to-crm/scripts/channels.py (_ig_norm_handle, _ig_handle_from_url,
# _li_slug); keep the regexes in sync if IG/LI URL formats ever change. FB is a
# light local version: a DM thread means the person is already known, so no need
# for the Firecrawl-backed group-post resolver.

_IG_SYSTEM_SEGMENTS = {
    "p", "reel", "reels", "tv", "explore", "stories", "live", "popular",
    "accounts", "direct", "about", "developer", "legal",
}


def _ig_norm_handle(text):
    h = (text or "").strip().lower().lstrip("@").rstrip("/")
    if "?" in h:
        h = h.split("?")[0]
    if not h or h in _IG_SYSTEM_SEGMENTS:
        return ""
    return h


def _ig_identity(raw):
    if "instagram.com" in (raw or "").lower():
        u = raw.strip().lower()
        for alt in ("secure.instagram.com", "www-fallback.instagram.com",
                    "www.latest.instagram.com", "m.instagram.com"):
            u = u.replace(alt, "www.instagram.com")
        m = re.search(r"instagram\.com/([^/?#]+)", u)
        return _ig_norm_handle(m.group(1)) if m else ""
    return _ig_norm_handle(raw)


def _li_identity(raw):
    if "linkedin.com" in (raw or "").lower():
        m = re.search(r"linkedin\.com/in/([^/?#]+)", raw.strip().lower())
        return m.group(1).rstrip("/") if m else ""
    return (raw or "").strip().lower().lstrip("@").rstrip("/")


def _fb_identity(raw):
    u = (raw or "").strip().lower()
    if "facebook.com" in u:
        m = re.search(r"[?&]id=(\d+)", u)
        if m:
            return f"id:{m.group(1)}"
        m = re.search(r"facebook\.com/([^/?#]+)", u)
        slug = m.group(1).rstrip("/") if m else ""
        return "" if slug in {"profile.php", "groups", "people", "pages"} else slug
    return u.lstrip("@").rstrip("/")


def normalize_identity(channel, raw):
    fn = {"instagram": _ig_identity, "linkedin": _li_identity, "facebook": _fb_identity}[channel]
    return fn(raw)


# Keep in sync with countExchanges() in the dashboard's src/lib/db.ts.
# An exchange = one prospect turn. Two formats supported:
# 1. The "[Me]: / [Them]:" prefix convention (explicit, preferred).
# 2. Raw copy-pasted DM exports: scan line by line, and treat a line as a new
#    speaker turn only if it "looks like a name" (short, no digits/sentence
#    punctuation, every word capitalized, trailing timestamp stripped first
#    since some exports - LinkedIn - put "Name   10:33 PM" on one line) OR it
#    exactly matches the known contact's handle (some IG handles are plain
#    lowercase, e.g. "hupru", so the Title-Case check alone would miss them).
#    NOT just any line after a blank line, since a single message can have
#    its own paragraph breaks (which would otherwise be miscounted as extra
#    turns) and exports often have standalone timestamp/read-receipt lines
#    ("05:38", "Seen 23m ago") mixed in. Aleem is the one constant name
#    across every conversation (the lead's name/handle varies), so any
#    recognized name line that isn't his is a prospect turn.
_SELF_NAMES = {"aleem", "aleem ul hassan", "aleem hassan"}
_TRAILING_TIME_RE = re.compile(r"\s+\d{1,2}[:.]\d{2}\s*([AaPp][Mm])?$")


def _strip_trailing_time(line):
    return _TRAILING_TIME_RE.sub("", line).strip()


def _looks_like_name(line):
    line = _strip_trailing_time(line.strip())
    if not line or len(line) > 40:
        return False
    words = line.split()
    if not words:
        return False
    for w in words:
        if not w[0].isupper() or not all(c.isalpha() or c in "'-" for c in w):
            return False
    return True


def count_exchanges(thread, contact_hint=None):
    text = thread or ""
    bracket_count = len(re.findall(r"^\s*\[?(them|prospect)\b", text, re.I | re.M))
    if bracket_count or re.search(r"^\s*\[?me\]?\s*:", text, re.I | re.M):
        return bracket_count

    hint = (contact_hint or "").strip().lower()
    count = 0
    for raw_line in text.splitlines():
        line = _strip_trailing_time(raw_line.strip())
        if not line:
            continue
        lower = line.lower()
        is_name = _looks_like_name(raw_line) or (hint and lower == hint)
        if is_name and lower not in _SELF_NAMES:
            count += 1
    return count


# --- Supabase REST client ---------------------------------------------------

def _load_env():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not (url and key):
        env_file = REPO_ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if "=" not in line or line.startswith("#"):
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == "SUPABASE_URL" and not url:
                    url = v
                elif k == "SUPABASE_SERVICE_ROLE_KEY" and not key:
                    key = v
    if not (url and key):
        fail("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set (env or repo .env)")
    return url.rstrip("/"), key


def _request(method, path, params=None, body=None, prefer=None):
    url, key = _load_env()
    qs = f"?{urllib.parse.urlencode(params)}" if params else ""
    req = urllib.request.Request(
        f"{url}/rest/v1/{path}{qs}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            **({"Prefer": prefer} if prefer else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode()
            return json.loads(text) if text.strip() else []
    except urllib.error.HTTPError as e:
        fail(f"Supabase {e.code}: {e.read().decode()[:300]}")
    except urllib.error.URLError as e:
        fail(f"Supabase unreachable: {e.reason}")


def fail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


# --- commands ----------------------------------------------------------------

def _ident_or_die(channel, raw):
    ident = normalize_identity(channel, raw)
    if not ident:
        fail(f"could not derive a {channel} identity from {raw!r}")
    return ident


def cmd_get(args):
    ident = _ident_or_die(args.channel, args.identity)
    rows = _request("GET", "conversations",
                    {"channel": f"eq.{args.channel}", "identity": f"eq.{ident}"})
    print(json.dumps(rows[0] if rows else {}, indent=2))


def cmd_upsert(args):
    ident = _ident_or_die(args.channel, args.identity)
    rec = {"channel": args.channel, "identity": ident,
           "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if args.name:
        rec["name"] = args.name
    if args.profile:
        rec["profile"] = args.profile
    if args.stage:
        if args.stage not in STAGES:
            fail(f"stage must be one of {STAGES}")
        rec["stage"] = args.stage
    if args.meeting:
        if args.meeting not in MEETING_STATUSES:
            fail(f"meeting must be one of {MEETING_STATUSES}")
        rec["meeting_status"] = args.meeting
    if args.last_draft:
        rec["last_draft"] = args.last_draft
    if args.thread_file:
        thread = Path(args.thread_file).read_text(encoding="utf-8-sig")
        rec["thread"] = thread
        rec["exchange_count"] = count_exchanges(thread, contact_hint=ident)
        rec["last_contact"] = datetime.date.today().isoformat()

    # Partial update when the row exists (merge-duplicates would blank
    # omitted columns on conflict via defaults only for new rows; PATCH keeps them).
    existing = _request("GET", "conversations",
                        {"channel": f"eq.{args.channel}", "identity": f"eq.{ident}",
                         "select": "id"})
    if existing:
        rows = _request("PATCH", "conversations",
                        {"channel": f"eq.{args.channel}", "identity": f"eq.{ident}"},
                        body=rec, prefer="return=representation")
    else:
        rows = _request("POST", "conversations", body=rec,
                        prefer="return=representation")
    print(json.dumps(rows[0] if rows else {}, indent=2))


def cmd_list(args):
    params = {"select": "channel,identity,name,stage,exchange_count,meeting_status,last_contact",
              "order": "updated_at.desc"}
    if args.channel:
        params["channel"] = f"eq.{args.channel}"
    print(json.dumps(_request("GET", "conversations", params), indent=2))


def cmd_delete(args):
    ident = _ident_or_die(args.channel, args.identity)
    _request("DELETE", "conversations",
             {"channel": f"eq.{args.channel}", "identity": f"eq.{ident}"})
    print(json.dumps({"deleted": f"{args.channel}/{ident}"}))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("get")
    g.add_argument("channel", choices=CHANNELS)
    g.add_argument("identity")
    g.set_defaults(fn=cmd_get)

    u = sub.add_parser("upsert")
    u.add_argument("channel", choices=CHANNELS)
    u.add_argument("identity")
    u.add_argument("--name")
    u.add_argument("--profile")
    u.add_argument("--stage")
    u.add_argument("--meeting")
    u.add_argument("--thread-file")
    u.add_argument("--last-draft")
    u.set_defaults(fn=cmd_upsert)

    l = sub.add_parser("list")
    l.add_argument("--channel", choices=CHANNELS)
    l.set_defaults(fn=cmd_list)

    d = sub.add_parser("delete")
    d.add_argument("channel", choices=CHANNELS)
    d.add_argument("identity")
    d.set_defaults(fn=cmd_delete)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
