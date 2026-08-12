# The Term-Gap Workflow

The free replacement for NeuronWriter or Surfer, plus the edit contract that stops the
optimization pass from quietly destroying the page.

This is the aruntastic Modern Optimization Workflow, kept because the corpus does not carry
it and its two distinctive moves are genuinely load-bearing: the body/heading split, and
the re-score verification that closes the loop.

---

## The loop

```bash
# 1. Measure
python scripts/terms.py --query "the target query" --url URL --out before.json

# 2. Edit under the contract below

# 3. Re-measure and report the delta
python scripts/terms.py --query "the target query" --url URL --refresh --out after.json
```

Step 3 is the part people skip and the part that makes it a process rather than advice. An
edit nobody re-measured is a claim.

**Cost:** the SERP is free when `seo-foundation` already cached that query, otherwise one
Serper credit. Fetching the ranking pages is free. Re-running is free.

---

## Reading the output

Two lists, and they are not interchangeable.

| Output | What it means | What you do |
|---|---|---|
| **Missing SECTION topics** | The ranking pages put this in a heading | You are missing a **section**. Consider whether it belongs, then write it. |
| **Missing BODY concepts** | The ranking pages discuss this in prose | You are missing a **point**. One or two sentences, where it fits. |

Collapsing these into one list is what produces pages with keywords stapled into
paragraphs. A concept the ranking set thought deserved its own H2 is a structural gap; a
concept they mention in passing is a sentence.

**Coverage score.** Percentage of the concepts used by most of the ranking set that your
page also uses. It exists so an edit can be verified as having changed something. It is not
a ranking prediction and it should never be shown to a client as one.

**Confidence.** Below four readable competitors the script says `low` and explains why.
Take that seriously - with two pages, "most competitors use this" and "both pages use this"
are the same statement.

---

## When the method does not apply

`terms.py` excludes platform and UGC results (Facebook, Reddit, YouTube, TripAdvisor,
Wikipedia) from the competitor set, because those are not documents you displace with
better on-page work.

If that leaves almost nothing, **that is the finding, not a failure**. A page one made of
social profiles and forum threads means there is little editorial content to out-cover, and
the lever is intent, the profiles themselves, or a different query. Say so and stop. Do not
lower the bar to manufacture a term list.

Live example: `renaissance faire springfield illinois` returned 9 results, of which 6 were
platform or UGC, 1 blocked, and 1 was the client's own page. One readable competitor. The
honest output was "this method does not apply to this query", and that was more useful than
a fabricated list would have been.

---

## The Revise-Don't-Rewrite contract

The failure mode when editing an existing page is not a bad edit. It is regeneration: asked
to improve a page, the natural default is to produce a new one that is smoother, blander,
and missing the specific first-hand detail that was the only thing making it worth reading.

So the edit is constrained. These are the working rules:

- **Revise, do not rewrite.** Modify the draft that exists. Do not produce a new article.
- **Integrate naturally.** A term earns its place by adding context. Anything that reads as
  inserted has failed, whatever it does to the score. If a sentence exists only to carry a
  term, delete the sentence.
- **Use heading terms for structural changes**, body terms for prose. The lists are
  separate for a reason.
- **Preserve tone, intent and core message.** Especially the first-hand parts. Those are
  what a rewrite smooths away and they are the hardest thing on the page to replace.
- **Set a readability target explicitly** if the audience needs one, rather than letting it
  drift. Note the corpus sets no threshold - `content.readability` reports the grade and
  never gates on it.
- **Then re-measure**, and report the delta honestly, including when it barely moved.

## What this workflow will not do

- **No frequency targets.** There is no "use this term 11 times". Frequency targets are how
  you get the over-optimization the helpful-content system catches, and the question is
  whether the page covers the concept, not how many times a string appears.
- **No word-count matching.** Competitor median length is reported as context. Padding to
  match it is exactly the pattern that gets caught.
- **No score shown to a client as a prediction.** Internally it verifies an edit. Externally
  it means nothing.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`, by the `index` field.
