# blog-writer — eval benchmark (iteration 1)

Date: 2026-07-21. Method: skill-creator with-skill vs baseline (no-skill), graded against `evals.json` assertions. Both configs skipped live web research to isolate structure/voice/metadata.

## Result

| Eval | With-skill | Baseline | Skill lift |
|---|---|---|---|
| #1 SEO blog (AI agents for support) | 10/10 | 8/10 | +2 |
| #3 from-scratch (no topic) | 4/4 | 3/4 | +1 |
| **Aggregate** | **14/14 (100%)** | **11/14 (79%)** | **+21 pts** |

## Where the skill won (the differentiators)

- **SEO title/meta length discipline** — with-skill hit 54-char title / 156-char meta; baseline ran ~99 / ~180 (both over limit).
- **No-agency-name rule** — with-skill kept Aleem's personal brand (author = the person); baseline stamped `author: NexusPoint`, violating voice-principles.
- **Honesty rule** — with-skill refused to invent statistics and flagged the skipped research; baseline fabricated "70-80 percent" style numbers.
- **AEO/GEO structure** — with-skill added answer-block callouts (the extractable snippets), two comparison tables, and both `BlogPosting` + `FAQPage` JSON-LD; baseline had an FAQ but no schema, tables, or callouts.
- **From-scratch gating** — with-skill paired every proposed angle with a primary keyword + search intent + format; baseline proposed angles without keywords/intent.

## Notes / not-yet-tested

- Tone quality is judged at the human review gate, not asserted here (subjective).
- Eval #2 (how-to / AI Overviews) written but not run this iteration; structural assertions overlap #1.
- Live research path (Step 2) and the actual Google Doc export were intentionally not exercised in the benchmark; `publish.py`'s markdown parser was unit-tested separately and the Doc engine (`save_content.py`) is already production-proven via content-engine/post-creator.
