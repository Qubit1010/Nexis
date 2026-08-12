# The deliverable

Written to `client-projects/<slug>/12-seo-authority-ai.md`, numbered to sit after
`11-seo-technical.md`.

The shape follows the family: a one-line diagnosis, three prioritized fixes, what is fine, and
the structural question. Not forty findings. An audit that lists everything is the standard
output of an automated tool, and it is why tool exports do not sell.

**One structural difference from the siblings:** section 2 comes before the fixes. Retrievability
is a precondition, and if it fails, sections 4 to 7 are theoretical. The report has to say that
where the reader hits it, not in a caveat at the end.

---

## Template

```markdown
# Authority and AI Visibility - <Client>

**Confidence: <Full | Partial>.** <what was sampled, at how many runs, on what date>
**Built from:** <which of 07-11 existed, N pages, M prompts x R runs x E engines>
**Working artifact:** <Sheet link> - 6 tabs.
**What this cost:** <Serper credits, Apify USD - or "nothing was sampled">

## 0. What we know, and how we know it
Fact | Source | Confidence table. Then the gap list, Search Console first.

## 1. The diagnosis
One line, naming the mechanism. If it could be pasted onto another client's report,
it is not a diagnosis.

## 2. Can they retrieve you at all
The tier-1 answer, before anything else.
Bot | Declared | Recommended | Effect if wrong.
Then Bing indexation, then the JS-rendering cross-reference.
If this section is bad, say here that sections 4-7 are theoretical.

## 3. The three highest-impact fixes
Each: Evidence / Fix / Expected effect (honest, including when small) / Effort.

## 4. AI visibility, measured
The distribution, never a point estimate.
"Cited in 2 of 3 ChatGPT runs", never "67%".
Separate: named, cited, and who was cited instead.
If nothing was sampled, this section says "not sampled" and states what it would cost.

## 5. Entity identity
Wikidata Q-number, KGMID, Entity Home, sameAs, description consistency.
Framed as infrastructure with a weeks-to-months lag, not a quick win.

## 6. Mentions and authority
Platform count against the 4+ threshold. The reclamation queue as a work list.
The honest link position, in these words: what could not be measured, why, and why
mentions are not a consolation prize.

## 7. Local
Three surfaces separately, primary category first.
Or one line: "not applicable, recorded so nobody implements it later."

## 8. What is fine
Named explicitly. It is what makes the failures credible.

## 9. The structural question
One, if there is one.

## 10. The next 90 days
course/42's roadmap adapted to what was found. Sequenced by the funnel, not by ease.

## What we could not establish
Every unknown with its manual route.

## Handoff
Which sibling skill owns what comes next.
```

---

## The rules that carry the design

**Never render a citation rate as a bare percentage.** "Cited in 2 of 3 runs" is the only
permitted format. A percentage from three samples implies a precision that does not exist, and at
2 of 3 the 95% interval is [0.208, 0.939].

**Separate the three negatives.** "Not cited", "not sampled" and "not retrievable" are different
findings with different fixes. Collapsing them is how this report would lie.

**Separate named from cited.** Being recommended by name while a third party gets the link is a
specific, fixable finding, not a flat failure.

**Tag the tier on every borrowed number.** `[peer-reviewed]` in this tier means Princeton and
nothing else. r = 0.664 is `[practitioner, correlational]` and is never stated as causal. Map-pack
weights are `[practitioner, modeled estimates, not disclosed weights]`.

**Never quote 58% as an average** - it is a ceiling. **Never quote the 520% photos figure** at
all. **"Under 1% of referrals today, rising fast"** is the defensible AI-traffic line.

**Translate the jargon.** "Query fan-out" means nothing to a client. "The engine quietly asks
itself eight follow-up questions and your site answers two of them" does.

**Client voice.** No emojis. No em dashes in body text. Never mention NexusPoint or Aleem - it is
the client's document.

---

## The 90-day roadmap, sequenced

Adapted from course/42. Order is by dependency, not by ease.

| Window | Focus | Typical items |
|---|---|---|
| **Days 1-30** | Retrievability and truth | Fix any bot inversion. Submit to Bing Webmaster Tools and IndexNow. Enable the measurement stack: GA4 14-month retention first (it is not retroactive), GSC-GA4 link, the AI channel regex. Capture the citation baseline at 3+ runs. |
| **Days 31-60** | Entity and extraction | Wikidata entry, Organization `sameAs`, Entity Home `@id`. Rewrite the top 3-5 pages with the three Princeton modifiers. Answer the unanswered PAA questions. |
| **Days 61-90** | Mentions and authority | Reclaim the unlinked mentions. Reach 4+ platform presence with one consistent description. Re-sample at the same prompt set and run count, and compare distributions, not point estimates. |

**Set the expectation honestly.** Entity recognition is weeks to months. Foundation work shows
minimal traffic movement in months 1-3. Never guarantee a ranking or a citation.
