# Legal & Ethics — the guardrails

Distilled from `research-synthesis.md` Q7 (+ Q6 for real estate). **Never assert blanket legality — it is
jurisdiction-, data-type-, and ToS-specific.** This file is the "read before you scrape, escalate if a
client engagement touches gated/personal data" gate.

## What the case law actually says
- **hiQ v. LinkedIn (9th Cir.)** [Q7 118-123]: scraping *publicly accessible* data does **not** violate the
  CFAA. Foundational US precedent. **But hiQ lost on breach of contract (ToS)** — public ≠ permission.
- **Meta v. Bright Data (Jan 2024)** [Q8 126]: reinforced that scraping public (logged-out) data is
  defensible.
- **The real 2026 exposure is publisher contracts + copyright, not the CFAA** [Q8 126]: Reddit sued
  Anthropic (June 2025) and Perplexity (Oct 2025) over unlicensed scraping.
- **EU/GDPR is stricter for personal data**: EDPB Guidelines 03/2026 on web scraping for generative AI
  [Q7 109][114] + CNIL legitimate-interest focus sheet [Q7 113]. Requires a lawful basis (usually legitimate
  interest, balanced against data-subject rights), data minimization, transparency, and exclusion of
  special-category data. GDPR + CCPA both bite on personal data [Q7 115][116][117].

## Operating rules (keep the work defensible)
1. **Scrape only public data.** No logins, no paywalls, no auth-gated content [Q7 110][112].
2. **Read + respect `robots.txt` and ToS.** Document any exception with a reason/approval [Q7 108][112].
   `Crawl-delay` is binding [Q2 32].
3. **Minimize personal data.** Prefer business/firmographic facts (company, site, category, public phone)
   over individuals' personal data. If personal data is unavoidable, have a lawful basis [Q7 113][116].
4. **Never special-category data** (health, beliefs, etc.) without explicit grounds [Q7 109].
5. **Rate-limit so you never degrade the target.** Aggressive scraping can itself be a CFAA/DoS problem, not
   just impolite [Q2 30][32].
6. **Keep provenance** for anything downstream (source URL, timestamp, license) — required for ML corpora
   [Q5 84][85], good hygiene everywhere.

## Vertical notes
- **Real estate** [Q6 102][104][105]: listing *facts* are generally scrapeable, but photos/descriptions can
  be **copyrighted**, MLS/portal ToS often forbid scraping, and some data is licensed. Treat as contested —
  read `is-it-legal-to-scrape-real-estate` [Q6 102] before a paid engagement.
- **Social platforms**: most forbid scraping in ToS and block hard; Firecrawl intentionally blocks them
  [Q8 127]. For NexusPoint's social lead-gen, the house `lead-generator` (WebSearch resolution) and
  `facebook-lead-nav` (logged-in, human-paced) are the sanctioned paths, not this skill.
- **Training data** [Q5]: don't scrape gated or clearly-licensed content for model training; "Do Not Trust
  Licenses You See" — provenance-trace it [Q5 85].

## Where NexusPoint's real uses land
Public business directories for B2B outreach, public listing facts, public papers/repos for research — all
sit in the **defensible zone**, provided ToS/robots are honored, volume stays polite, and personal data is
minimized. When a job touches gated or clearly personal data, **stop and escalate to a real read of the
legal refs — do not guess or reassure.**
