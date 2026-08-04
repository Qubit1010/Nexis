# Review Rubric — auditing an existing strategic foundation

Review mode. The client already has a strategy, a business plan, a deck, or a set of
statements. The job is to say what is load-bearing, what is decoration, and what is missing,
then fix the pieces worth fixing.

**This rubric is ours.** There is no validated strategy-audit instrument in the corpus
`[C]` gap noted in `research-synthesis.md` Q8. It is assembled from the evidence below and
must be presented as a structured judgment, not a published scoring model.

**The evidence that justifies doing this at all:** formal strategic planning improves
financial performance in small firms, by meta-analysis `[C]` [s45]. Lead with that if the
client asks why a review is worth paying for.

---

## The lens

Rumelt's kernel is the review structure: a strategy needs a **diagnosis**, a **guiding
policy**, and **coherent action**. It is practitioner-tier `[P]` and must be labelled as a
framework, not evidence. It earns its place because it separates the three things clients
most often conflate, and because most weak strategies fail the first test: they have goals
where a diagnosis should be.

Two evidenced additions to the kernel:
- **Separate formulation from implementation.** Their success factors differ `[C]` [s9], so
  a strategy can be well made and badly run. Score them apart.
- **Check alignment.** Alignment is the bridge between formulation and implementation
  `[C]` [s47], and its absence is a distinct failure mode from a bad strategy.

---

## The scorecard

Seven rows. Each is **Strong / Workable / Weak / Missing**. Lead the deliverable with this
table, then justify every row below it.

| # | Dimension | Strong means |
|---|---|---|
| 1 | **Diagnosis** | Names the actual constraint, with evidence. Not a list of goals or a SWOT. |
| 2 | **Target customer** | Defined on behaviour and value, excludes someone, and is stable enough to act on `[C]` [s10] [s11]. |
| 3 | **Market understanding** | Sized bottom-up with visible assumptions, not a top-down number with an assumed share `[P]` [s94] [s74]. |
| 4 | **Competitive position** | Names real alternatives and the tradeoff being made against them. Not a logo grid. |
| 5 | **Value proposition** | One recognizable sentence, backed by something structural in the business, not a claim `[C]` [s15] vs [s20]. |
| 6 | **Business model coherence** | The revenue model, cost structure and target customer reinforce each other. The unit works. |
| 7 | **Coherent action** | Decisions and resource allocation follow from 1-6. Says what they will **not** do. |

**Scoring discipline.** Weak and Missing are different: Weak means present but not
load-bearing, Missing means absent. Do not soften. A scorecard where everything is Workable
tells the client nothing and is the most common way this deliverable fails.

**Calibration:** most real strategies score Weak or Missing on rows 1 and 7. Goals-instead-of-
diagnosis and no-stated-tradeoffs are the two dominant failure patterns. If you score a
document Strong across the board, re-read it looking for the choice it is avoiding.

---

## Reading order

1. **Find the diagnosis.** Read for a sentence that names what is actually in the way. If
   every candidate sentence is a target or an aspiration, row 1 is Missing, and that is the
   headline finding of the review.
2. **Test for real choices.** For each major claim, ask whether a competent competitor would
   disagree. "We will deliver quality and value" fails. If nothing in the document is
   contestable, there is no strategy in it.
3. **Trace one decision end to end.** Pick a resource allocation the client has actually
   made and check whether the strategy predicts it. This is the fastest test of row 7.
4. **Check the numbers.** Every figure: sourced, client-reported, or assumed? Unsourced
   confident numbers are the most common defect, and client-supplied projections should be
   treated as biased high `[C]` [s64].
5. **Check the fit between rows.** A premium value proposition with a volume cost structure
   is an incoherence worth more than any individual weak row.

---

## Output structure

```markdown
# Strategic Foundation Review — <Client>
*Reviewed: <what documents, dated>*

## Verdict
<the 7-row scorecard, then two or three sentences of plain judgment>

## What's working
<genuine strengths, specific. If there are none, say so rather than manufacturing one.>

## The critical gaps, ranked
<ranked by what most changes outcomes if fixed. Usually two or three, not seven.>

## Section by section
<per dimension: Current -> Problem -> Fix. Quote their own words when calling something
weak, so the judgment is checkable and not just an assertion.>

## Rewritten pieces
<only where the fix IS a rewrite: mission, UVP, target customer definition. Do not rewrite
what only needs evidence.>

## What to do next
<the single highest-leverage fix, then two supporting moves. Not a list of twelve.>
```

---

## Rules

- **Quote before you criticize.** Every Weak or Missing score cites their actual wording.
- **Rank, do not enumerate.** Twelve equally-weighted gaps is not a review, it is a list.
  Row 1 and row 7 usually dominate.
- **Separate "wrong" from "unevidenced".** A claim can be plausible and unsupported. Say
  which it is.
- **Do not import a strategy they did not choose.** Review the strategy in front of you
  against its own logic before proposing a different one. If you conclude the whole direction
  is wrong, that is a legitimate finding, but say it explicitly rather than quietly rewriting
  toward your own preference.
- **Do not use failure-rate statistics to create urgency.** The "70-90% of strategies fail"
  family is not established `[C]` [s41] [s49]. It is also the most tempting line in this
  entire deliverable. Refuse it.
- **A review is not a rebuild.** If more than four rows are Missing, stop and say the honest
  thing: there is not enough here to review, and the right move is `build` mode.

---

## Handing off to build mode

Switch when the scorecard shows five or more Missing, or when rows 1 and 7 are both Missing
and the rest are Weak. Say so directly: "There is not enough strategy here to audit. What
exists is a set of goals. I would rather build the foundation than score an absence." Then
run `build-playbook.md`, reusing whatever Section 0 facts the review already established.
