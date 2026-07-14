---
name: free-for-dev-scout
description: >
  Finds free developer-tier cloud, SaaS, and PaaS services by topic or use case, sourced from a
  local catalog of ~1,250 services across 57 categories (Major Cloud Providers, CI/CD, Managed
  Data Services, Hosting, Email, Log Management, Monitoring, Authentication, CDN, Static Site
  Hosting, Generative AI, Analytics, and more), mirrored from github.com/ripienaar/free-for-dev.
  This is specifically about as-a-Service offerings with a genuine free tier (not free trials,
  not self-hosted software — for self-hosted alternatives use the selfhosted-scout skill instead).
  Pre-built catalog for instant answers; live Exa AI search as a fallback for anything not in
  the catalog.

  Always trigger this skill when the user wants a free tier of a cloud/dev/SaaS service for
  building or running something — even if they don't say "free-for-dev" by name. Trigger on:
  "free tier for X", "free hosting for X", "any free CI/CD services", "free database hosting",
  "free tier cloud provider", "what's free for devs", "free email sending service", "free CDN",
  "free monitoring/logging service", "free authentication service", "does X have a free tier",
  or when scoping a project and a free-tier service would help (hosting, CI, database, auth,
  email, monitoring, storage, etc.). This is the designated lookup source whenever searching for
  free developer/SaaS tiers by topic — check the catalog here before searching the open web.
argument-hint: "[category | service query | 'refresh']"
---

# Free-for-Dev Scout

Finds free developer-tier services — SaaS, PaaS, IaaS offerings with a genuine free tier aimed
at developers and infra practitioners. The catalog is pre-built from
[ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) (fast, no API cost) and
live-searchable via Exa AI on demand for anything the catalog misses.

**Scope note:** this list is strictly as-a-Service offerings with a real free tier (not a time-
limited trial). It does NOT cover self-hosted/open-source software you'd run yourself — for
"what's the open-source alternative to X that I can self-host," use the `selfhosted-scout` skill
instead. If a query is ambiguous between the two ("free X"), ask or check both.

## Categories

Major Cloud Providers, Cloud Management Solutions, Analytics/Events/Statistics, APIs/Data/ML,
Artifact Repos, BaaS, Low-code Platform, CDN and Protection, CI and CD, CMS, Code Generation,
Code Quality, Code Search and Browsing, Crash and Exception Handling, Data Visualization on Maps,
Managed Data Services, Design and UI, Dev Blogging Sites, DNS, Docker Related, Domain, Education
and Career Development, Email, Feature Toggles Management, Font, Forms, Generative AI, IaaS, IDE
and Code Editing, Mobile Number Verification, Issue Tracking and Project Management, Log
Management, Mobile App Distribution and Feedback, Management Systems, Messaging and Streaming,
Miscellaneous, Monitoring, PaaS, Package Build System, Payment and Billing Integration, Privacy
Management, Screenshot APIs, Flutter/iOS Build Tools, Search, Security and PKI, Authentication
and Authorization, Source Code Repos, Storage and Media Processing, Tunneling/WebRTC/WebSockets,
Testing, Team Collaboration Tools, Translation Management, Visitor Session Recording, Web
Hosting, Commenting Platforms, Browser-based Hardware Emulation, Remote Desktop Tools, Other
Free Resources.

This list is broad on purpose — if a query loosely matches one of these (e.g. "postgres hosting"
-> Managed Data Services, "send transactional email" -> Email), go straight to Catalog mode
instead of guessing.

---

## Mode Detection

Pick the mode from the user's message:

| Signal | Mode |
|--------|------|
| "free tier for X", "free hosting for Y", "any free [category] services" | **Catalog** (fast) |
| "does [specific product] have a free tier", "search for [niche/new service]" | **Live Search** (Exa) |
| "refresh", "update the catalog", "resync from free-for-dev" | **Refresh** |

When unsure: check the catalog first. It covers ~1,250 services, so most requests resolve there.
Only fall back to Live Search if the catalog has 0-1 relevant matches, or the user names a
specific product whose free tier isn't a clean category match.

---

## Catalog Mode

Read `catalog/free-for-dev.md` (path: `.claude/skills/free-for-dev-scout/catalog/free-for-dev.md`
from repo root). Find the matching category section, or scan across categories for keyword
matches in the service name or description if the query doesn't map cleanly to one category.

**Output format:**
```
**[Service Name]** — [Category]
- URL: [url]
- Free tier: [what's actually free — quote the specifics, not "free tier available"]
```

Show up to 10 relevant services. If fewer than 3 match, supplement with a Live Search
automatically — tell the user "checking Exa for more options...". Free-tier limits change
often, so if the entry's description looks vague or dated, say so and suggest verifying at the
URL before committing.

If `catalog/free-for-dev.md` is missing or empty, tell the user:
> "Catalog not built yet. Say 'refresh the free-for-dev catalog' to pull the latest list — takes a few seconds."

---

## Live Search Mode

Run from the repo root:
```
python .claude/skills/free-for-dev-scout/scripts/search_free_for_dev.py --query "[user's query]"
```

With optional category context:
```
python .claude/skills/free-for-dev-scout/scripts/search_free_for_dev.py --query "[query]" --category "[category]"
```

Parse the script output and present results inline, in the same output format as Catalog mode.
After showing results, offer: "Want me to add any of these to the catalog?" — if yes, append a
matching entry to `catalog/free-for-dev.md` under the right category by hand.

---

## Refresh Mode

Re-pulls and re-parses the free-for-dev README — takes a few seconds, no external API cost (a
plain GitHub fetch, not an Exa search).

Run from the repo root:
```
python .claude/skills/free-for-dev-scout/scripts/fetch_free_for_dev.py
```

When done, confirm: "Catalog updated — [N] services across [M] categories. Say 'free tier for X' to browse."

---

## Output Style

Keep it scannable — no paragraphs. Entries like:

**Open-Meteo** — Managed Data Services
- URL: https://open-meteo.com/
- Free tier: Global weather forecast API for non-commercial use, no signup

Group by category when showing 5+ results. For 10+ matches, ask which categories or use cases
matter most before dumping everything. When several services fit equally well, lead with whichever
has the most generous or least restrictive free tier (e.g. "free forever" beats "free for 12
months" beats "free trial with credit card required").
