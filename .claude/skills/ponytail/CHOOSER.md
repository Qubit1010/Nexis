# Ponytail Chooser

One family, six tools. Pick by what you're trying to do, not by name.

## Decision tree

**"I'm about to build / fix something — keep me from over-building."**
→ `/ponytail` (the mode). Stays active every response. Levels:
- `lite` — build what's asked, name the lazier alt in one line
- `full` (default) — the ladder enforced: YAGNI → reuse → stdlib → native → installed dep → one line → minimum
- `ultra` — YAGNI extremist, deletion before addition, challenges the requirement

**"Review this diff/PR for over-engineering only."**
→ `/ponytail-review`. One line per finding on the diff. Correctness/security/perf are out of scope (use a normal review for those).

**"Audit the whole repo, not just a diff — what can I cut?"**
→ `/ponytail-audit`. Repo-wide scan, ranked biggest cut first. One-shot report, applies nothing.

**"What shortcuts did ponytail defer? Track them before they rot."**
→ `/ponytail-debt`. Harvests every `ponytail:` comment into a ledger with ceiling + upgrade trigger. Flags any marker with no trigger (the ones that silently rot).

**"Show me why ponytail is worth it — the numbers."**
→ `/ponytail-gain`. Benchmark-medians scoreboard (lines/cost/speed). Note: benchmark medians, NOT this-repo savings — never invents a per-repo figure.

**"Remind me what all these commands do."**
→ `/ponytail-help`. The reference card.

## Quick pick by scenario

| Scenario | Use |
|----------|-----|
| Writing new code or fixing a bug | `/ponytail` (mode) |
| PR/diff looks bloated | `/ponytail-review` |
| Inherited a messy repo, want a hit list | `/ponytail-audit` |
| "What did we mark as 'later'?" | `/ponytail-debt` |
| Justify the approach to a teammate | `/ponytail-gain` |
| Forgot which command does what | `/ponytail-help` |

## Turn it off

`stop ponytail` or `normal mode` (or `/ponytail off`).

## Pair with

Caveman governs *how you talk* (terse prose). Ponytail governs *what you build* (least code that works). Use together for max signal-per-token.
