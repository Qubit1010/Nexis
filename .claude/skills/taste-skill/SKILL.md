---
name: taste-skill
description: Router for 13 design-taste and UI-generation skills from Leonxlnx/taste-skill (installed as one bundle). Covers anti-generic frontend design, brand-kit generation, UI aesthetic presets (brutalist/minimalist), image-to-code, image-only design direction (web + mobile), redesigns of existing projects, Stitch design systems, and full-output enforcement. Use this skill whenever the user wants a website/app/UI that doesn't look like generic AI slop, wants a specific visual aesthetic (brutalist, minimalist, luxury brand kit), wants design reference images before code, or wants an existing project redesigned. Trigger on: "make this look premium", "anti-slop design", "brutalist UI", "minimalist UI", "brand kit", "redesign this site", "generate design images first", "Stitch design system", "don't truncate the output".
---

# Taste Skill (Router)

This folder bundles 13 skills from the `Leonxlnx/taste-skill` GitHub repo. They are **not auto-merged** — each is a separate skill folder with its own `SKILL.md`. This file exists to tell you (and future-you) which one to invoke via the `Skill` tool.

**How to use:** read the table, pick the matching sub-skill, then invoke it with `Skill({ skill: "taste-skill/<folder-name>" })` (or however this harness addresses nested skills — if nested invocation isn't supported, open `taste-skill/<folder-name>/SKILL.md` directly and follow it).

## Decision Table

| If the task is... | Use | Notes |
|---|---|---|
| General landing page / portfolio / redesign that must not look templated | **design-taste-frontend** | Default anti-slop frontend skill. Audit-first on redesigns, strict pre-flight check. |
| Same as above, but a project depends on exact old behavior | **design-taste-frontend-v1** | Only for backward compatibility. `design-taste-frontend` is the current default. |
| Need a logo system, brand-guidelines board, identity deck | **brandkit** | Image generation for brand systems (minimalist, luxury, dark-tech, gaming, dev-tool, etc). |
| Want a raw, mechanical, Swiss-print x military-terminal aesthetic | **industrial-brutalist-ui** | Dashboards, portfolios, editorial sites that should feel like declassified blueprints. |
| Want a clean, warm-monochrome, no-gradient editorial UI | **minimalist-ui** | Flat bento grids, muted pastels, typographic contrast. |
| Want heavy GSAP scroll motion, AIDA structure, Awwwards-style page | **gpt-taste** | Elite UX/UI + advanced GSAP motion engineering. |
| Want the "expensive agency" look defined precisely (fonts/spacing/shadows/motion) | **high-end-visual-design** | Blocks generic AI-design defaults, Awwwards-tier direction. |
| Need to go from an image/mockup to working code | **image-to-code** | Generates its own reference images first, then implements to match. Codex-oriented but usable generally. |
| Need website design **reference images only** (no code) | **imagegen-frontend-web** | One image per section, composition variety enforced, no code output. |
| Need mobile app screen **concepts only** (no code) | **imagegen-frontend-mobile** | iOS/Android screen concepts in phone mockups, image-only. |
| Upgrading an existing site/app without breaking functionality | **redesign-existing-projects** | Audits current design, flags generic AI patterns, applies fixes in place. |
| Building a DESIGN.md for Google Stitch | **stitch-design-taste** | Semantic design-system file generation for Stitch workflows. |
| Any task where output must not be truncated / no placeholders | **full-output-enforcement** | Orthogonal — stack with any of the above when full, unabridged code output matters. |

## Quick heuristics

- **Web UI + code, no strong aesthetic named** → `design-taste-frontend`.
- **Aesthetic named** (brutalist, minimalist, luxury/brand, Awwwards/motion-heavy) → match the row above.
- **User wants images, not code** → one of the two `imagegen-frontend-*` skills.
- **Existing project, not greenfield** → `redesign-existing-projects`.
- **Anything Stitch-specific** → `stitch-design-taste`.
- **Truncation/placeholder complaints on long generations** → add `full-output-enforcement` on top of whichever design skill is active.

## Source

Installed via `npx skills add https://github.com/Leonxlnx/taste-skill --agent claude-code`, then consolidated from 13 top-level `.claude/skills/` folders into this single `taste-skill/` bundle for organization. All sub-skills passed Gen/Socket/Snyk security scans (Safe, 0 alerts, Low Risk) at install time (2026-07-03).
