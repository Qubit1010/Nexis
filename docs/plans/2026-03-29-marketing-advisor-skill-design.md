# Marketing Advisor Skill — Design Document

**Date:** 2026-03-29
**Status:** Approved, ready for implementation

## Purpose

An always-available marketing brain for NexusPoint that gives actionable guidance on cold email, LinkedIn outreach, content creation, Instagram, ads, offer positioning, strategy, and automation workflow design. Grounded in Hormozi's $100M Leads/Offers and Voss's Never Split the Difference.

## Key Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Interactivity | Hybrid (auto-detect advisor vs planner mode) | Quick questions get direct answers; action requests get structured plans |
| Automation output | Blueprint only (no code generation) | Architecture plans, not working scripts. Build separately. |
| Google Docs | User-gated (offer after substantial outputs) | Avoids overhead for quick answers, available when needed |
| Web research | Gated (offer when ask would benefit) | Frameworks handle 80% of asks; opt-in for live data |

## Skill Structure

```
.claude/skills/marketing-advisor/
├── SKILL.md
├── references/
│   ├── leads-framework.md        (337 lines)
│   ├── offers-framework.md       (167 lines)
│   ├── negotiation-framework.md  (148 lines)
│   ├── nexuspoint-positioning.md (97 lines)
│   ├── cold-email-playbook.md    (246 lines)
│   └── content-strategy-playbook.md (161 lines)
└── scripts/
    └── save_marketing_plan.py    (Google Docs output, user-gated)
```

## Mode Detection

| Mode | Detection Keywords | References Loaded |
|------|-------------------|-------------------|
| strategy | "marketing strategy", "what channels", "how to market", "growth plan" | leads + positioning |
| cold-email | "cold email", "outreach email", "email sequence" | cold-email-playbook + negotiation + leads |
| linkedin | "LinkedIn", "DM script", "connection request" | cold-email-playbook + content-strategy + negotiation |
| content | "content plan", "what should I post", "social media", "Instagram" | content-strategy + positioning |
| offer | "position this", "package", "pricing", "value stack" | offers + positioning |
| ads | "ads", "paid advertising", "ad budget" | leads + offers |
| automation | "automate", "marketing automation", "workflow" | leads + cold-email-playbook |
| advise (default) | anything marketing that doesn't match above | dynamic 1-2 most relevant |

**Loading rules:** Always load work.md + current-priorities.md. Max 3 reference files. Never all 6.

## Workflow

1. Parse & classify (detect mode, extract audience/goal/constraints)
2. Load context + mode-specific references
3. Decide response type: quick advisory (<300 words) vs structured plan
4. Apply frameworks (Core Four, Value Equation, tactical empathy, More-Better-New)
5. Deliver + offer follow-ups (Google Docs save, web research, next actions)

## Writing Rules

- Lead with dream outcome, not deliverable
- Position NexusPoint as AI-first
- Every cold email uses at least one label
- Low-friction CTAs only
- Numbers always specific (Rule of 100)
- No emojis, no em dashes in external content
- Value Equation as lens for all advice
- More-Better-New for channel decisions
- Never fabricate scarcity

## Edge Cases

- Vague ask → ask ONE clarifying question
- Multi-mode ask → primary first, offer second
- Unvalidated channel → flag, give minimum viable experiment
- Contradicts framework → push back with reasoning, respect final call
- Proposal territory → redirect to /proposal-generator
- Google Docs fails → output in conversation
