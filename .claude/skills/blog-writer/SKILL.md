---
name: blog-writer
description: >
  Research-backed long-form blog engine for Aleem's personal brand AND for client brands. Writes a complete, SEO + AI-search optimized blog post - from scratch (topic proposed) or from a given topic - that reads unmistakably human, not AI-generated, in the resolved brand voice: Aleem's by default, or a client's when a client-projects slug is named. Every post is engineered for traditional SEO AND for citation by AI answer engines (AEO / GEO / AIO - ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews): answer-first structure, query fan-out coverage, extractable blocks, comparison tables, FAQ + schema, E-E-A-T, plus a full SEO metadata package. Grounded in an 83-source cited 2026 corpus (references/research-synthesis.md) and the resolved voice source; honestly separates peer-reviewed findings from practitioner heuristics. Outputs a markdown file and, on request, a Google Doc. Use whenever Aleem says "write a blog", "write a blog post", "SEO blog", "optimize this blog for AI/search", "blog about X", "long-form article on X", "write me a blog that ranks", "blog that gets cited by AI", "AEO/GEO blog", "create a blog from scratch", "write a blog for [client]", "client blog post", or gives a topic and asks for a finished post. For the multi-platform content flywheel (ideas -> LinkedIn + Instagram + blog, repurposing), use content-engine; for a full-site AEO/GEO audit and AI-visibility measurement, use seo-authority-ai; for landing pages, sales pages, emails and ads rather than articles, use copy-conversion. This skill is the deep single-article writer.
argument-hint: [topic, or "from scratch" + niche/angle, or "for <client-slug>"]
---

# Blog Writer

Aleem's research-backed engine for one thing done well: a finished, **SEO + AI-search optimized long-form blog post** that reads human and sounds like Aleem, not a template.

## Read once (provenance + honesty)
- Built research-first on an **83-source cited 2026 corpus** (`references/research-synthesis.md`, audit trail in `_research/sources.json`) covering blog SEO, AEO/GEO, Google AI Overviews, human-tone writing, and blog formats.
- **Honesty rule:** the corpus flags every claim **[peer-reviewed]** vs **[practitioner]**. Peer-reviewed: people-first/E-E-A-T, answer-first structure drives AI citation, query intent > rank, query fan-out, human-tone craft. Practitioner (attributed, not invented): the Princeton GEO per-method boosts, the "40-60 word answer block," format citation-share numbers. Never present a practitioner heuristic as measured fact, and never quote a number that isn't in the corpus or a live query.
## Voice resolution (do this before anything else)

This skill writes in **one resolved voice source**. Everything downstream - including every
place `blog-structure-playbook.md` and `human-tone-rules.md` say "voice-principles" - means
**the voice source resolved here**, not always Aleem's.

| Subject | Voice source of truth | Hard rules |
|---|---|---|
| **Aleem, personal brand** (default) | `agency/personal-brand-voice.md` | Never name the agency; never mention university/BSAI/student; level 7+ only (POV/case study/framework, never a neutral explainer) |
| **A client brand** (a `client-projects/<slug>` is named, or the post is for someone else's site) | `client-projects/<slug>/14-brand-voice.md` (dimensions, tone shifts, use/never-use vocabulary) + `13-brand-strategy.md` (positioning, what the brand rules out) | Apply the client's never-use list; **the Aleem-specific rules above do not apply** and must not be carried over. Never mention NexusPoint or Aleem in the article |

Both, always: no em dashes or smart quotes in the body.

**If a client run finds no `14-brand-voice.md`,** say so and offer to run `brand-voice` first -
writing a client article with an invented voice is how a brand ends up sounding like its
agency. If Aleem declines, derive a working voice from the client's live copy and label it an
assumption in the handoff, rather than presenting it as their voice.

First-hand experience for E-E-A-T is Aleem's on a personal post and **the client's** on a
client post. Never attribute Aleem's projects to a client, or a client's results to Aleem.

## Boundary (avoid overlap)
- **blog-writer (this):** ONE deep, SEO/AEO/GEO-optimized, human-toned long-form article, from a topic or from scratch, with a full metadata package. The single-article specialist.
- **content-engine:** builds a subject's content engine (hooks, formats, copywriting rules) and writes posts against it, plus the Blog -> LinkedIn + Instagram repurposing flywheel and logging. It no longer ideates. Use it for "full content run", "repurpose this". (blog-writer reuses its `voice-principles.md` and `save_content.py`.)
- **seo-onpage:** the on-page and content EXECUTION skill (Tier 2). It owns the canonical on-page thresholds and measures them - titles, metas, headings, structure, internal links, media, E-E-A-T, schema - against a draft or a live URL, and audits whole sites. blog-writer writes the article and calls it in Step 5b to validate; it does not carry its own copies of those numbers.
- **seo-authority-ai:** the in-house AEO/GEO audit and AI-visibility MEASUREMENT skill (Tier 4). It owns robots.txt vs the AI-bot matrix, llms.txt, entity resolution, and sampling whether answer engines actually cite the brand. Hand off site-level AEO work to it; blog-writer distills only the article-relevant parts. (`marketing-skills/ai-seo` is the installed third-party equivalent - use the in-house one first.)
- **copy-conversion:** conversion copy rather than articles - landing pages, sales pages, emails, ads, CTAs, product descriptions. If the ask is a page that sells rather than an article that ranks, route there.
- **copywriting-advisor:** the knowledge and factcheck hub for copywriting claims. If the ask is "is that statistic real" or "explain why this copy underperforms", route there.

## Context to load first
1. The **resolved voice source** (see Voice resolution above) - always. Aleem's is `agency/personal-brand-voice.md`; a client's is `client-projects/<slug>/14-brand-voice.md`.
2. `references/seo-aeo-geo-checklist.md` - the optimization scoreboard (always). It owns the AEO/GEO and query-fan-out half; the on-page thresholds it cites are owned by `seo-onpage/references/checks.md` and cross-referenced, not duplicated.
Then load the workflow-specific reference(s) below. Pull citations/depth from `references/research-synthesis.md` when you need the evidence behind a claim.

---

## Entry modes
| Mode | Trigger | First move |
|---|---|---|
| **from-topic** | a topic/title/keyword is given | confirm intent + angle, go |
| **from-scratch** | "write a blog", no topic | propose 3 angles from Aleem's pillars + a niche, let him pick |
| **optimize-existing** | a draft/URL + "optimize for SEO/AI" | skip drafting; run steps 5a-7. Start by measuring: `seo-onpage/scripts/onpage.py --draft <file>` (or `--url`) so the edit is aimed at something real rather than at a re-read. |
| **client** | a `client-projects/<slug>`, a client name, or "blog for [client]" | resolve the client voice source FIRST (see Voice resolution), then run from-topic or from-scratch as normal. Combines with the other modes rather than replacing them |

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

### Step 5a - SEO / AEO / GEO / AIO pass
Run the draft through `references/seo-aeo-geo-checklist.md`:
- Answer-first intro + each H2 opens with a **40-60 word** direct answer, inside a section that stands alone at roughly **134-167 words**. These are two different numbers and both matter: the 40-60 is the answer that opens the section, the 134-167 is the whole extractable unit. See `seo-onpage/references/checks.md` §2.
- Headings map to real queries; comparison table where the intent is "vs/best"; FAQ (3-6 fan-out Q&A).
- Cite sources + include specific dated stats (direction, not the exact Princeton %); first-hand experience for E-E-A-T.
- Build the **SEO metadata block**: SEO title (**50-60**, primary keyword in the first 40 characters), meta description (**105-155**, key info in the first 120), URL slug, primary + supporting keywords, the extractable answer callouts, FAQ + `FAQPage` JSON-LD, `Article`/`BlogPosting` JSON-LD stub, image alt texts, internal-link suggestions, external sources cited, "last updated" date.

### Step 5b - Validate the draft (mechanical)
Nothing above verifies itself, so measure it. `seo-onpage` owns the on-page thresholds and runs them against the draft file:
```bash
python .claude/skills/seo-onpage/scripts/onpage.py --draft content/blog/<slug>.md \
  --primary-keyword "<primary keyword>" --fails-only
```
Fix every `fail`. Read every `review` and decide - those are the judgment calls (does the opening actually answer the query, is a section padding), and the script attaches the evidence rather than guessing.

Optionally, to see what the pages currently ranking cover that this draft does not:
```bash
python .claude/skills/seo-onpage/scripts/terms.py --query "<primary keyword>" --draft content/blog/<slug>.md
```
Treat that as coverage, never as a keyword quota. If you edit in response, edit under the Revise-Don't-Rewrite contract in `seo-onpage/references/terms-workflow.md` - the failure mode is regenerating a smoother, blander post that has lost the first-hand detail. Then re-run and report the delta.

Carry the results into Step 7. Do **not** add a second human checkpoint.

### Step 6 - Human-tone pass (mandatory)
Run `references/human-tone-rules.md`: phrase audit (purge "game-changer/leverage/dive into", empty "Furthermore/Moreover" openers, "it's not X it's Y"), cadence/burstiness (vary sentence length, no 3 equal-length in a row), first-person specificity, no em dashes / smart quotes, and the **read-aloud self-check**. Also run `what-not-to-do.md`. The point is genuine voice, not detector-gaming.

### Step 7 - Review gate (single checkpoint)
Present the finished post + the SEO metadata block inline for approval, **plus the Step 5b check result** (fails fixed, and the `review` calls you made with your reasoning). State the format, target keyword, and word count. Ask for a go before saving. This is the one human checkpoint - 5b reports into it rather than adding another.

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
| Client/company blog (not Aleem's brand) | **client mode** - resolve the client voice source, then proceed normally. Aleem-specific rules do not carry over |
| Client mode, no `14-brand-voice.md` exists | Say so and offer `brand-voice` first. If declined, derive a working voice from their live copy and label it an assumption |
| Client mode, no first-hand experience to draw on | Use the client's own projects and results, never Aleem's. If they have none, use the No-Experience Fallback rather than borrowing someone else's |
| Wants repurposing / multi-platform | hand off to content-engine |
| Wants ideas / what to post about | no skill ideates since 2026-08-28. Point at `18-content-strategy.md` |
| Wants a full site AEO audit or AI-visibility measurement | hand off to seo-authority-ai |
| Wants a landing page, sales page, email or ad | hand off to copy-conversion - this skill writes articles |
| Asked whether a copywriting statistic is real | hand off to copywriting-advisor (factcheck mode) |
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
└── publish.py                  # blog .md -> Google Doc (reuses tools/gdocs/save_content.py)
evals/evals.json
```
Reuses: the resolved voice source - `agency/personal-brand-voice.md` (Aleem) or `client-projects/<slug>/14-brand-voice.md` (client) - and `tools/gdocs/save_content.py` (Docs). Siblings: **content-engine** (content system), **seo-authority-ai** (AEO/GEO audit + AI-visibility measurement), **seo-onpage** (on-page thresholds), **copy-conversion** (conversion copy), **copywriting-advisor** (copy factcheck + diagnosis), **research** (topic sources), **brand-voice** (defines the client voice this consumes).
