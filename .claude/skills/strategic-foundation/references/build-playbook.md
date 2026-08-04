# Build Playbook — from a thin client brief to a strategic foundation

The default mode. The client has no strategic foundation, or has fragments. This produces
one document, grounded in what was actually learned about their business and what the
research actually supports.

**The governing constraint:** every claim in the output traces to either a fact about the
client (with a source), a cited finding (with a tier), or a named assumption. Nothing else
is allowed in. A confident invention is worse than a gap, because the client cannot tell
which is which.

---

## Step 1 — Resolve the input

Partial input is enough. Do not interrogate before working.

| What the client gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / PPTX / XLSX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` written beside it |
| `.md` / `.txt` / pasted text | `Read` it, or use the paste inline |
| Business website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 12 --extract raw` |
| Name or one-line brief only | `python .claude/skills/research/scripts/research.py --query "<name> <industry hint>" --depth medium --mode entity` to find the site, then crawl it |

All of these run UNSANDBOXED. Prefer the site's about, services, pricing and team pages.
Stop when you have enough to describe the business; do not crawl the whole site by reflex.

**If you cannot find the business at all**, say so and ask for the URL. Do not invent a
plausible company.

## Step 2 — Research the market

Always, regardless of how good the client brief was. Three deep passes, saved:

```
python .claude/skills/research/scripts/research.py --query "<industry> market size growth <geo> 2026" --depth deep --save
python .claude/skills/research/scripts/research.py --query "<industry> competitive landscape main players <geo>" --depth deep --save
python .claude/skills/research/scripts/research.py --query "<industry> trends challenges 2026" --depth deep --save
```

Cite these with their URLs in the deliverable. They are live research, not part of the
locked `[sN]` corpus, so keep the two kinds of citation visually distinct: `[sN]` for the
methodology evidence, a plain URL for a fact about this client's market.

## Step 3 — Ask only what you cannot infer

Use `AskUserQuestion`, batched, one round, 2 to 4 questions maximum. Skip anything the
brief or the site already answered. The two that are almost never inferable:

1. **Who actually buys, and who is the worst-fit customer they have said yes to?** The
   second half surfaces the real segment boundary faster than the first.
2. **What do they believe makes them the right choice, and what would a competitor say to
   that?**

Add at most two more, only if genuinely load-bearing: current revenue model and rough
scale, or the constraint that matters most (cash, capacity, or a channel they cannot use).

If the client is not available to answer, proceed and mark each gap as an assumption in
Section 7. Do not stall the deliverable on questions nobody is going to answer.

## Step 4 — Write the document

```markdown
# Strategic Foundation — <Client>
*<one-line description of the business, in their language not yours>*
```

### 0. What we know, and how we know it

A table. This section is load-bearing and comes first for a reason: everything downstream
is only as good as this, and the client can immediately see which inputs are shaky.

| Fact | Source | Confidence |
|---|---|---|

- **Source** is the URL, the document name, or "client-reported".
- **Confidence** is High (verified in two places or primary), Medium (single source),
  Low (inferred).
- Client-reported figures are **never** promoted above Medium, per [s64] and [s67].
- End with an explicit **"What we could not establish"** list. That list is what Section 7
  turns into assumptions.

### 1. Mission, vision, values

Three short statements plus a line on what each one is *for*. Write them so a manager could
use them to settle an argument without escalating.

- Mission: what they do, for whom, and how value is created.
- Vision: the future state, specific enough to be wrong.
- Values: three to five, each phrased as an observable behaviour, not an abstraction.

**Honesty line, include it:** these earn their place through decision clarity. The link
between mission statements and financial performance is not established `[C]` [s58], though
vision does show an association with employee performance `[C]` [s2].

**Kill test:** swap in a competitor's name. If it still reads true, rewrite it.

### 2. Target customer

- The primary segment, defined on **behaviour and value**, not demographics `[C]` [s10].
- The job they are hiring this business to do.
- Where they currently go instead.
- **Explicitly: who this business should not serve.** A target customer section that
  excludes nobody has defined nothing.
- Note whether the segment is stable enough to build on `[C]` [s11], or flag it as untested.

### 3. Market landscape

- Size, built **bottom-up** from reachable accounts times realistic annual revenue, then
  cross-checked top-down `[P]` [s94].
- Show the arithmetic inline. Every multiplier gets a stated basis.
- TAM / SAM / SOM as nested scopes, with SAM and SOM carrying the story and TAM as context
  `[P]` [s74].
- Two or three trends that change the picture, each with a live source URL.

**Never** present a market size without its assumptions, and never assume a share
percentage.

### 4. Competitive position

- Three to five real competitors, direct and substitute.
- For each: the choice they have made, and what it costs them. Not a feature checklist.
- Where this business is genuinely different, and where it is at parity. Parity is fine and
  saying so builds credibility.
- Structural read using Five Forces `[C]` [s1] to name the binding constraint.

**Include the calibration:** industry structure explains roughly 19% of profit variance
against 32% for business-specific factors `[C]` [s50]. Point the client at what they control.

### 5. Unique value proposition

One sentence a customer would recognize, plus the evidence for it.

- What it is, who for, and against what alternative.
- The proof: what in the business actually makes it true (capability, cost structure,
  access, focus). If nothing does, **say so** and treat it as the central strategic problem
  rather than writing a better sentence.

**Where the evidence is contested, say it:** differentiation shows meta-analytic support for
financial performance `[C]` [s15] [s16], but perceived brand differentiation has been
directly challenged `[C]` [s20] and distinctiveness findings are mixed `[C]` [s19].
Differentiation in the offer and economics is the defensible kind; differentiation that
lives only in messaging is what the counter-evidence targets.

### 6. Business model

- Revenue model, cost structure, and the unit that has to work.
- Contribution per unit, with every input labelled as client-reported, sourced, or assumed.
- What has to be true for this to scale, and what breaks first.

**Calibrate the recommendation:** business model innovation relates robustly to performance
across 147 studies `[C]` [s28] and matters most early in the life cycle `[C]` [s3], but
reconfiguration breadth has an inverted U `[C]` [s27] and refining an existing model pays
off `[C]` [s25]. **Default to sharpening what exists.** Recommend reinvention only when the
diagnosis demands it, and say which finding is driving that call.

**Financial forecast rules, non-negotiable:**
- Structure and named assumptions only. **No invented client-specific revenue figures.**
- Any client-supplied projection is labelled client-reported and discounted, citing the ~22%
  average overshoot `[C]` [s64].
- Anchor survival framing on the ~78-80% one-year establishment rate `[C]` [s8], never on
  "90% of startups fail".
- Flag revenue volatility as a risk signal, not just revenue level `[C]` [s32].
- **No CAC, LTV, LTV:CAC or margin benchmarks.** They are not in the corpus. Give the client
  the formula and tell them we need their actuals.

### 7. Assumptions to validate

The honesty section, and the one that makes the document trustworthy. Every unknown from
Section 0 arrives here as a testable statement.

| Assumption | Why it matters | How to test it | Cost to test |
|---|---|---|---|

Rank by what would most change the strategy if wrong. Cheap tests first.

### 8. First 90 days

Three to five actions, sequenced. Each one either tests a Section 7 assumption or moves the
single biggest constraint named in Section 4. No generic advice.

### Companion artifact: the audience persona

After Section 2 is settled, offer the persona. It is written as a **separate document**, not
a subsection, because the people who use it (writers, SEO, AEO/GEO) are usually not the
people who read the strategy. Follow `persona-playbook.md`.

Section 2 decides **which segment**. The persona makes that segment **concrete enough to
write for**, and captures the vocabulary and questions that content and search need. Do not
collapse the two: using a persona to pick the segment is the error `[C]` [s10], and Section 2
must be settled first.

---

## Step 5 — Run the kill list, then deliver

Before showing it to anyone, run the whole document through `what-not-to-do.md`, especially:

- Every number resolves to `[sN]`, a live source URL, "client-reported", or a named
  assumption. **Any orphan number is a bug.**
- No refused claim ("90% of startups fail", "70% of strategies fail", an LTV:CAC target)
  has crept in.
- The mission and UVP fail the competitor-swap test.
- Section 7 is not empty. If it is, you have overclaimed somewhere.

Save as markdown. Offer a Google Doc or PDF only if asked; neither is built by default.

---

## Scaling the work

- **Thin brief, no URL, no client access:** the document is mostly Section 0 gaps and
  Section 7 assumptions. That is a legitimate and useful output. Say plainly that it is a
  hypothesis set awaiting validation, not a finished foundation.
- **Rich input (existing docs, site, and client answers):** all eight sections carry real
  weight and Section 7 shrinks.
- **The client only wants one section:** that is `section` mode. Write it in full with its
  Section 0 evidence and its assumptions, and skip the rest.
