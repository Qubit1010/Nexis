# Nexis

Executive assistant and second brain powered by Claude Code. Built for managing agency operations, client acquisition, research, and automation workflows.

## What This Is

A structured workspace that turns Claude Code into a personalized operating system for running a digital agency. It combines persistent context, custom skills, and decision logging to maintain continuity across conversations.

## Structure

```
context/          # Who I am, what I do, current priorities, goals
decisions/        # Append-only decision log
projects/         # Active workstreams
templates/        # Reusable templates
references/       # SOPs and style guides
scripts/          # Utility scripts
brand-assets/     # Logos, fonts, brand guidelines
research/         # Research outputs
archives/         # Retired material
.claude/          # Claude Code config, rules, and skills
```

## Skills

Custom Claude Code skills that extend functionality:

- **Deep Research** -- Context-aware research via OpenAI (deep/quick modes)
- **Delegate** -- Auto-match tasks to team members with ready-to-send messages
- **Frontend Design** -- Production-grade UI generation
- **Skill Builder** -- Create and optimize Claude Code skills
- **Skill Creator** -- Build, eval, and benchmark skills

## Setup

1. Clone this repo
2. Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
3. Create a `.env` file with required API keys (see `.env.example`)
4. Create `CLAUDE.local.md` for local overrides
5. Run `claude` in the project directory

## Requirements

- Claude Code CLI
- Python 3.10+ (for research skill)
- Node.js (for skill-creator scripts)
