---
name: ai-use-case-generator
description: >
  Generates 3 tailored AI automation use cases with ROI framing for a specific client or prospect.
  Given a business description, URL, or company name + industry, outputs concrete use cases that span
  operational efficiency, revenue growth, and customer experience — each with specific ROI metrics
  and a one-liner hook ready to drop into cold outreach or a discovery call.

  Use this skill whenever the user asks to:
  - "generate AI use cases for [client/company]"
  - "what AI can I pitch to [prospect]"
  - "give me use cases for [industry]"
  - "create a use case deck / pitch / hook for [business]"
  - "what automation makes sense for [company description]"
  - "prep AI ideas before my call with [client]"
  - "what should I pitch to a [type of business]"

  Also trigger proactively when the user shares a business description and is preparing for a discovery call, writing outreach, or building a proposal.
argument-hint: "[business description | URL | company name + industry]"
---

# AI Use Case Generator

You generate 3 specific, ROI-framed AI automation use cases for a prospect or client — formatted for cold outreach and discovery calls.

## Input

The user will provide one of:
- **Free text description** — e.g. "physiotherapy clinic, 3 locations, manual scheduling and insurance claims"
- **URL** — e.g. `https://example.com` → crawl with WebFetch or Firecrawl MCP to understand the business first
- **Company name + industry** — e.g. "Medi-Care, healthcare admin" → generate from your knowledge of that industry

If a URL is provided, fetch it before generating. Extract: what the business does, who their customers are, what processes they likely run, and any pain points mentioned.

## Context to load

Before generating, read:
- `references/roi-framing.md` — ROI benchmarks and framing patterns by industry type

## Generation rules

### The 3-use-case framework

Always produce exactly 3 use cases, each covering a different dimension:

1. **Operational efficiency** — a repetitive internal process (scheduling, data entry, reporting, document handling) that AI can automate to save staff time
2. **Revenue / growth** — something that directly affects pipeline, conversion, or deal velocity (lead qualification, follow-up, personalization, pricing)
3. **Customer experience** — a touchpoint that improves how clients/customers interact with the business (onboarding, support, follow-up, communication)

This spread ensures the use cases feel varied and hit different decision-makers (ops, sales, CX).

### ROI framing

- Always include at least one specific metric per use case — a time range ("saves 8-12 hours/week"), a cost estimate ("reduces admin overhead by ~$1,500/month"), or a conversion lift ("improves lead response time from 4 hours to under 5 minutes")
- Use ranges, not made-up exact numbers. "6-10 hours/week" is more credible than "exactly 9 hours/week"
- Anchor metrics to what you know about the industry from `references/roi-framing.md` — use the right benchmarks for their sector
- If you don't have sector-specific data, use conservative estimates and label them as typical ("typically saves...")

### Hook lines

Each use case ends with a **Hook** — one sentence a salesperson could drop verbatim into a cold email or say at the top of a discovery call. It should:
- Name the specific pain (not vague AI buzzwords)
- Imply the ROI without overselling
- Sound natural, not scripted

Bad hook: "Our AI automation solutions can transform your business operations."
Good hook: "Most physio clinics we work with get back 10+ hours a week just by automating appointment reminders and no-show follow-ups — without changing their current booking system."

### Specificity over generality

The biggest failure mode is generic use cases that could apply to any business. Push for specificity:
- Name the actual process being automated (not "data entry" — "patient intake forms")
- Name the actual output (not "insights" — "a weekly report showing which SKUs are dead stock")
- Name the integration if obvious (not "connects to your systems" — "syncs with your Mindbody account")

## Output format

Use this exact template:

---

**AI Use Cases for [Business Name / Description]**

---

**Use Case 1: [Title]**
**Dimension:** Operational Efficiency
**Problem:** [1-2 sentences on the current pain — what they're doing manually, what it costs them]
**Solution:** [1-2 sentences on what gets automated and how it works at a high level]
**ROI:** [Specific metric — time saved, cost reduced, or revenue impact with a range]
**Hook:** "[One outreach-ready sentence in quotes]"

---

**Use Case 2: [Title]**
**Dimension:** Revenue / Growth
**Problem:** ...
**Solution:** ...
**ROI:** ...
**Hook:** "..."

---

**Use Case 3: [Title]**
**Dimension:** Customer Experience
**Problem:** ...
**Solution:** ...
**ROI:** ...
**Hook:** "..."

---

**Quick pitch summary** (3 bullets, one per use case — use this in a cold email P.S. or slide deck intro)
- [Use case 1 in one line]
- [Use case 2 in one line]
- [Use case 3 in one line]

---

## Edge cases

- **Vague input** (e.g., "a startup"): Ask one clarifying question — industry and team size — before generating. Don't generate generic use cases if you can avoid it.
- **Very niche industry**: Use your general knowledge. If genuinely unsure about ROI benchmarks, be transparent ("typically in this space, we see...") rather than inventing numbers.
- **User wants more than 3**: Generate 3 strong ones first. Offer to add more after.
- **User wants it for a specific use case type only** (e.g., "just give me ops use cases"): Generate 3 within that dimension instead.
