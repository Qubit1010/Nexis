# Agent/OS Template

A starting skeleton for a file-based AI operating system: an identity (`CLAUDE.md`) + context + skills + always-on rules + a decision log, with a built-in privacy model. Copy it, fill the `{{PLACEHOLDERS}}`, and you have a working OS for a person, a client, a team member, or a domain.

Proven by **Nexis** (agency OS) and **Atlas** (personal OS). Full playbook: `references/sops/build-an-agent-os.md`.

## Quick start

1. **Copy** this folder to a new location outside any existing repo:
   `cp -r templates/agent-os-template <new-os-name>`
2. **Rename** the templates: drop `.template` (`CLAUDE.md.template` → `CLAUDE.md`, the `context/*.md.template` files, `CLAUDE.local.md.template`).
3. **Fill the placeholders** — `{{AGENT_NAME}}`, `{{PRINCIPAL}}`, `{{ROLE}}`, `{{ONE_LINE_MANDATE}}`, persona, domains — in `CLAUDE.md` and the `context/` files.
4. **Set the privacy line** — edit `.gitignore`, `.claude/rules/privacy.md`, and `scripts/pre-commit-privacy-guard.sh` so they list the same sensitive paths.
5. **Init git, install the guard:**
   `git init && cp scripts/pre-commit-privacy-guard.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`
6. **Wire tooling** — copy needed keys into `.env` (gitignored).
7. **Build/port skills** as the work calls for them (reuse before building).
8. **(Optional) dual vault + graph** — `references/sops/build-a-second-brain.md`.
9. **Seed** `decisions/log.md` with the founding decision.

## What's inside
```
CLAUDE.md.template            identity + persona + @context routing
CLAUDE.local.md.template      API-key handling (gitignored)
.gitignore                    privacy defaults
context/*.md.template         identity, domain, priorities, goals
.claude/rules/                never-break, communication-style, privacy,
                              skill-creation, research-backed-skills, gdrive-sync
.claude/skills/README.md      SKILL.md anatomy
decisions/log.md              append-only ledger
scripts/pre-commit-privacy-guard.sh   blocks committing private paths
```
