# NexusPoint Claude Skills

Free [Claude Code](https://docs.claude.com/en/docs/claude-code) skills from [NexusPoint](https://nexus-point.co/). Two research-backed advisor skills grounded in NotebookLM syntheses of cited 2026 sources (no API keys or accounts needed), plus a hands-on outreach automation (`leads-to-crm`) you point at your own Google Sheets.

## claude-advisor

The go-to guide to **everything Claude**, as an installable skill. Ask it anything about Claude and get a specific, sourced answer instead of a vague one:

- **"Which Claude should I use for this?"** chat vs Claude Code vs Cowork, with a decision table.
- **"Opus vs Sonnet vs Haiku for X?"** model selection grounded in 2026 specs and pricing.
- **"Can I build this workflow in Claude Code?"** feasibility first, then the build shape.
- **"Best plugins / MCP servers / tools?"** the ecosystem map.
- **"Which plan should I buy?"** Free / Pro / Max / Team / Enterprise, and how Claude compares to ChatGPT and Gemini.

Grounded in a **NotebookLM synthesis of 237 cited 2026 sources**, with honesty flags on anything version- or price-sensitive.

## marketing-advisor

A **research-backed marketing advisor** for agencies and founders. Strategy and benchmarks, not framework dumps:

- **"How do I get more clients?"** channel selection paced to 2026 reply/connection-rate benchmarks.
- **"Who should I target?"** ICP definition, scoring, and intent signals.
- **"What should I post?"** LinkedIn / Instagram-Reels strategy and content calendars.
- **"How should I price/package this?"** offer positioning on the Value Equation with 2026 agency pricing data.
- **"Is X still working?"** a sourced kill list of stale tactics, plus a live benchmark scoreboard.

Grounded in a **NotebookLM synthesis of 234 cited 2026 sources**. Strategy only - it frames the plan; the actual outreach copy is a separate pass.

## leads-to-crm

A **hands-on outreach automation** for agencies and teams. It moves manually-scraped leads from your per-channel source Google Sheets into the matching outreach CRM, writing a personalized **Touch 1 message** for each genuinely new lead:

- **Identity-based dedup** on the @handle / LinkedIn slug, so it only adds new rows and never duplicates ones already sent.
- **Instagram + LinkedIn** today, built to extend to more channels with one config block.
- **Touch 1 messages** via OpenAI (`gpt-5.4-mini`) with a Claude Haiku fallback, or run with blank messages to fill later.

Unlike the advisor skills, this one **does things in your accounts**, so it needs a little setup: point it at your own sheets with environment variables (`LEADS_IG_SOURCE_SHEET_ID`, `LEADS_IG_CRM_SHEET_ID`, `LEADS_LI_SOURCE_SHEET_ID`, `LEADS_LI_CRM_SHEET_ID`), the [`gws` Google Workspace CLI](https://nexus-point.co/) authenticated to your Google account, and optionally `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`. Full details in its `SKILL.md`.

## Install

In Claude Code, add the marketplace once, then install either or both:

```
/plugin marketplace add Qubit1010/nexuspoint-claude-skills
/plugin install claude-advisor
/plugin install marketing-advisor
/plugin install leads-to-crm
```

The skills activate automatically when you ask a matching question.

## Use it on Claude.ai (no Claude Code needed)

Each skill folder also works as an uploadable Skill on Claude.ai (Settings -> Capabilities -> Skills). Zip the inner skill folder (e.g. `plugins/claude-advisor/skills/claude-advisor/`) and upload it.

## What's inside

```
plugins/
├── claude-advisor/skills/claude-advisor/       # SKILL.md + 11 references + 237-source index + local export script
├── marketing-advisor/skills/marketing-advisor/ # SKILL.md + 11 references + 234-source index + local export script
└── leads-to-crm/skills/leads-to-crm/           # SKILL.md + message archetypes + channel-config pipeline scripts
```

The two advisor skills need no API keys, Google account, or external auth. `leads-to-crm` is the exception: it acts in your accounts, so it needs the `gws` CLI and your own sheet IDs (see its setup above).

---

Built by [NexusPoint](https://nexus-point.co/) - AI systems, automation, and web. If this is useful and you want this kind of thing built for your business, that's what we do.

## License

[MIT](./LICENSE) - use it, fork it, ship it.
