# Finding People & Companies (agency lead-gen)

Evidence + citations in `research-synthesis.md` Q3-Q4. This is the `--mode entity` playbook. Run it
for founders, decision-makers, and company profiling. Respect ToS and privacy; this is public-source
(OSINT) discovery, not scraping behind logins.

## Find a person (founder / decision-maker)
1. **LinkedIn X-ray** (Google indexes profiles LinkedIn hides) [37][41][42]:
   - `site:linkedin.com/in "<company>" (founder OR "co-founder" OR CEO)`
   - `site:linkedin.com/in "<role>" "<industry>" "<city>"`
   The orchestrator auto-adds the `site:linkedin.com/in` dork variant in entity mode + queries Exa
   `category="people"`.
2. **Cross-reference** the hit: company People page, About/Team, a talk/podcast, GitHub — confirm the
   person is current and the right one (beware same-name collisions) [38][40].

## Find the email
Format → permute → verify [43][44][45][46]:
1. **Discover the pattern** from one known address (press page, WHOIS, GitHub commit email, a
   signature): usually `first.last@`, `first@`, or `flast@` [44][47][48].
2. **Permute** first/last/domain into all plausible candidates (permutator tools, incl. open-source)
   [49][50][51][52][53][54].
3. **Verify** each via SMTP/MX before using — never send to unverified guesses (bounces wreck sender
   reputation) [43][45][49]. Paid enrichment (Hunter/Apollo) skips 1-3 but the free path works [46].

## Profile a company
- **Tech stack:** BuiltWith / Wappalyzer (site + extension) → CMS, framework, analytics, hosting,
  martech [67][68][69]. For an agency this shows what a prospect runs (WordPress vs Webflow vs custom)
  and the opening to help. Newer: WhatStack, WhatBuilt [70][71].
- **Hiring signals:** open roles = priorities + budget + pain (3 React hires = frontend investment)
  [56][59][60].
- **Funding / firmographics:** Crunchbase (founders, funding, headcount, investors); pair with
  LinkedIn for B2B lists [61][64][65].
- **Dorks:** `site:<co>.com (careers OR jobs)` · `"<co>" (raised OR "series a" OR funding)` ·
  `site:linkedin.com/company "<co>"` [39][66].

## Output for entity mode
Deep entity synthesis returns: who/what, identity & role (with [n]), company/context, canonical links
& contact, and a **confidence** line calling out any ambiguity between similarly-named entities.
Never assert an email or identity as certain without a verifying source [98].
