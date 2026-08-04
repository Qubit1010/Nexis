# Persona Playbook — an audience persona built for content and search

Produces a persona that a writer, an SEO, and an AI-search strategist can all work from. It
is derived from the same analysis as the rest of the foundation, and it is a **standalone
artifact** because the people who consume it (content, SEO, AEO/GEO) are usually not the
people who read the strategy document.

---

## What this artifact is, and is not

Get this right or the deliverable is decoration.

**A persona is a communication and alignment artifact.** A controlled experiment comparing a
persona system against an analytics system on identical data found personas afford **faster
task completion** for identifying users `[C]` [s255]. That is what it is for: making an
abstract segment concrete enough that a writer knows who they are addressing.

**A persona is not a prediction instrument.** Demographic and geographic bases are criticized
specifically for **failing to predict behaviour** `[C]` [s10]. Never use a persona to choose
a segment, size a market, or allocate budget. Those decisions come from Sections 2, 3 and 6
of the foundation.

| Use it for | Never use it for |
|---|---|
| Aligning writers on who they address `[C]` [s255] | Choosing which segment to serve `[C]` [s10] |
| Capturing the audience's real vocabulary `[C]` [s260] | Predicting purchase behaviour |
| Deriving the questions content must answer | Sizing a market or allocating budget `[C]` [s12] |

**Two rules that come straight from the evidence:**
1. **Build it from data, not assumptions.** Assumption-based personas are exactly what the
   persona literature criticizes itself for `[C]` [s257] [s256]. Data-driven construction is
   the corrective `[C]` [s252] [s254].
2. **Show your sources inside the artifact.** Transparency about how a persona was
   constructed measurably improves how it is received, because the construction is otherwise
   opaque `[C]` [s253]. This is why every section below carries evidence markers.

---

## The evidence-marker convention

Every claim inside the persona is tagged. This is the transparency requirement `[C]` [s253]
made operational, and it is what stops the artifact drifting into fiction.

- `[verified]` — stated on their site, in their docs, or in a review you can point to
- `[research]` — from the market or competitor research passes, with a URL
- `[inferred]` — a reasoned deduction from the above, defensible but unconfirmed
- `[assumption]` — a guess that needs validation, and belongs in Section 7 of the foundation

**A persona where most lines are `[assumption]` is a hypothesis.** Say so at the top rather
than presenting it as knowledge.

---

## Step 1 — Mine the language before writing anything

This is the load-bearing step and the one most personas skip. Customers describe needs "in
layman's terms" while businesses describe specifications, and bridging that gap requires
deliberate method `[C]` [s260]. Mining user-generated content is the established way to close
it `[C]` [s260] [s251].

Sources, in order of value:

1. **Their own reviews** — Google, Trustpilot, Yelp, G2, Capterra, app stores. The single
   richest source of unedited customer phrasing.
2. **Competitor reviews**, especially 2 and 3 star. Those name the unmet need precisely.
3. **Forums and Q&A** — Reddit, industry forums, Quora, Facebook groups, trade communities.
4. **Their own sales and support** — if the client will share inbound emails or call notes,
   this beats everything above.

Run it:

```
python .claude/skills/web-scraper/scripts/scrape.py --url "<review or forum URL>" --extract llm \
  --instructions "Extract verbatim customer quotes describing problems, frustrations, desired outcomes, and the words they use for the product category. Keep original wording. Do not paraphrase."

python .claude/skills/research/scripts/research.py --query "<category> customers complaints problems reddit forum" --depth deep --save
```

**Collect verbatim.** Paraphrasing destroys the artifact's entire value. If a customer wrote
"I just need someone to actually show up", that exact sentence is worth more than any summary
of it.

## Step 2 — Write the persona

One primary persona. Add a second only if the business genuinely serves two segments with
different vocabularies, and say why. Three or more is almost always a sign the target
customer section was never decided.

```markdown
# Audience Persona — <Client> — "<Short label>"

**Confidence:** <Grounded | Partial | Hypothesis>  ·  **Built from:** <sources, dated>

## In one line
<Who they are and what they are trying to get done, in plain language.>

## Situation
- Role / context: <...> [verified|research|inferred|assumption]
- The setup they are working in: <team size, tools, constraints> [...]
- What triggers them to go looking: <the event that starts the search> [...]

## What they are trying to get done
The job, in their words. Not the product category.
- Primary: <...> [...]
- Also true: <...> [...]

## What is in the way
- <Pain point, phrased as they would phrase it> [...]
- <...>

## How they decide
- What they compare: <...> [...]
- What makes them say no: <...> [...]
- Who else is involved in the decision: <...> [...]

## Their words  <- the section that makes this useful for search
**Verbatim quotes** (source and date each one):
> "<exact customer wording>" — <source>

**They say / they don't say:**

| They say | They never say | Note |
|---|---|---|
| <customer term> | <industry or spec term> | <why the gap matters> |

**Questions they actually ask**, grouped by intent:
- Informational: <...>
- Commercial investigation: <...>
- Transactional: <...>
- Post-purchase: <...>

## Where they are
- Where they search: <...> [...]
- Where they hang out: <communities, publications, channels> [...]
- Who they already trust: <...> [...]

## What this means for content
- Topics that map to real questions above: <...>
- The vocabulary to write in, and the terms to avoid.
- Formats and depth this audience actually consumes.

## Open questions
<Everything marked [assumption], as testable statements. These feed Section 7 of the
foundation.>
```

## Step 3 — Hand off to search and content

The persona is an input, not the finish line. **Do not do the SEO work here.**

`seo-advisor` owns the search mechanics on its own 320-source corpus: keyword research and
intent classification, AI search and AEO/GEO, entity SEO, and query fan-out. Cross-cite it,
never restate its numbers. The relevant mechanic for a persona is that AI engines expand one
prompt into many sub-queries, so the **question list in "Their words" is the highest-value
output of this artifact**: broad question coverage in the audience's own phrasing is what
survives fan-out.

| Hand the persona to | For |
|---|---|
| **seo-advisor** | Turning the question list into keyword clusters, intent mapping, and an AEO/GEO plan |
| **blog-writer** | Long-form articles answering the questions, in the audience's vocabulary |
| **content-engine** / **post-creator** | Social and multi-platform content, voice and pillars |
| **client-content-creator** | A full content package for the client's brand |
| **marketing-advisor** | Which channels to reach them on |

State the handoff. Do not silently start doing keyword research inside this playbook.

---

## Quality bar

Run these before delivering. Each maps to a real failure mode.

- **The verbatim test.** Are there real quotes with sources? If every quote is invented, this
  is fiction with a name on it `[C]` [s257].
- **The vocabulary test.** Does the "they say / they never say" table contain at least one
  genuine gap? If the customer words and the business words are identical, either you have
  not mined enough or the client already writes well. Verify which `[C]` [s260].
- **The competitor-swap test.** Swap in a competitor's customer. If the persona still reads
  true, it describes a category, not an audience.
- **The question test.** Could a writer produce ten articles from the question list without
  asking anything further? If not, the list is too thin to be useful for search.
- **The marker test.** Is every non-obvious line tagged? An untagged persona hides which parts
  are known and which are guessed, which is the transparency failure `[C]` [s253].
- **The demographics test.** If the richest section is age, location and job title, this is
  the weak kind of persona `[C]` [s10]. The language and questions sections should be the
  longest.

## What not to do

- **No stock photo, no invented name-and-backstory** presented as insight. A short label
  ("The overwhelmed practice manager") is enough. The "relatable person with a name, a face
  and a story" framing is practitioner convention `[P]`, and the fictional-profile criticism
  is documented in the research itself `[C]` [s257].
- **No invented quotes.** Ever. A quote with no source is the worst possible line in this
  document, because it looks like the strongest evidence in it.
- **No claim that the persona will lift traffic, rankings or conversion.** No evidence in this
  corpus supports that. The measured benefit is faster user understanding `[C]` [s255], and
  the vocabulary gap is established `[C]` [s260]; the search payoff is inferred, not proven.
- **No demographic detail that changes nothing.** If knowing their age does not change a
  single content decision, cut it.
- **No third persona** without a stated reason.
