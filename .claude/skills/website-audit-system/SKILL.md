---
name: website-audit-system
description: >
  Crawls a prospect's website via Firecrawl, runs AI analysis across UX/messaging, SEO basics,
  performance (Google PageSpeed Insights), and conversion gaps, and produces a formatted audit
  report saved to Google Drive plus a ready-to-send cold outreach email. Two modes: quick (homepage
  only, 3-5 findings, hook email — optimized for cold outreach) and deep (multi-page crawl, scored
  breakdown per dimension, professional report — sold as a paid deliverable).

  Use this skill whenever Aleem says:
  - "audit this website", "run a website audit on [X]", "audit [company]'s site"
  - "check this site for [prospect]", "quick audit of [URL]", "deep audit of [URL]"
  - "website audit for outreach", "audit a prospect site"
  - Pastes a URL along with "outreach", "prospect", "cold email", or "lead"

  Also trigger proactively when Aleem shares a prospect URL and is clearly preparing cold outreach
  or evaluating a site's fit for NexusPoint's services. Default to quick mode when only a URL is
  given — that matches the cold outreach priority.
argument-hint: "[URL] [quick|deep] [optional: company name, industry, notes]"
---

# Website Audit System

You audit a prospect's website, producing a structured report saved to Google Drive and a ready-to-send cold outreach email. This is one of NexusPoint's highest-leverage outreach tools — a specific, well-researched audit earns replies that a generic pitch cannot.

## Context to load first

Before running, read these two reference files in full. They are the source of truth for findings and email voice:

- `references/audit-framework.md` — what to check in each of the 4 dimensions, severity rubric, writing rules
- `references/outreach-templates.md` — hook email archetypes + Voss-flavored voice

## Mode detection

Parse Aleem's input:

| Signal | Mode |
|---|---|
| Contains "quick", "cold outreach", "opener", "just a URL" | **quick** |
| Contains "deep", "full audit", "paid", "deliverable", "comprehensive" | **deep** |
| Only a URL, no mode hint | **quick** (default — cold outreach is the primary use case) |

If genuinely ambiguous, ask one clarifying question: "Quick (cold outreach opener) or deep (paid deliverable)?"

## Required inputs

- **URL** (required): prospect's website
- **Company name** (optional but strongly preferred): for personalization
- **Industry / context** (optional): sharpens findings

If URL is missing, ask for it. Don't proceed without it.

## Environment check

Before running, confirm these env vars are set:
- `ANTHROPIC_API_KEY` — required for `analyze_audit.py` and `generate_hook_email.py`
- `FIRECRAWL_API_KEY` — required for `crawl_site.py`
- `PAGESPEED_API_KEY` — optional (script works without it, but may be rate-limited)

If `FIRECRAWL_API_KEY` is unset, fall back: invoke the Firecrawl MCP tool directly (`mcp__firecrawl__scrape` or the equivalent), save the response to a temp JSON file shaped like `{"status": "ok", "mode": "quick", "url": "...", "pages": [{"url": "...", "markdown": "...", "html_snippet": "...", "metadata": {...}}]}`, and pass that file to `analyze_audit.py --crawl-file`.

If no Anthropic key is set, stop and tell Aleem — this is the one hard requirement.

## Workflow — Quick mode

Goal: cold outreach opener. Homepage only. Output = markdown summary + Google Doc + ready-to-send email.

### 1. Crawl the homepage

```bash
python .claude/skills/website-audit-system/scripts/crawl_site.py \
  --url "<URL>" --mode quick > /tmp/audit_crawl.json
```

Check `status` field. If error, report to Aleem and stop.

### 2. Run PageSpeed Insights

```bash
python .claude/skills/website-audit-system/scripts/pagespeed.py \
  --url "<URL>" > /tmp/audit_pagespeed.json
```

If PageSpeed returns `status: error`, continue anyway — the audit will flag performance as "not measured".

### 3. Analyze

```bash
python .claude/skills/website-audit-system/scripts/analyze_audit.py \
  --mode quick \
  --crawl-file /tmp/audit_crawl.json \
  --pagespeed-file /tmp/audit_pagespeed.json \
  --company "<Company>" \
  --industry "<Industry if known>" \
  > /tmp/audit_result.json
```

Output JSON has `summary`, `findings` (3-5), `company`, `url`, `mode`.

### 4. Create Google Doc

```bash
cat /tmp/audit_result.json | python .claude/skills/website-audit-system/scripts/create_audit_doc.py \
  > /tmp/audit_doc.json
```

Extract `doc_url` from the response.

### 5. Generate hook email

```bash
cat /tmp/audit_result.json | python .claude/skills/website-audit-system/scripts/generate_hook_email.py \
  --doc-url "<doc_url from step 4>" > /tmp/audit_email.json
```

### 6. Respond to Aleem

Report in this exact format:

```
**Audit: [Company] ([URL])**

**Summary:** [2-3 sentence summary from audit]

**Top findings:**
1. [Severity] [title] — [one-line business impact]
2. [Severity] [title] — [one-line business impact]
...

**Google Doc:** [doc_url]

**Ready-to-send email:**
Subject: [subject]

[full body]
```

Don't editorialize. Just show what was produced. Aleem will decide what to tweak.

## Workflow — Deep mode

Goal: paid deliverable. Multi-page crawl. Output = executive summary + Google Doc (no hook email).

### 1. Multi-page crawl

```bash
python .claude/skills/website-audit-system/scripts/crawl_site.py \
  --url "<URL>" --mode deep --max-pages 8 > /tmp/audit_crawl.json
```

### 2. PageSpeed (homepage only — deep mode still scores one page for the perf section)

```bash
python .claude/skills/website-audit-system/scripts/pagespeed.py \
  --url "<URL>" > /tmp/audit_pagespeed.json
```

### 3. Analyze with deep mode

```bash
python .claude/skills/website-audit-system/scripts/analyze_audit.py \
  --mode deep \
  --crawl-file /tmp/audit_crawl.json \
  --pagespeed-file /tmp/audit_pagespeed.json \
  --company "<Company>" \
  > /tmp/audit_result.json
```

Output includes `scores` (1-10 per dimension) and 8-14 findings.

### 4. Create Google Doc

Same command as quick mode — `create_audit_doc.py` switches templates based on `mode` in the audit JSON.

### 5. Respond to Aleem

```
**Deep audit: [Company] ([URL])**

**Executive summary:** [summary]

**Scores:**
- UX & Messaging: X/10
- SEO Basics: X/10
- Performance: X/10
- Conversion: X/10

**Critical findings (fix within 1 week):** [list]
**High findings (fix within 2-4 weeks):** [list]

**Google Doc:** [doc_url]
```

No hook email in deep mode — paid-deliverable clients already bought.

## Edge cases

- **Site behind auth / login wall**: Firecrawl will return thin content. Report to Aleem honestly: "Only the login page was accessible. Can't produce a meaningful audit without authenticated pages."
- **Heavy SPA with no markdown**: Check crawl_site.py output — if markdown is under a few hundred chars, the site is likely rendering client-side. Flag it and offer to retry with a longer `waitFor` parameter.
- **PageSpeed rate-limited (429)**: The audit runs fine without performance scores. Framework explicitly says: omit Performance findings rather than fabricate them.
- **Firecrawl out of credits (402)**: Report the error. Offer to wait or use the Firecrawl MCP fallback described in the environment check section.
- **URL typo / unreachable site**: crawl_site.py will return `status: error`. Ask Aleem to confirm the URL.
- **Aleem asks for multiple audits at once**: Run them sequentially. Running in parallel risks hitting rate limits on PageSpeed and Firecrawl simultaneously.

## Quality bar

After every run, read the findings before handing off. If any of these are true, regenerate or adjust:

- Any finding is generic ("the homepage could be more engaging" — useless)
- Any finding doesn't quote real evidence from the site
- Any finding uses "LCP", "CLS", "TBT", or similar jargon without translating it
- The summary reads like marketing filler instead of honest observation
- The hook email is over 100 words or uses "I hope this finds you well"
- Any em dashes or emojis snuck in (will corrupt the Google Doc — see Memory)

If the audit has fewer than 3 findings in quick mode or fewer than 8 in deep mode, that usually means the crawl came back thin. Check `page_count` and `markdown` length in the crawl JSON before blaming the model.

## After the audit

For quick mode: Aleem copies the email and sends. If he wants to send via `gws gmail +send`, he'll ask — don't do it automatically. This is outreach, not a broadcast; he reviews before sending.

For deep mode: The Doc is the deliverable. If Aleem says it's for a paying client, offer to draft a short delivery email referencing the doc.

In both modes, the Doc URL should be kept somewhere retrievable — for now, it's in `NexusPoint Website Audits` Drive folder. Future work could log audits into the Sheets CRM alongside cold-outreach leads.
