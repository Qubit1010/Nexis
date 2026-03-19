---
name: Deep Research
description: Context-aware research via OpenAI with deep and quick modes
---

# Deep Research Skill

## When to Trigger

Activate this skill when the user says:
- "research [topic]", "look into [topic]", "deep dive on [topic]"
- "what's the latest on [topic]", "find out about [topic]"
- Any query needing real-time external knowledge beyond what you already know
- Explicitly: "deep research..." or "quick search..."

## Mode Selection

| Mode | When to Use | Model | Cost |
|------|-------------|-------|------|
| **Deep** | Open-ended, comparative, strategic, or multi-faceted topics | OpenAI gpt-4o | $$$ |
| **Quick** | Single factual answer, moderate lookup | OpenAI gpt-4o-mini | $$ |
| **Lite** | Simple lookups, factual questions, cheap research | Claude Haiku (subagent) | $ |

**Auto-select logic:**
- Default to **quick** for simple factual questions
- Use **deep** for: market analysis, competitor research, strategic decisions, multi-source topics
- Use **lite** for: simple factual lookups, quick checks, when cost matters
- User can force mode: "deep research..." / "quick search..." / "lite research..." / "cheap research..."

## Context Injection

Before calling the script, read relevant context files and summarize to ~500 words max. Pass as `--context` arg.

| Query Type | Read These Files |
|---|---|
| Market/competitor analysis | context/work.md, context/current-priorities.md, context/goals.md |
| Tech/tool evaluation | context/work.md, context/me.md |
| Client/industry research | context/work.md, context/team.md |
| Academic/learning | context/me.md, context/goals.md |
| General/other | context/work.md, context/current-priorities.md |

## Invocation

### Deep & Quick modes (OpenAI API)
```bash
python .claude/skills/deep-research/research.py --query "..." --mode deep|quick --context "..." [--save]
```

**Arguments:**
- `--query` (required): The research question
- `--mode`: `deep` or `quick` (default: quick)
- `--context`: Business context summary string
- `--save`: Force save to file (deep mode auto-saves)

### Lite mode (Claude Haiku subagent)
Spawn the `research-lite` agent using the Agent tool:
```
Agent(subagent_type="research-lite", model="haiku", prompt="Research: [query]\n\nBusiness context: [context summary]")
```
No Python script, no API key needed. The agent uses WebSearch/WebFetch natively.

## Output Handling

- **Quick mode**: Display results inline. Don't save unless user asks.
- **Deep mode**: Display inline summary + full report auto-saves to `research/YYYY-MM-DD-slug.md`
- **Lite mode**: Display results inline. Save only if user asks.

## Cost Guard

Before running **deep** mode on broad/vague queries, confirm with the user:
> "This is a broad topic — deep research will use gpt-4o with multiple web searches. Want me to proceed, or should I narrow the scope first?"

Skip confirmation for specific, well-scoped queries.
