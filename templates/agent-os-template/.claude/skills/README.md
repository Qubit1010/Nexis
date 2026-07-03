# Skills

One folder per skill, each with a `SKILL.md`.

## SKILL.md anatomy
```markdown
---
name: skill-name
description: >
  What it does + when to use it. Pack the trigger phrases in here — this is what routes to the skill.
argument-hint: "[what to pass]"
---

# Skill Name
Body: how to do the job. Load context first, then the method. Keep load-bearing detail in references/.
```

Heavier skills add: `references/` (playbooks, research-synthesis.md), `_research/` (sources.json citation trail), `scripts/`, `evals/`.

Build a skill only when a workflow repeats (see `.claude/rules/skill-creation.md`). Research-backed advice skills follow `.claude/rules/research-backed-skills.md`.
