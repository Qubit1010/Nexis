# Martech Stack & Attribution 2026

**Source basis:** Distilled from `references/research-synthesis.md` Q8 (234-source NotebookLM synthesis). Citations map to `_research/sources.json`. Use when designing marketing automation, choosing tools, or answering "how do I measure this." Keep stacks lean and composable - built around workflow gaps, not bloated suites (there are 15,000+ martech tools; you need ~8) [s160].

---

## Recommended lean stack for a small B2B / AI-automation agency

| Layer | Tools | Notes |
|-------|-------|-------|
| **AI delivery & automation** | **Make** ($9/mo, visual no-code) or **n8n** (open-source, self-host to avoid per-op pricing at scale) | Connect to OpenAI (GPT-4o) for generation, **Anthropic Claude** for doc analysis; vector DB Pinecone/Supabase for RAG [s198] |
| **CRM & marketing automation** | **HubSpot free tier** (good to 50-100 clients); **ActiveCampaign** for email-driven multichannel journeys | [s52] |
| **Data enrichment & outbound** | **Clay** - pulls dozens of data providers, enriches, AI-writes personalized outbound, bypasses CRM decay | Essential for ICP list-building [s198] |
| **ABM & attribution** | **6sense / Demandbase** (enterprise); **Factors.ai** ($20-60k/yr) for SMB - multi-touch attribution + account intelligence + reverse-IP | [s160] |
| **All-in-one (lean)** | **Ciela AI** ($99/mo) - LinkedIn automation + email + CRM + e-sign + resellable AI agent templates | [s198] |
| **Ad automation** | **Ryze AI** - autonomous bid/budget/creative optimization across Google + Meta | [s59] |

A lean agency stack often already runs n8n/Make + Python + Gmail + Google Sheets + a lead-gen pipeline. This stack extends, not replaces, that. Recommend tools by name with the workflow gap they fill - don't over-engineer; start with what closes the current gap.

---

## Attribution in 2026: single-model is dead

Cookie deprecation + privacy killed single-model attribution. The norm is **method stacking (dual-model)** [s162, s48]:
- **MTA (Multi-Touch)** for tactical day-to-day optimization (47% of B2B teams use it).
- **MMM (Marketing Mix Modeling)** for strategic budget allocation (26%, tripled since 2023).
- **AI reconciliation** bridges them: hybrid models give a **+27-point lift in predictive accuracy** vs single-model.
- **Account-level measurement:** aggregate every touch from every contact at a company into one account record (deals need 6-10 stakeholders).

---

## The dark funnel (you can't track ~38% of pipeline)

Activity in private Slacks, dark-social DMs, podcasts, and word-of-mouth = a **median 38% of B2B pipeline** (51% for PLG) [s162]. You can't see it in GA4. Solve with **Self-Reported Attribution**:
- Embed "How did you hear about us?" (open text) on high-value gates and post-signature surveys.
- Blend the data: weight **70% digital tracking / 30% survey** to credit dark-funnel sources fairly [s162].

**Last-click is broken:** still used by 67% of teams, but it awards 100% credit to the final touch, over-crediting bottom-funnel (paid search/retargeting) and ignoring the brand/content that created demand. GA4 misattributes **67-75%** of long-cycle B2B conversions to "Direct/None" [s162].

---

## Metrics that actually matter (and what to ignore)

**Track (ROI-based)** [s206]:
- Pipeline: Lead-to-Opportunity (SQL) rate, pipeline per channel, win rate, avg deal size by source.
- Economics: CAC, CAC payback period, LTV:CAC.
- Email: **CTOR + reply rate** (NOT opens - MPP inflates them to 42-44%).
- Ads/social: social-sourced opportunities, cost per qualified lead, **POAS** (not just ROAS).

**Ignore (vanity):** raw website traffic, email opens, ad impressions, follower counts. They look good and predict nothing [s206].

---

## Quick application
- "What tools do I need?" -> name the workflow gap, then the lean tool that fills it (above). Don't recommend a suite.
- "How do I know what's working?" -> dual-model + self-reported attribution; track SQL rate, CAC payback, CTOR/reply, POAS.
- "Why is everything showing as Direct?" -> that's GA4 + the dark funnel; add a "how did you hear about us?" survey.
- Designing an automation -> output a written blueprint (trigger, steps, tools by name, data flow, exit) per the SKILL.md Automation Blueprint format.
