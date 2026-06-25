# Nexis

Executive assistant and second brain for [NexusPoint](https://nexus-point.co), powered by Claude Code. Manages agency operations, client acquisition, content, outreach, and automation workflows.

## What This Is

A structured workspace that turns Claude Code into a personalized operating system for running a digital agency. Persistent context files, a custom skill library, and an append-only decision log keep the assistant sharp across every session.

## Structure

```
context/          # Who I am, what I do, current priorities, goals, team
projects/         # Active workstreams (reel engine, upwork scout, etc.)
templates/        # Reusable session and document templates
scripts/          # Utility scripts
brand-assets/     # Logos, fonts, brand guidelines
research/         # Research outputs
archives/         # Retired material
.claude/          # Claude Code config, rules, and skills
```

> `decisions/`, `docs/`, `references/`, and `client-projects/` are gitignored (private/local only).

## Skill Library

45+ custom skills covering the full agency workflow:

### Client Acquisition & Sales
- **Sales Playbook** — Opener archetypes, Voss calibrated questions, Hormozi value equation, full 30-min discovery call script, 10 objection responses. All claims sourced from 77-source NotebookLM synthesis.
- **Leads to CRM** — Scrape Instagram/LinkedIn/Facebook → identity-deduped push into per-channel CRM with Claude Haiku Touch 1 message
- **Facebook Lead Navigation** — Resolves Facebook group post authors to profile URLs via Playwright CDP automation
- **Website Audit System** — Firecrawl + AI analysis → Google Doc report + cold outreach hook email (quick and deep modes)
- **Marketing Advisor** — Research-backed (234 cited 2026 sources) marketing strategy: cold email, LinkedIn, content, ads, offer positioning
- **Sales Playbook Dashboard** — Local web app for drafting LinkedIn/Instagram DMs from the playbook

### Client Operations
- **Proposal Generator** — Hormozi $100M Offers framework → formatted Google Doc proposals
- **Client Onboarding Workflow** — 3-phase: Drive folder + onboarding doc + checklist sheet + Gmail draft (Phase 1); local confidential project workspace (Phase 2); task progress tracking (Phase 3)
- **Team Task Delegation** — Auto-match tasks to team members, generate ready-to-send messages

### Content & Brand
- **Content Engine** — Full Instagram/LinkedIn/blog creation: idea scoring, OpenAI research, writing, flywheel repurposing, Sheets logging
- **Reel Creator** — Infographic post → 40-50s vertical motion-graphics reel (Remotion + Whisper + ElevenLabs)
- **Daily Brief** — AI/tech news intelligence brief (NewsAPI, HackerNews, RSS)

### Research & Knowledge
- **Deep Research** — Context-aware research via OpenAI (deep/quick/lite modes)
- **Claude Advisor** — Research-backed guide to everything Claude: surfaces, models, Claude Code, Cowork, API, plans
- **NotebookLM** — Full programmatic access: create notebooks, add sources, generate podcasts/quizzes/reports
- **Assignment Research** — Academic research → structured outlines saved to Google Docs

### Installed Collections
- **Marketing Skills** (`.claude/skills/marketing-skills/`) — Router for 45 skills: SEO, paid ads, cold email, CRO, pricing, launches, retention, and more
- **Awesome Claude Skills** — 26 productivity/dev skills (lead research, competitive ads, webapp testing, mcp-builder, etc.)
- **Scientific Agent Skills** — 147 ML/data science/bioinformatics/chemistry/quantum skills

### Engineering & Design
- `senior-architect`, `senior-backend`, `senior-frontend` — system design, API/DB, modern frontend
- `code-reviewer` — multi-language PR review and security scan
- `frontend-design`, `ui-ux-pro-max`, `canvas-design` — production UI and visual art
- `reel-creator` + `remotion-best-practices` — motion graphics video pipeline
- `ponytail` — lazy senior dev enforcer: YAGNI ladder, shortest working diff
- `skill-creator` — standard skill authoring and eval workflow

## Setup

1. Clone this repo
2. Install [Claude Code](https://claude.ai/code)
3. Create `.env` with required API keys (see `.env.example`)
4. Create `CLAUDE.local.md` for local overrides (API key handling, personal preferences)
5. Run `claude` in the project directory

## Requirements

- Claude Code CLI
- Python 3.10+ (research, reel, and audit skills)
- Node.js 18+ (reel engine, skill scripts)
- Google Workspace CLI (`gws`) authenticated to your account
