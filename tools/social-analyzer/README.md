# social-analyzer — username-correlation OSINT tool

Vendored copy of [qeeqbox/social-analyzer](https://github.com/qeeqbox/social-analyzer) (AGPL-3.0,
upstream `LICENSE` preserved; original upstream README kept at `UPSTREAM_README.md`). Checks a
username against ~1000 sites and reports which ones have a matching profile, with a 0-100 "rate"
confidence score per hit.

## What it actually does (read before using)

It answers **"does a profile page exist at this URL for this username"** — not **"is this the same
business/person."** There is no semantic verification step. Tested against two known-verified
`lead-generator` leads on 2026-07-13:

- `netrocket` → Facebook hit at **100%** was **wrong** (real page is `netrocketua`; `netrocket` is a
  different, unrelated account that happens to own the shorter handle). Instagram hit at 66.67% was
  correct, but only because it echoed a handle already confirmed via WebSearch.
- `gspcampaigns` → Facebook hit at 100% was plausible but **unverified** — no confirmed Facebook page
  exists for that business in our own records.
- Control test: a throwaway, almost-certainly-unregistered username (`nexustestcheck12345`) still came
  back "detected" — Facebook at **100%**, Instagram at 33%. Nothing real exists at either URL; this is
  the clearest evidence the "rate" score mostly reflects "the URL returned 200," not "a genuine profile
  exists there."

**Conclusion:** treat every hit as an unverified candidate, never a resolved value. Short/generic
usernames collide easily; a "100%" rate does not mean "confirmed match." Do not write its output
directly to a leads sheet — it still needs a manual or WebSearch-based identity check (page title,
bio, follower count, etc.) before being trusted, which is the same verification `lead-generator`
already does. Best fit is as a cheap first-pass candidate generator when WebSearch is quota-blocked,
not as a replacement for it.

## Setup

- Python deps: `pip install -r requirements.txt` (bs4, tld, termcolor, langdetect, requests, lxml,
  galeodes) — already installed under the system Python 3.12.
- No API key required; it's a direct HTTP prober.

## Usage — CLI

```bash
python tools/social-analyzer/app.py --username "handle" --websites "facebook instagram twitter linkedin" \
    --mode fast --filter good --method find --options "link rate" --output pretty
```

Site names must be **lowercase** (`facebook`, not `Facebook`) — capitalized names silently match zero
sites (`[Init] Selected websites: 0`) with no error.

- `--filter good` drops low-confidence noise; drop it to see everything including weak matches.
- `--mode fast` skips the slower NLP-heavy checks; use `--mode slow` for the fuller (still unverified)
  pass.
- `--output pretty` prints a readable table; other formats exist for piping to JSON.

## Notes / gotchas

- `data/sites.json` is the site-check database this tool ships with — required for it to run, kept
  in this vendored copy (~2.8MB total across `data/`).
- AGPL-3.0 licensed. Internal use only; don't fold its code into anything redistributed or
  productized without checking license obligations.
- `.git` history and `logs/` were stripped when vendoring in — this is a snapshot, not a live clone.
  Re-clone from upstream if a newer version is ever needed.
