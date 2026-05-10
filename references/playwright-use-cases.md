# Playwright CLI — Use Case Ideas

Setup lives at `projects/browser-automation/`. All commands run from that directory.

---

## Screenshots & Visuals

- Full-page screenshots of any URL: `npm run screenshot https://example.com`
- Before/after screenshots to catch visual regressions on client sites after deploys
- Export any webpage as a PDF (useful for generating client-facing reports)
- Capture screenshots across multiple breakpoints (mobile, tablet, desktop) in one run

---

## Scraping & Data

- Scrape job boards (Upwork, LinkedIn) into Google Sheets
- Extract lead data from business directories (Clutch, G2, Trustpilot)
- Pull pricing, copy, or service listings from competitor sites
- Monitor a page for content changes (new listings, price drops, status updates)
- Scrape portfolio sites for prospect research before discovery calls

---

## Testing Your Own Apps

- E2E test any Next.js dashboard at `localhost:3000` (already wired up)
- Test form submissions, login flows, auth redirects
- Visual regression tests — screenshot on every deploy and diff against baseline
- Verify API-driven UI renders correctly after data changes

---

## Browser Automation

- Auto-fill and submit forms (demonstrated with portfolio contact page)
- Log into sites and perform multi-step actions (click, navigate, download)
- Batch-download files or reports from web portals
- Automate repetitive data-entry tasks across web UIs
- Save and restore login sessions (storageState) to avoid re-auth on every run

---

## Client Work

- Audit client websites for broken links, missing meta tags, slow elements
- Generate PDF reports from HTML/CSS templates as client deliverables
- Automate QA checklists on delivered projects before handoff
- Check cross-browser consistency (Chromium, Firefox, WebKit) on a client's live site

---

## Code Generation

- `npm run codegen https://anysite.com` — opens a browser recorder
- Every click and input you make gets written as Playwright test code automatically
- Best way to build scrapers or automation scripts for unfamiliar sites — record first, refine after

---

## Quick Reference — Scripts Available

| Command | What it does |
|---|---|
| `npm test` | Run all E2E tests headlessly |
| `npm run test:watch` | Slow-mo headed run for visual review |
| `npm run test:ui` | Playwright interactive dashboard |
| `npm run screenshot <url>` | Full-page PNG → `output/screenshots/` |
| `npm run scrape <url> <selector>` | Extract text from any CSS selector |
| `npm run codegen <url>` | Record browser actions → auto-generate test code |
