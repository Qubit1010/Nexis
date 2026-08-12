# The Report

`client-projects/<slug>/10-seo-onpage.md`, sitting after `09-seo-foundation.md`.

The shape is `course/20`'s four-part output, expanded only where a client deliverable needs
more than a training exercise. The four parts are the deliverable. Everything else is
supporting material.

An audit that lists forty problems is the standard output of an automated tool, and it is
exactly why tool exports do not sell. **The judgment is what is being bought.**

---

## Template

```markdown
# On-Page Audit - <Client>

**Confidence: <Full | Partial>.** <what was measured, what was not, and on what date>
**Built from:** <the upstream files, the URLs audited, the counts - "18 pages crawled,
9 measured in depth, 1 term-gap analysis">
**Working artifact:** <link to the Sheet, with its six tab names>

---

## 0. What we know, and how we know it

| Fact | Source | Confidence |
|---|---|---|
| ... | measured / [sN] / assumption | ... |

### What we could not establish
- **Search Console is not connected.** <the export steps, and what it would change>
- ...

---

## 1. The diagnosis

<One line. It has to name what is actually wrong.>

---

## 2. The three highest-impact fixes

### 1. <fix>
**Evidence:** <the measurement, the report, the SERP>
**Fix:** <what to do, concretely>
**Expected effect:** <honest, including when it is small>
**Effort:** <hours or a size>

### 2. ...
### 3. ...

---

## 3. What is fine

<Genuinely useful and almost always omitted.>

---

## 4. The structural question

<If there is one. A decision the owner has to make, not a task you can hand them.>

---

## 5. Findings by area

<Only the areas with something to say. Ten headings with "nothing found" under eight of
them is padding.>

---

## 6. The first 90 days

| When | What | Why it is in this order |
|---|---|---|

---

## What we could not establish

<Repeated from section 0, because it belongs at both ends of the document.>

## Handoff

| Hand this to | For |
|---|---|
```

---

## Section 1 is the whole document

A diagnosis names the mechanism. A summary lists symptoms.

| Not a diagnosis | A diagnosis |
|---|---|
| "Several SEO issues were found." | "The content is fine, the titles are filing labels and the pages are orphaned." |
| "Meta descriptions need improvement." | "Nine pages rank on page two and none of them have a reason to be clicked." |
| "The site has technical problems." | "Your service pages and your blog are targeting the same six queries, so each is capping the other." |

Test it: could this sentence be copied onto a different client's report without changing?
If yes, it is not a diagnosis.

---

## Section 2: three, and why three

Not four, not twelve. The constraint is what forces the ranking, and the ranking is the
value. `push_sheet.py` blocks a write with more than five findings marked "this week" for
this reason.

Each fix carries evidence that points at something checkable - a measured byte count, a
Lighthouse audit id, a SERP, a crawl output. "Best practice suggests" is not evidence.

**Be honest about the expected effect, including when it is small.** "This will recover
maybe 5 to 10% of the clicks you are already earning impressions for" is a credible
sentence. "This will dramatically improve your rankings" is not, and a client who has been
sold that before will recognise it.

---

## Section 3 exists for two reasons

It tells the reader you looked rather than pattern-matched, and it stops them changing
something that works. It is also where the floor-versus-lever distinction gets stated:
if Core Web Vitals pass, say they pass and say that no further work there is worth buying.

---

## Client-facing voice

- Translate the jargon. "LCP" means nothing; "the biggest thing on the screen takes 4.1
  seconds to appear on a phone" means something.
- Lead with the number where one was measured. "Your hero image is 412KB and can be 71KB"
  beats "images should be optimized".
- Never mention NexusPoint or Aleem inside the report. It is the client's document.
- No emojis. No em dashes in body text; headings may use them.
- Every number resolves to a measurement made here, an `[sN]` citation, or a named
  assumption. If it does none of those, cut it.

---

## Before shipping

Run `what-not-to-do.md` over the whole thing, then three checks:

1. **Is section 1 a diagnosis or a summary?**
2. **Does section 3 exist and say something specific?**
3. **Is every unknown named, Search Console first?** Burying it makes the rest of the
   document look more certain than it is.

Then report the Serper credits actually spent.
