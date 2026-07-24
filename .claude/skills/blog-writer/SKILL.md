---
name: blog-writer
description: >
  Research-backed long-form blog engine for Aleem's personal brand. Writes a complete, SEO + AI-search optimized blog post - from scratch (topic proposed) or from a given topic - that reads unmistakably human, not AI-generated, in Aleem's voice. Every post is engineered for traditional SEO AND for citation by AI answer engines (AEO / GEO / AIO - ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews): answer-first structure, query fan-out coverage, extractable blocks, comparison tables, FAQ + schema, E-E-A-T, plus a full SEO metadata package. Grounded in an 83-source cited 2026 corpus (references/research-synthesis.md) and Aleem's voice-principles; honestly separates peer-reviewed findings from practitioner heuristics. Outputs a markdown file and, on request, a Google Doc. Use whenever Aleem says "write a blog", "write a blog post", "SEO blog", "optimize this blog for AI/search", "blog about X", "long-form article on X", "write me a blog that ranks", "blog that gets cited by AI", "AEO/GEO blog", "create a blog from scratch", or gives a topic and asks for a finished post. For the multi-platform content flywheel (ideas -> LinkedIn + Instagram + blog, repurposing), use content-engine; for the exhaustive AEO/GEO audit methodology, cross-reference ai-seo. This skill is the deep single-article writer.
argument-hint: [topic, or "from scratch" + niche/angle]
---

# Blog Writer

Aleem's research-backed engine for one thing done well: a finished, **SEO + AI-search optimized long-form blog post** that reads human and sounds like Aleem, not a template.

## Read once (provenance + honesty)
- Built research-first on an **83-source cited 2026 corpus** (`references/research-synthesis.md`, audit trail in `_research/sources.json`) covering blog SEO, AEO/GEO, Google AI Overviews, human-tone writing, and blog formats.
- **Honesty rule:** the corpus flags every claim **[peer-reviewed]** vs **[practitioner]**. Peer-reviewed: people-first/E-E-A-T, answer-first structure drives AI citation, query intent > rank, query fan-out, human-tone craft. Practitioner (attributed, not invented): the Princeton GEO per-method boosts, the "40-60 word answer block," format citation-share numbers. Never present a practitioner heuristic as measured fact, and never quote a number that isn't in the corpus or a live query.
- **Voice:** this writes as **Aleem, personal brand.** `content-engine/references/voice-principles.md` is the voice source of truth. Hard rules from it: never name the agency, never mention university/BSAI/student; no em dashes or smart quotes in the body; level 7+ content only (POV/case study/framework, never a neutral explainer).

## Boundary (avoid overlap)
- **blog-writer (this):** ONE deep, SEO/AEO/GEO-optimized, human-toned long-form article, from a topic or from scratch, with a full metadata package. The single-article specialist.
- **content-engine:** the multi-platform content *system* - idea sourcing, scoring, the Blog -> LinkedIn + Instagram repurposing flywheel, logging. Use it for "what should I post", "full content run", "repurpose this". (blog-writer reuses its `voice-principles.md` and `save_content.py`.)
- **ai-seo** (installed): the exhaustive AEO/GEO audit methodology (robots.txt for AI bots, llms.txt, OKF, full schema tables, the Princeton table). Cross-reference for site-level audits; blog-writer distills the article-relevant parts.

## Context to load first
1. `content-engine/references/voice-principles.md` - Aleem's voice (always).
2. `references/seo-aeo-geo-checklist.md` - the optimization scoreboard (always).
Then load the workflow-specific reference(s) below. Pull citations/depth from `references/research-synthesis.md` when you need the evidence behind a claim.

---

## Entry modes
| Mode | Trigger | First move |
|---|---|---|
| **from-topic** | a topic/title/keyword is given | confirm intent + angle, go |
| **from-scratch** | "write a blog", no topic | propose 3 angles from Aleem's pillars + a niche, let him pick |
| **optimize-existing** | a draft/URL + "optimize for SEO/AI" | skip drafting; run steps 5-7 on the existing text |

---

## Workflow

### Step 1 - Intake
Extract or decide: **topic**, **search intent** (informational / comparison / how-to / opinion), **primary keyword** (given or derive), **content type** (guide / comparison / how-to / listicle / opinion-case-study), **audience**, **target length** (depth-driven, see `blog-structure-playbook.md`).
- **from-scratch:** propose 3 angles rooted in Aleem's pillars (AI automation, agentic systems, real client/build lessons, cross-domain: philosophy/systems/CS) and one target keyword each. Let him pick before writing. Ask at most ONE clarifying question if truly blocked.

### Step 2 - Research the topic (real sources)
Gather facts, stats, and citable sources - GEO rewards real citations and specific data, and E-E-A-T rewards accuracy. Use the `research` skill (unsandboxed, Python 3.12):
```
python .claude/skills/research/scripts/research.py --query "<topic> 2026" --depth medium --json
```
Use `--depth deep` for a pillar/definitive guide. Also brainstorm the **5-10 query fan-out questions** the post must cover (`seo-aeo-geo-checklist.md` §1). Keep the source URLs - they become citations + external links + the FAQ.

### Step 3 - Keyword + outline
Set primary + 3-6 supporting keywords mapped to intent. Pick the format template from `blog-structure-playbook.md` and outline: H1 hook, answer-first intro, H2s phrased as the fan-out questions (each answer-first), the right blocks per section (steps / comparison table / pros-cons / FAQ), where first-hand experience lands, the FAQ, the ending.

### Step 4 - Write in Aleem's voice (level 7+)
Draft the post per `voice-principles.md`: real hook (never "In this post..."), strong POV, lived experience with specific anchors, the So-What test on every paragraph, the Golden Pattern arc for case-study/opinion. **Draft in layers** (`human-tone-rules.md`): idea pass, then evidence pass, then a rhythm/voice pass. Weave cited stats in naturally as interpretation, not a data dump. If Aleem hasn't shipped the exact thing, use the No-Experience Fallback (bridge to adjacent work, frame as hypothesis) - never fake authority.

### Step 5 - SEO / AEO / GEO / AIO pass
Run the draft through `references/seo-aeo-geo-checklist.md`:
- Answer-first intro + each H2 opens with a short (~40-60 word) self-contained answer.
- Headings map to real queries; comparison table where the intent is "vs/best"; FAQ (3-6 fan-out Q&A).
- Cite sources + include specific dated stats (direction, not the exact Princeton %); first-hand experience for E-E-A-T.
- Build the **SEO metadata block**: SEO title (<=60), meta description (<=160), URL slug, primary + supporting keywords, the extractable answer callouts, FAQ + `FAQPage` JSON-LD, `Article`/`BlogPosting` JSON-LD stub, image alt texts, internal-link suggestions, external sources cited, "last updated" date.

### Step 6 - Human-tone pass (mandatory)
Run `references/human-tone-rules.md`: phrase audit (purge "game-changer/leverage/dive into", empty "Furthermore/Moreover" openers, "it's not X it's Y"), cadence/burstiness (vary sentence length, no 3 equal-length in a row), first-person specificity, no em dashes / smart quotes, and the **read-aloud self-check**. Also run `what-not-to-do.md`. The point is genuine voice, not detector-gaming.

### Step 7 - Review gate (single checkpoint)
Present the finished post + the SEO metadata block inline for approval. State the format, target keyword, and word count. Ask for a go before saving. This is the one human checkpoint.

### Step 8 - Save (on approval)
Always write the markdown file (post + metadata block) to `content/blog/<slug>.md` (or a path Aleem names). Then, if he wants a Google Doc:
```bash
python .claude/skills/blog-writer/scripts/publish.py content/blog/<slug>.md
```
`publish.py` parses the markdown and reuses content-engine's `save_content.py` (creates a Doc in "Nexis Content", normalizes smart quotes, returns the URL). Pipe/run via Bash on Windows (PowerShell adds a BOM that gws rejects). If it fails, output the post inline and note it.

---

## Output contract
1. **Markdown file** - the blog (H1 + body) followed by a `## SEO Metadata` section containing the full package from Step 5.
2. **Google Doc** (on request) via `publish.py`.
Both always. Never a Doc without the markdown.

## Edge cases
| Scenario | Action |
|---|---|
| Vague / no topic | from-scratch mode: propose 3 angles, one keyword each, let him pick |
| Asked for a stat not in the corpus | run the live query (`notebook-live-query.md`); if still nothing, say so - never invent |
| Client/company blog (not Aleem's brand) | this skill is personal-brand; flag it and offer client-content-creator instead |
| Wants ideas / repurposing / multi-platform | hand off to content-engine |
| Wants a full site AEO audit | hand off to ai-seo |
| Practitioner number requested as fact | give it labeled ("industry heuristic, not measured"), cite the honesty flag |
| save/publish fails | output inline, note the failure |

## Reference map
```
SKILL.md
references/
├── research-synthesis.md      # MASTER: Q1-Q5 cited synthesis of 83 2026 sources (peer-reviewed vs practitioner flags)
├── seo-aeo-geo-checklist.md    # THE SCOREBOARD - the optimization pass (load by default)
├── blog-structure-playbook.md  # formats, outlines, length, marrying SEO structure with Aleem's voice
├── human-tone-rules.md         # anti-AI-tell pre-publish pass (research + voice-principles mechanics)
├── what-not-to-do.md           # stale/penalized/AI-tell kill list
└── notebook-live-query.md      # LIVE FALLBACK: fresh research deep pass -> append to synthesis
_research/                       # audit trail: sources.json (83) + q1..q5.json + reports.md + gather_blog.sh + build_sources_index.py
scripts/
└── publish.py                  # blog .md -> Google Doc (reuses content-engine/save_content.py)
evals/evals.json
```
Reuses: `content-engine/references/voice-principles.md` (voice), `content-engine/scripts/save_content.py` (Docs). Siblings: **content-engine** (content system), **ai-seo** (AEO/GEO audit), **research** (topic sources), **client-content-creator** (client-brand blogs).
