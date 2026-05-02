# Decision Log

Append-only. When a meaningful decision is made, log it here.

Format: [YYYY-MM-DD] DECISION: ... | REASONING: ... | CONTEXT: ...

---

[2026-04-17] DECISION: Extended South Asia exclusion filter to also check LinkedIn URL subdomain (pk/in/bd/lk/np.linkedin.com) | REASONING: Profiles without a location field set were bypassing the filter despite being South Asian - URL subdomain is a reliable secondary signal | CONTEXT: lead-gen/linkedin_push.py

[2026-04-17] DECISION: Added Unicode normalization step to GPT connection note output before returning from transformer | REASONING: GPT-4o-mini occasionally returns smart quotes and em dashes that cause encoding errors in downstream CSV/terminal output | CONTEXT: lead-gen/transformers/linkedin_transformer.py

[2026-04-23] DECISION: Built Upwork Proposal Generator as a dashboard (Next.js) rather than a pure CLI skill | REASONING: Proposal workflows benefit from a visual UI for reviewing/editing before saving to Drive - same pattern as content engine dashboard | CONTEXT: projects/upwork-proposal-dashboard

[2026-04-23] DECISION: LinkedIn DM Responder skill uses two distinct modes (sequence mode vs. live reply mode) | REASONING: Post-connection nurture and live conversation handling require different frameworks - sequence = time-boxed cadence, live = Voss tactical empathy | CONTEXT: .claude/skills/linkedin-dm-responder

[2026-04-24] DECISION: Built Website Audit System skill with two modes (quick for outreach, deep for paid deliverable) and three outputs (markdown summary, Google Doc, hook email) | REASONING: Quick mode directly supports the Q2 bottleneck (cold outreach reply rate), deep mode doubles the same infrastructure as a $300-500 productized offer - single build, two revenue surfaces | CONTEXT: .claude/skills/website-audit-system

[2026-04-24] DECISION: Audit uses Google PageSpeed Insights public API rather than local Lighthouse or a headless browser | REASONING: Same Lighthouse output, no browser install, free without a key for low volume - keeps the skill portable across Aleem's machines with no setup beyond env vars | CONTEXT: .claude/skills/website-audit-system/scripts/pagespeed.py

[2026-04-24] DECISION: Audit skill defers CRM/Sheets logging to v2 | REASONING: Coupling audit output to the cold-outreach Sheets now would overbuild before we know how Aleem actually uses the output - revisit after 10-20 real runs | CONTEXT: .claude/skills/website-audit-system

[2026-05-01] DECISION: Built client-content-creator as a separate skill from content-engine | REASONING: Client content and personal brand content have different inputs (client brief vs. news/topics), tone, and destinations (client Drive folder vs. Aleem's Sheets/Docs) - collapsing them would create confusion and reduce reusability | CONTEXT: .claude/skills/client-content-creator

[2026-05-01] DECISION: Added eval framework with 3 test clients and grading rubrics before shipping client-content-creator | REASONING: Content quality is subjective and hard to catch in code review - a benchmark iteration lets us validate output and detect regressions when the skill is modified | CONTEXT: .claude/skills/client-content-creator/evals
