# Agentic Coding Playbook

**Source basis:** `research-synthesis.md` Q6 (sources `[s131]`–`[s154]`). Load when the question is "how do I get the best code out of AI tools / Claude Code" or when a blueprint milestone maps to an agentic workflow. For Claude *product* questions, hand off to `claude-advisor`.

## First principle
**Structure beats phrasing.** In 2026, how you curate context matters more than prompt wording [s134]. The discipline is **context engineering** — Anthropic's Applied AI team's term (Sept 2025): curating the optimal set of tokens during inference [s131][s130]. Agents can't be re-prompted mid-refactor; they need a persistent, curated environment [s131].

## The workflow: Explore → Plan → Code → Commit
1. **Explore** — agent reads the relevant code first; use subagents to search broadly without polluting main context [s145].
2. **Plan** — plan mode before coding; jumping to code solves the wrong problem [s140].
3. **Code** — implement against the plan.
4. **Commit** — with review.
Anthropic's explicit guidance: "Explore first, then plan, then code" [s140][s151].

## Context engineering mechanics
- **CLAUDE.md** = a README for the agent: structure, commands, conventions, guardrails. Well-configured → context loads in seconds, conventions followed from line one [s143][s152]. Keep it curated — bloat is the #1 token waste; good context can cut 200K → 60–80K tokens (60–70%) [s136].
- **Skills / subagents / hooks / MCP** — the `.claude/` dir is a hierarchical, version-controlled config system [s147]. Specialized subagents per task (frontend, DB, QA, review), some in parallel [s143][s144].
- **Second opinion beats self-grading** — a fresh subagent tries to refute the result; the agent that did the work shouldn't grade it [s140][s144].

## Spec-Driven Development (SDD)
Write a structured spec first (goal, requirements, constraints, **testable acceptance criteria**) as a first-class artifact before code. Agent implements against it; you review against acceptance criteria, "not vibes" [s138][s139]. Enables parallel agent implementation [s138]. (In Nexis: the gstack `/spec` skill does exactly this.)

## Applying it in a blueprint
When milestones involve building with Claude Code, frame them as: spec → plan mode → implement → fresh-agent review. Point to the repo's own tooling (CLAUDE.md, rules, subagents, `/spec`, `/review`).

## Checklist
- [ ] Is there a CLAUDE.md / spec before coding starts?
- [ ] Explore→plan→code→commit, not straight to code.
- [ ] Context curated, not dumped.
- [ ] A separate reviewer pass (agent or human).

**Anchor sources:** Anthropic "Best practices for Claude Code" [s151], Claude Code overview/docs [s152], "Advanced Patterns: Subagents, MCP, Scaling" [s153].
