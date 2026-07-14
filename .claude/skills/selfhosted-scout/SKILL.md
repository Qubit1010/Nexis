---
name: selfhosted-scout
description: >
  Finds free, open-source, self-hosted software by topic or use case — the software you run on
  your own server as an alternative to a SaaS product — sourced from a local catalog of ~1,240
  projects across 83 categories (Analytics, CRM, CMS, E-commerce, File Transfer, Media Streaming,
  Monitoring, Password Managers, Project Management, Note-taking, Video Conferencing, and more),
  mirrored from github.com/awesome-selfhosted/awesome-selfhosted. Each entry includes license,
  platform/language, and description. This is specifically about software you self-host (not a
  hosted free tier — for as-a-Service free tiers use the free-for-dev-scout skill instead).
  Pre-built catalog for instant answers; live Exa AI search as a fallback for anything not in
  the catalog.

  Always trigger this skill when the user wants an open-source or self-hosted alternative to a
  SaaS product, or software to run on their own server — even if they don't say "selfhosted-
  scout" by name. Trigger on: "self-hosted alternative to X", "open source alternative to X",
  "what can I self-host for X", "free open source CRM/CMS/analytics/etc", "self host my own X",
  "run my own X instead of paying for it", "open source X I can host myself", or when scoping
  infrastructure and a self-hosted option would help. This is the designated lookup source
  whenever searching for self-hosted software by topic — check the catalog here before searching
  the open web.
argument-hint: "[category | software query | 'refresh']"
---

# Self-Hosted Scout

Finds free, open-source software you can self-host as an alternative to SaaS. The catalog is
pre-built from [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)
(fast, no API cost) and live-searchable via Exa AI on demand for anything the catalog misses.

**Scope note:** this list is strictly Free/open-source software you host yourself. It does NOT
cover as-a-Service free tiers hosted by someone else — for "what's free for my app if I don't
want to manage a server," use the `free-for-dev-scout` skill instead. If a query is ambiguous
between the two ("free X"), ask, or surface both.

## Categories

83 populated categories including: Analytics, Archiving and Digital Preservation, Automation,
Backup*, Blogging Platforms, Booking and Scheduling, Bookmarks and Link Sharing, Calendar &
Contacts, Communication (Custom/Email/IRC/SIP/Social/Video/XMPP), Content Management Systems
(CMS), Customer Relationship Management (CRM), Database Management, DNS, Document Management,
E-commerce, Feed Readers, File Transfer & Synchronization, Games, Genealogy, Generative AI
(GenAI), Groupware, Health and Fitness, Human Resources Management, Identity Management*,
Internet of Things, Inventory Management, Knowledge Management, Learning and Courses,
Manufacturing, Maps and GPS, Media Management, Media Streaming (Audio/Multimedia/Video)*,
Money/Budgeting, Monitoring & Status Pages*, Network Utilities, Note-taking & Editors, Password
Managers, Personal Dashboards, Project Management, Real Estate, Search Engines, Site Generators,
Task Management, URL Shorteners, Video Surveillance, VPN*, Web Servers, Wikis, and more.

*Categories marked with an asterisk are redirect-only in the source (they point to sub-categories
or an external list rather than listing entries directly) — if the catalog shows nothing for
one of these, check its named sub-categories (e.g. "Media Streaming - Audio Streaming") or fall
back to Live Search.

---

## Mode Detection

Pick the mode from the user's message:

| Signal | Mode |
|--------|------|
| "self-hosted alternative to X", "open source X I can host", "any self-hosted [category]" | **Catalog** (fast) |
| "search for [specific/niche project]", "is there a self-hosted [very specific thing]" | **Live Search** (Exa) |
| "refresh", "update the catalog", "resync from awesome-selfhosted" | **Refresh** |

When unsure: check the catalog first. It covers ~1,240 projects, so most requests resolve there.
Only fall back to Live Search if the catalog has 0-1 relevant matches, the category is one of
the redirect-only ones above, or the user names a specific SaaS product and wants its self-
hosted equivalent (scan descriptions for "alternative to [product]" phrasing — many entries
name the SaaS product they replace).

---

## Catalog Mode

Read `catalog/selfhosted.md` (path: `.claude/skills/selfhosted-scout/catalog/selfhosted.md` from
repo root). Find the matching category section, or scan across categories for keyword matches in
the project name or description (many descriptions explicitly say "alternative to X" — search for
the named SaaS product directly).

**Output format:**
```
**[Project Name]** — [Category]
- URL: [url]
- License: [license]
- Platform: [language/platform, e.g. Docker, Python, Go]
- About: [one-line description]
```

Show up to 10 relevant projects. If fewer than 3 match, supplement with a Live Search
automatically — tell the user "checking Exa for more options...". Flag any entry marked
`(unmaintained)` in the catalog — mention it explicitly rather than silently recommending
something that may no longer receive updates or security patches.

If `catalog/selfhosted.md` is missing or empty, tell the user:
> "Catalog not built yet. Say 'refresh the selfhosted catalog' to pull the latest list — takes a few seconds."

---

## Live Search Mode

Run from the repo root:
```
python .claude/skills/selfhosted-scout/scripts/search_selfhosted.py --query "[user's query]"
```

With optional category context:
```
python .claude/skills/selfhosted-scout/scripts/search_selfhosted.py --query "[query]" --category "[category]"
```

Parse the script output and present results inline, in the same output format as Catalog mode
(fill in License/Platform as "Unknown — verify at URL" since Exa results won't have these
pre-classified). After showing results, offer: "Want me to add any of these to the catalog?" —
if yes, append a matching entry to `catalog/selfhosted.md` under the right category by hand.

---

## Refresh Mode

Re-pulls and re-parses the awesome-selfhosted README — takes a few seconds, no external API cost
(a plain GitHub fetch, not an Exa search).

Run from the repo root:
```
python .claude/skills/selfhosted-scout/scripts/fetch_selfhosted.py
```

When done, confirm: "Catalog updated — [N] projects across [M] categories. Say 'self-hosted alternative to X' to browse."

---

## Output Style

Keep it scannable — no paragraphs. Entries like:

**Matomo** — Analytics
- URL: https://matomo.org/
- License: GPL-3.0
- Platform: PHP
- About: Web analytics that protects your data and your customers' privacy (alternative to Google Analytics)

Group by category when showing 5+ results. For 10+ matches, ask which categories or use cases
matter most before dumping everything. When the user names a specific SaaS product they want an
alternative to, lead with entries whose description explicitly says "alternative to [that
product]" — those are the most directly relevant, not just topically adjacent.
