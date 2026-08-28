---
name: content-strategy
description: "Use to BUILD or AUDIT a client's content strategy: content pillars, the editorial calendar and publishing cadence, the content funnel, distribution, repurposing, the evergreen and trending mix, and how any of it gets measured. Execution skill that produces the artifact, not the advice skill. Triggers on: content strategy, content plan, content marketing strategy, editorial strategy, content pillars, pillar content, content themes, content calendar, editorial calendar, publishing schedule, publishing cadence, content funnel, content by funnel stage, top of funnel content, content distribution, amplification, syndication, content repurposing, repurposing map, content clusters, evergreen versus trending, content refresh, content audit, content inventory, content operations, editorial governance, thought leadership programme, UGC programme, creator programme, content measurement, content KPIs, content ROI reporting. Also: 'what should we be publishing', 'we post but nothing happens', 'how often should we post', 'we have no content plan', 'our blog is dead', 'how do we get more out of one piece', 'what do we do with all these webinar recordings', 'audit our content', 'how do we prove content is working'. Works from a Google Doc, a PDF or DOCX deck, pasted text, a website URL it crawls, live channels, or a client-projects slug. Consumes 07-strategic-foundation.md, 08-audience-persona.md, 13-brand-strategy.md, 14-brand-voice.md and the keyword map in 09-seo-foundation.md rather than re-deriving them. Outputs client-projects/<slug>/18-content-strategy.md. For what a format should look like, or whether a content statistic is real, use content-advisor. To write a piece use content-production, blog-writer, carousel, shorts-creator or reel-creator. For Aleem's personal-brand content use content-engine and post-creator. Works for any client slug, including nexuspoint."
argument-hint: [a client slug, a doc or URL, or a content strategy to audit]
---

# Content Strategy

The execution spoke that turns content knowledge into a client's operating plan.

**`content-advisor` knows things. This skill does things.** If the ask is "explain content
pillars to me", that is the hub. If it is "build their pillars", it is this.

## Where this sits

```
07-strategic-foundation ─┐
08-audience-persona ─────┤
13-brand-strategy ───────┼──> 18-content-strategy.md ──> content-production
14-brand-voice ──────────┤        (this skill)           blog-writer / carousel
09-seo-foundation ───────┘                               shorts-creator / reel-creator
                                                         linkedin-infographics
```

Upstream is taken, never re-derived. Downstream is routed, never duplicated.

---

## Operating principles (read once)

- **Operability is the bar.** Someone who has never met the client should be able to read
  `18-content-strategy.md` and publish the right thing on Monday. A calendar row with no named
  owner will not happen, and a strategy nobody can execute is a document, not a strategy.
- **Size the plan to the team that exists.** The most common failure in this deliverable is
  prescribing an operation the client cannot staff. An ambitious cadence abandoned in month
  three costs more than a modest one sustained, and sizing is a strategic decision that gets
  stated in the document rather than a compromise that gets hidden.
- **Distribution is not publishing.** It is the section most strategies skip and the reason
  most content underperforms. Every format gets day one, week one, and day thirty.
- **Refuse the folklore.** The 80/20 and 4-1-1 educational-to-promotional ratios, "one video
  becomes thirty pieces", "buyers are 57% through the journey", "content costs 62% less and
  generates 3x the leads" - none of these has a traceable primary source. See
  `content-advisor/references/what-not-to-do.md`. Set the mix from the client's funnel and
  say that is what you did.
- **Never promise a percentage lift.** Content attribution is genuinely hard, observational and
  experimental estimates diverge substantially, and most client stacks cannot resolve content's
  contribution to revenue at all. The honest measurement section says what it cannot tell them.
- **Consume the cluster, never rebuild it.** `seo-foundation` builds the keyword map and
  `seo-onpage` sizes and links the cluster. This skill turns that map into a calendar.

---

## Boundaries / handoffs (important)

| Hand off to | For |
|---|---|
| `content-advisor` | What a format should look like, whether a statistic is real, why content is underperforming, and any "explain this" question. It owns the corpus this skill cites |
| `content-production` | Writing the formats no other skill owns: whitepapers, ebooks, gated guides, newsletters, threads, X posts, memes, webinar structure, long-form video scripts, LinkedIn document carousels |
| `blog-writer` | Writing an actual article, including its AEO/GEO structure. It owns article-level search on its own corpus. Cross-cite, never restate |
| `carousel` / `linkedin-infographics` / `shorts-creator` | Image prompts for Instagram carousels, LinkedIn infographics and vertical short frames |
| `reel-creator` / `hyperframes-reel` | A rendered, voiced 9:16 video |
| `podcast-repurposer` | Turning a transcript into short-form pieces |
| `seo-foundation` / `seo-onpage` | The keyword map, cluster sizing, and page-level keep/update/merge/remove tracks |
| `copy-conversion` | Copy whose job is to make someone act, and how a post is formatted for a platform |
| `brand-voice` / `brand-strategy` / `strategic-foundation` | The upstream documents, when they are missing |
| `content-engine` / `post-creator` | Aleem's personal brand: his pillars, his voice, the weekly posting schedule. **Not this skill** |
| `social-media-advisor` | Platform-native mechanics this skill deliberately stops short of: how a platform ranks content, per-platform cadence and hashtag strategy, organic account and follower growth, engagement strategy, profile optimisation, community management and social listening. This skill decides *which channel and when*; that one explains *how the channel behaves* |
| *(no owning skill)* | Channel mix, offer and pricing, paid ads, email and lifecycle, and cross-channel measurement. No current skill covers these. Say so plainly rather than improvising. |

State the handoff when you make it. Do not silently stop.

---

## Context to load first

`references/method.md` in build mode, `references/review-rubric.md` in audit mode. Pull
`content-advisor/references/format-specs/` when choosing formats and
`content-advisor/references/research-synthesis.md` when you need the evidence behind a claim.

**Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **build** (default) | "build a content strategy", "content plan for", "define their pillars", "we have no content plan", a slug or a brief | `method.md` + `report-structure.md` |
| **audit** | "audit our content", "review this strategy", "is this any good", an existing strategy document | `review-rubric.md` |
| **calendar** | "just the calendar", "12-week plan", "what should they publish", pillars already exist | `method.md` Phases 5-6 only |
| **repurpose** | "get more out of this", "repurposing plan", "what do we do with these recordings" | `method.md` Phase 8 |

If ambiguous, prefer build. If an audit reveals the document is a calendar rather than a
strategy, say so and offer build mode rather than scoring the wrong artifact.

---

## Workflow

Follow `references/method.md`, Phases 0-11. In short:

1. **Resolve the input** (Phase 0) — Doc, file, URL, slug or name.
2. **Read upstream and take** (Phase 1) — `07`, `08`, `13`, `14`, `09`. Name what is missing,
   offer to run the producing skill, then proceed with gaps labelled `[assumption]`.
3. **Audit what they already publish** (Phase 2) — 12-month inventory, what worked, real
   capacity, unused raw material. Never skip this.
4. **Ask 2-4 questions once** (Phase 3) — capacity, commercial goal, constraints, what they
   already abandoned. Nothing inferable from steps 2-3.
5. **Pillars** (Phase 4) — 3-5, each with an exclusion.
6. **Format x funnel map, cadence, calendar** (Phases 5-6).
7. **Distribution, repurposing, evergreen** (Phases 7-9).
8. **Measurement and assumptions** (Phases 10-11) — including what cannot be measured.
9. **Write** to `client-projects/<slug>/18-content-strategy.md` per `report-structure.md`.

---

## Writing Rules

- **Internal (to Aleem):** direct, analytical, bullets. Lead with the recommendation.
- **Client-facing:** operator, not consultancy. Write like someone who has run a content
  operation, not someone selling one. **Never mention NexusPoint, Aleem, or any skill name in
  the client document.**
- Both: no emojis, **no em dashes in body text** (headings may use them).
- Every number carries its tier. `[P]` is labelled vendor-published; `[P*]` platform figures
  carry a retrieval date. `[K]` craft may inform technique, never support a claim.
- Be concrete: name the format, the channel, the owner, the date.

---

## Edge Cases

| Scenario | Action |
|---|---|
| No upstream documents at all | Say so plainly, offer `strategic-foundation` first, then proceed. Every derived fact is `[assumption]` |
| Client wants daily posting on five channels with two people | Build the plan they can hold, show the arithmetic, and name what was cut. Do not quietly deliver the fantasy |
| Asked for a guaranteed traffic or lead number | Refuse the forecast. Give leading indicators and the honest limit of attribution |
| Their best content contradicts the positioning | Report it as a finding. It usually means the positioning is wrong, not the content |
| "What's the ideal posting frequency" | Capacity first, then evidence. There is no universal number and the corpus does not contain one |
| A pillar excludes nothing | It is a topic area. Rewrite it or cut it |
| Client already has pillars they like | Audit them against row 1, keep what holds, and say which ones exclude nothing |
| Asked to write the pieces too | Build the strategy, then route: `content-production`, `blog-writer`, or the visual skills |
| No analytics access | Say the measurement section is unverifiable, propose what to instrument, do not invent baselines |
| Nothing published in 18 months | The audit finding is capacity or approval latency, not content. Diagnose that before planning |

---

## Reference Map

```
references/
├── method.md            THE PIPELINE, Phases 0-11. Build mode
├── report-structure.md  Section order for 18-content-strategy.md
└── review-rubric.md     7-row scorecard + the Monday and capacity gates. Audit mode
```

No `_research/` here on purpose. `[sN]` resolves via
`.claude/skills/content-advisor/_research/sources.json`. Run
`python .claude/skills/content-advisor/_research/gather.py verify` after any citation edit;
it checks this skill's `references/` too.
