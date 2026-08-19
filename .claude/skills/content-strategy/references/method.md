# Method — building a content strategy

The pipeline. Load this first in build mode.

Output: `client-projects/<slug>/18-content-strategy.md`, structured per `report-structure.md`.

**The bar is that someone could run this next Monday without asking a question.** Not an essay
about the importance of content. A pillar they can write against, a cadence they can actually
sustain with the people they have, a distribution plan naming who does what, and a measurement
plan that does not require attribution software they do not own. A strategy the client has to
interpret before using has failed, however well it reasons.

**The most common failure in this deliverable is prescribing a content operation the client
cannot staff.** A four-person company does not publish daily across five channels. Sizing the
plan to the team is a strategic decision, not a compromise, and it is stated in the document.

---

## Phase 0 — Resolve the input

Same dispatch as the sibling skills. All run **UNSANDBOXED**.

| What they gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / PPTX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` |
| `.md` / `.txt` / pasted text | `Read` it, or use the paste inline |
| Business website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 20 --extract raw` |
| Name only | `python .claude/skills/research/scripts/research.py --query "<name> <industry>" --depth medium --mode entity` then crawl |
| `client-projects/<slug>` | `Read` the numbered files directly, then still audit the live channels (Phase 2) |

---

## Phase 1 — Read upstream and take, do not re-derive

The phase that separates this from a generic content-calendar prompt. These documents exist
for a reason, and re-deriving positioning here forks the client's brand quietly.

| File | Take |
|---|---|
| `07-strategic-foundation.md` | The UVP, the business model, the target customer. Content pillars are derived from these, never invented alongside them |
| `08-audience-persona.md` | The questions the audience actually asks, in their words, grouped by intent. **This is the raw material for the entire topic layer** - a pillar built without it is a guess about what people want to read |
| `13-brand-strategy.md` | Positioning, personality, and the **"what this rules out"** section. A pillar that violates the exclusions is off-brand however well it would perform |
| `14-brand-voice.md` | Voice dimensions, tone shifts per context. Constrains *how* every format sounds; `content-production` and `blog-writer` both read it downstream |
| `09-seo-foundation.md` | The keyword map and the SERP-overlap clusters, if the SEO chain has run. **Consume this; never rebuild it.** The cluster becomes the topic spine of the calendar |
| `12-seo-authority-ai.md` | Which pages AI engines already cite, if it exists. Changes what is worth refreshing versus writing new |

### When they are missing

**Say so before writing, and offer to build them.** In order of how much damage the gap does:

| Missing | Consequence | Offer |
|---|---|---|
| `08-audience-persona.md` | Topics get invented from the category rather than mined from the audience. This is the single biggest driver of content nobody reads | Run `strategic-foundation --mode persona` |
| `07-strategic-foundation.md` | Pillars have nothing to ladder to, so they drift into whatever is easy to write | Run `strategic-foundation` first |
| `13-brand-strategy.md` | No exclusions means the calendar fills with generic category content | Run `brand-strategy` first |
| `14-brand-voice.md` | Every writer sounds different and the client rejects drafts on "tone" they cannot name | Run `brand-voice` first |
| `09-seo-foundation.md` | The search layer is guesswork. Survivable, unlike the four above | Run `seo-foundation`, or proceed and label the topic layer `[assumption]` |

If Aleem declines, **proceed** - do not stall the deliverable. Derive working substitutes from
the live channels and the category, and record every one in the fact table at the top as
`[assumption]`, never `[verified]`. The client should be able to see which parts of their
strategy rest on something they told us and which rest on our inference.

---

## Phase 2 — Audit what they already publish, before proposing anything

Non-negotiable, and the phase most often skipped. You cannot plan a content operation without
knowing what the last one produced.

1. **Inventory the last 12 months.** Every channel, what was published, how often, and when it
   stopped. Gaps are the most informative part: a blog that posted weekly for four months and
   then nothing tells you the cadence was unsustainable, which is a finding about capacity, not
   about content.
2. **Find what already works.** Their best-performing pieces, by their own numbers. A strategy
   that ignores the two things that worked and proposes five new formats is not a strategy.
3. **Inventory production capacity honestly.** Who writes, who films, who approves, and how
   long approval takes. **Approval latency is usually the real bottleneck, not writing.**
4. **Check what assets already exist** that have not been used: webinar recordings, sales
   decks, support docs, podcast back-catalogue, customer calls. Most clients are sitting on
   more raw material than they think, and repurposing it is cheaper than commissioning new.
5. **Read the competitors' content**, enough to know what is table stakes in the category and
   what nobody is covering.

---

## Phase 3 — Ask only what you could not infer

Batch **2 to 4 questions**, once, via `AskUserQuestion`. Never a questionnaire. Anything
answerable from Phase 1 or 2 is not a question.

The ones that genuinely cannot be inferred:

- **Capacity.** How many hours a week, from whom, and who signs off.
- **Commercial goal.** Pipeline, hiring, investor visibility and category education produce
  genuinely different plans, and the client rarely states this unprompted.
- **Constraints.** Regulated claims, legal review, competitors they cannot name, topics that
  are off limits.
- **What they have already tried and abandoned**, and why. Proposing it again unaware is the
  fastest way to lose the room.

---

## Phase 4 — Pillars

Three to five. Fewer than three and the brand looks one-note; more than five and none of them
accumulates authority.

Each pillar carries: **what it is**, **which audience question it answers** (cite the persona),
**what business outcome it ladders to**, **which formats it suits**, and **what it excludes**.

**The exclusion is the test.** A pillar that rules nothing out is a topic area, not a pillar.
"Industry insights" excludes nothing and will absorb any piece anyone wants to write, which is
how content operations become directionless without anyone deciding to.

Tag each pillar's role: **educational**, **thought leadership**, **promotional**, or **UGC**.
Do not reach for the 80/20 or 4-1-1 ratio here - see `what-not-to-do.md`; neither has a
traceable primary source. Set the mix from the client's funnel and their audience's awareness
level, and say that is what you did.

---

## Phase 5 — Format and funnel map

A table, not prose: **pillar x format x funnel stage x channel**.

Formats come from `content-advisor/references/format-specs/`. Do not restate the spec here;
name the format and let the hub own what it is. **Choose formats the client can actually
produce** - a podcast is a standing weekly commitment, not a content type you add to a plan.

State for each row: who produces it, roughly how long it takes, and what it costs in approval
time. A plan that omits production cost is a wish list.

---

## Phase 6 — Cadence and calendar

Cadence is set by **capacity first, evidence second** - never by a benchmark of what other
companies publish. Publishing frequency has real diminishing returns and real wearout effects
(synthesis Q12), and the failure mode in practice is an ambitious cadence abandoned in month
three, which costs more than a modest one sustained.

Produce a **12-week calendar** with the first 4 weeks specified to the piece and weeks 5-12 at
the theme level. Specifying all 12 in detail is false precision; nobody follows it past week 5.

Every row: date, pillar, format, channel, working title, the audience question it answers, the
CTA, and the owner. **A calendar row with no named owner will not happen.**

---

## Phase 7 — Distribution

The section most content strategies skip, and the reason most content underperforms. Publishing
is not distribution.

For each piece: **where it goes on day one, what happens in week one, and what happens at day
thirty.** Name the channels, the internal amplifiers (staff, the client's own team), the
existing audiences (newsletter, community), and any syndication or partner surface.

Treat seeding and amplification claims carefully - the evidence on who to seed is genuinely
mixed (synthesis Q13). Give the client a plan and say which parts are tested and which are
convention.

---

## Phase 8 — Repurposing map

One-to-many, drawn as an explicit map from the **hero asset** down to the derivatives, with the
transformation named at each step, not just the output format.

Do not promise a multiplier. "One video becomes thirty pieces" is folklore with no traceable
source (`what-not-to-do.md`), and thirty derivatives of a thin asset is thirty thin pieces.
Map what this specific asset can actually carry.

Where an existing skill produces the derivative, **name it**: `blog-writer`, `carousel`,
`shorts-creator`, `reel-creator`, `linkedin-infographics`, `podcast-repurposer`, or
`content-production` for the formats none of them own.

---

## Phase 9 — Evergreen, trending and refresh

Set the ratio deliberately and defend it. Evergreen accrues and needs maintenance; trending
spikes and decays fast (synthesis Q14). A client with no search presence and no audience needs
a different ratio from one with either.

Include a **refresh schedule** for the evergreen set: what gets reviewed, how often, and the
trigger for updating versus consolidating versus retiring. Hand the page-level mechanics to
`seo-onpage`, which owns the keep/update/merge/remove tracks. Do not restate them.

---

## Phase 10 — Measurement

Name the metric, where it is read, who reads it, and how often. Then state plainly what this
setup **cannot** tell them.

That last part is the honest half. Content attribution is genuinely hard, observational and
experimental estimates diverge substantially (synthesis Q15), and most SMB stacks cannot
resolve content's contribution to revenue at all. Say so in the document. **Never promise a
percentage lift**, and never present a modelled number as measured.

Give them leading indicators they can actually read, and one honest sentence about what would
have to be true to measure the rest.

---

## Phase 11 — Assumptions and what would change this

Close with the fact table's `[assumption]` rows gathered in one place, each with what would
confirm or kill it. A strategy that cannot be wrong is not a strategy.
