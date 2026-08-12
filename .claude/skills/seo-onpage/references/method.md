# The Method

Phases 0 to 9, in order. The order is `course/20`'s impact order, not a checklist order:
find the biggest problems first so that running out of time still leaves you with the ones
that matter.

The satisfying fixes - rewriting titles, tidying alt text - sit in the middle. Starting
there is the most common way to spend a day making a page that targets the wrong query more
clickable.

---

## Phase 0 - Resolve the inputs

Work out what you were actually given, and find everything already known about this client.

| Input | Command |
|---|---|
| A client-projects slug | Read `client-projects/<slug>/` - `07-strategic-foundation.md`, `08-audience-persona.md`, `09-seo-foundation.md` |
| A live URL | `python scripts/fetch_page.py URL` |
| A whole site | `python scripts/links.py --site URL --max-pages 100` |
| A markdown draft | `python scripts/onpage.py --draft path.md` |
| A Google Doc | `gws docs documents get --params '{"documentId": "ID"}'` |
| A PDF / DOCX | `python .claude/skills/to-markdown/scripts/convert.py <file>` |
| A business name only | `research` skill to find the site, then treat as a live URL |

This is the same resolution table `seo-foundation` and `strategic-foundation` use, on
purpose. A client should not have to explain themselves twice.

**Three things to establish before anything else:**

1. **Is there a keyword map?** `09-seo-foundation.md` and its Sheet carry the
   cluster-to-URL mapping. Without it, phase 3's intent match and cannibalization findings
   are inferred from the SERP rather than known, and the report has to say so. Offer to run
   `seo-foundation` first.
2. **Is there Search Console access?** Almost always no. Ask anyway - if they can export
   the Performance report, `inventory.py --gsc-csv` will merge it and half the unknowns
   become knowns.
3. **Live page or draft?** Draft mode skips `lighthouse.py`, `links.py` and the live half
   of `media.py`. Say which checks did not run rather than letting their absence read as a
   pass.

---

## Phase 1 - Orientation

The phase people skip, and the one that decides whether the audit produces a diagnosis or a
list.

- What does this site sell, and to whom? One sentence. If you cannot write it from the
  homepage, that is the first finding.
- Rough page count: `python scripts/links.py --site URL --count-only`, or `site:domain.com`
  if the site blocks crawling.
- **Identify the 5 to 10 pages that matter commercially.** Not the 200 pages. These are the
  pages the business would miss if they vanished: the money pages, and the top-of-funnel
  content that feeds them.

Everything downstream runs against that shortlist. Auditing 200 pages equally is how you
end up with forty findings and no idea which three matter.

Present the shortlist before proceeding. If the client disagrees about which pages are
commercial, they are right and you are wrong, and it is cheap to find out now.

---

## Phase 2 - Fetch and measure

```bash
python scripts/fetch_page.py URL                       # raw HTML, whole, cached
python scripts/onpage.py --url URL --primary-keyword "..." --out page.json
python scripts/lighthouse.py URL --strategy mobile --out lh.json
```

`onpage.py` runs every check in `checks.md` and returns one row each. `lighthouse.py` adds
the free Lighthouse SEO category - 14 audits Google runs for you, including several this
skill would otherwise have to approximate.

Read the `verdict` distribution before reading individual rows. A page with thirty `pass`
and two `fail` has a metadata problem. A page with fifteen `review` has a content problem
and the script cannot help you with it.

**`--primary-keyword` is not optional in practice.** Without it the structural checks still
run but the relevance checks degrade to `review`, and you lose the ability to say whether
the structure is about the right thing.

---

## Phase 3 - Intent match and cannibalization

The two checks that outrank everything below them, and neither is scriptable.

**Intent match.** For each priority page, search its main query and look at what actually
ranks. Does this page's *type* match the page type on page one? A service page competing
against ten listicles is not a title problem, and no amount of on-page work fixes it. The
options are to change the page type, target a different query, or accept the position.

Pull the intent from `09-seo-foundation.md`'s Keyword Map when it exists rather than
re-deriving it. `seo-foundation/references/intent-taxonomy.md` owns the six-intent
classification; do not re-litigate it here.

**Cannibalization.** Two pages fighting each other is worse than either page's individual
problems.

- From the keyword map: does any URL appear against two clusters? That is the finding, and
  `push_sheet.py` will block the write until it is resolved.
- From the crawl: `links.py` reports pages whose titles and H1s overlap heavily.
- From Search Console, if connected: filter by top query and check whether several URLs
  pick up impressions for the same one. Without GSC this half returns `not connected`.

Resolution order, and it is an order: **Consolidate** (merge into the strongest page, 301
the losers to it - never to the homepage, an irrelevant redirect is a soft 404) beats
**Differentiate** (make them genuinely target different intents) beats **Prune**.

---

## Phase 4 - Content quality and the term gap

The substance. Read the top 3 pages properly - actually read them, not the extracted rows.

Four questions per page, and `onpage.py` gives you the raw material for each:

1. Do the first 40 to 60 words answer the query?
2. Is there evidence - a concrete number, a named source, something first-hand?
3. Is there padding - a section that restates the one before it, a definition of something
   obvious?
4. **Would a reader stop searching after this page?** The other three serve this one. If
   the answer is no, nothing else on the page matters.

Then the term gap:

```bash
python scripts/terms.py --query "primary query" --url URL --out terms.json
```

This is the free replacement for NeuronWriter or Surfer. It reads the live top 10 (free if
`seo-foundation` already cached that SERP), fetches each result, and reports the terms and
concepts those pages cover that this one does not - split into **body terms** and **heading
terms**, because they get treated differently. Full procedure and the edit contract are in
`terms-workflow.md`.

The output is coverage, not a keyword quota. "The top 3 all explain X and this page never
mentions it" is a real finding. "Add the phrase X eleven times" is not.

**Checkpoint here.** Write the one-line diagnosis and present it before writing any
replacement metadata. Everything from phase 5 on is aimed at the problem you just named,
and if the name is wrong, the aim is wrong.

---

## Phase 5 - Titles, meta descriptions, headings

Now the fast wins, and only now.

Write the replacements, do not just flag the failures. The deliverable on the Metadata tab
is current-versus-proposed, paste-ready. A finding that says "title is 78 characters" makes
the client do the work; a finding that hands them the 56-character replacement does not.

Title formulas by intent (`course/11`):

| Intent | Shape |
|---|---|
| Informational | `Primary Query: What It Is and How It Works` |
| Commercial | `Best [thing] for [audience] in 2026` or `X vs Y: Which for [use case]` |
| Transactional | `[Service] in [Location] \| [Brand]` |
| Comparison | `X vs Y vs Z: [dimension] Compared` |

Keyword inside the first 40 characters, whole title 50-60, and check that title, H1 and
first paragraph tell the same story - that agreement is the defence against Google
rewriting your title.

Headings: fix hierarchy skips in CSS rather than by demoting a heading, phrase roughly a
third as real questions sourced from People Also Ask, split anything much over 200 words,
and remove backward dependencies so each section can be lifted out on its own.

---

## Phase 6 - Internal linking and E-E-A-T

```bash
python scripts/links.py --site URL --priority-pages pages.txt --out links.json
```

Four outputs, in descending order of how much they usually matter:

1. **Opportunities** - pages that mention a topic and do not link to the page that owns it.
   This is the highest-yield finding in the whole audit and it usually surfaces dozens.
2. **Orphans** - zero inbound internal links. Link them or remove them; there is no third
   option.
3. **Click depth** - anything commercial more than 3 clicks from home.
4. **Anchors** - "click here", "read more", and any anchor repeated at scale.

Then E-E-A-T, which is mostly reading rather than running: named author with a real bio,
HTTPS, a genuine About page, working contact details that are not only a form, and at least
one honest acknowledgment of a limitation. Then run the six questions in `checks.md` §7.
Most pages fail three or more, and that conversation is worth more than the automated rows.

---

## Phase 7 - Media

```bash
python scripts/media.py --url URL --max-images 30 --out media.json
```

Every finding here is a measured byte count with a measured saving, because "optimize your
images" is advice a client has already ignored twice and "your hero is 412KB and can be
71KB" is not.

Priority order: the LCP image first (weight, format, not lazy-loaded, `fetchpriority`),
then explicit width and height on everything (one line of HTML, removes an entire class of
layout shift), then alt text, then filenames going forward only.

Video: hosted on YouTube rather than the client's server, and the transcript published on
the page. The transcript is the highest-value and most-skipped action in the area.

---

## Phase 8 - Inventory and tracks

Only in site mode, and only when the site is big enough to have decay.

```bash
python scripts/inventory.py --site URL --gsc-csv export.csv --out inventory.json
```

Every URL gets exactly one track: **keep**, **update**, **merge**, or **remove**. No
blanks - a blank means the decision was avoided, and avoided decisions are why the site has
300 thin pages.

Without Search Console the clicks and impressions columns come back `not connected`, and
track assignment leans on internal links, last-update date and cluster membership instead.
Say so. Full procedure in `refresh-tracks.md`.

Deleting pages to improve rankings feels wrong and is frequently correct: thin content in
one section suppresses good content elsewhere on the same domain `[practitioner]`.

---

## Phase 9 - Ship

```bash
python scripts/push_sheet.py --payload payload.json --validate-only
python scripts/push_sheet.py --payload payload.json --title "On-Page Audit - Acme"
```

Then write `client-projects/<slug>/10-seo-onpage.md` using the template in
`report-structure.md`.

Before delivering, run `what-not-to-do.md` over the whole thing. Then three final checks:

- **Is section 1 a diagnosis or a summary?** "Several SEO issues were found" is a summary.
  "The content is fine, the titles are filing labels and the pages are orphaned" is a
  diagnosis.
- **Does section 3 exist?** What is fine is almost always omitted and it is what proves you
  looked rather than pattern-matched. It also stops the client breaking something that
  works.
- **Is every unknown named?** Especially Search Console. Burying it makes the rest of the
  document look more certain than it is.

Report the Serper credits actually spent.

---

## The Revise-Don't-Rewrite contract

Whenever you edit an existing draft or page rather than writing a new one - phases 4, 5 and
any optimize-mode run - the failure mode is not a bad edit. It is regeneration: asked to
improve a page, the natural default is to produce a new one that is smoother, blander, and
missing the specific first-hand detail that was the only thing making it rank.

So the edit is constrained:

- **Revise, do not rewrite.** Modify the draft that exists. Do not produce a new article.
- **Integrate naturally.** Terms earn their place by adding context. Anything that reads as
  inserted has failed, regardless of what it does to a score.
- **Structural changes use heading terms**, not body terms. The two lists are separate for
  a reason.
- **Preserve tone, intent and core message.** Especially the first-hand parts, which is
  exactly what a rewrite smooths away.
- **Then re-measure.** Re-run `terms.py` and `onpage.py` and report the delta. An edit
  nobody verified is a claim, not a fix.

That closing loop - measure, edit under constraint, re-measure - is the whole method in
miniature.

Citations `[sN]` resolve via `seo-advisor/_research/sources.json`, by the `index` field.
