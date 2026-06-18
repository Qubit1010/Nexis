# NexusPoint Claude Skills

Free, research-backed [Claude Code](https://docs.claude.com/en/docs/claude-code) skills from [NexusPoint](https://nexus-point.co/). Two installable skills, each grounded in a NotebookLM synthesis of cited 2026 sources, no API keys or accounts required.

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

## Install

In Claude Code, add the marketplace once, then install either or both:

```
/plugin marketplace add Qubit1010/nexuspoint-claude-skills
/plugin install claude-advisor
/plugin install marketing-advisor
```

The skills activate automatically when you ask a matching question.

## Use it on Claude.ai (no Claude Code needed)

Each skill folder also works as an uploadable Skill on Claude.ai (Settings -> Capabilities -> Skills). Zip the inner skill folder (e.g. `plugins/claude-advisor/skills/claude-advisor/`) and upload it.

## What's inside

```
plugins/
├── claude-advisor/skills/claude-advisor/      # SKILL.md + 11 references + 237-source index + local export script
└── marketing-advisor/skills/marketing-advisor/ # SKILL.md + 11 references + 234-source index + local export script
```

No API keys, no Google account, no external auth required.

---

Built by [NexusPoint](https://nexus-point.co/) - AI systems, automation, and web. If this is useful and you want this kind of thing built for your business, that's what we do.

## License

[MIT](./LICENSE) - use it, fork it, ship it.
