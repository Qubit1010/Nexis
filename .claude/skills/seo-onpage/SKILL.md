---
name: seo-onpage
description: >
  Use to OPTIMIZE or AUDIT the on-page and content layer of a client's pages, a whole site,
  or an unpublished blog draft. This is the execution skill that produces the artifact and
  the fixes, not the advice skill. Triggers on: on-page SEO, on page optimization, optimize
  this page, optimize this post, "is this page optimized", on-page audit, content audit,
  SEO audit of a page, title tag, title tags, meta description, meta descriptions, SERP
  snippet, "rewrite my titles", "my CTR is low", heading structure, H1, H2, heading
  hierarchy, "too many H1s", content structure, URL slug, slug, "should I change this URL",
  site navigation, breadcrumbs, orphan page, orphan pages, content quality, thin content,
  "is my content good enough", "why isn't this page ranking", helpful content, topical
  authority, pillar page, content cluster, cluster pages, internal linking, internal links,
  anchor text, link depth, "nothing links to this page", image SEO, alt text, image
  optimization, image compression, WebP, hero image weight, video SEO, transcripts, E-E-A-T,
  EEAT, author bio, "how do I show expertise", trust signals, content refresh, refresh this
  post, update old content, content decay, "traffic is dropping on old posts", consolidate
  pages, prune content, delete pages, content inventory, "what should I do with these 200
  pages", answer blocks, extractable answers, FAQ schema, HowTo schema, JSON-LD on a page,
  "optimize this for AI search", "make this page citable", content optimization terms, "what
  am I missing versus page one", term gap, "what do the top results cover that I don't".
  Works from a live URL, a whole site, a markdown draft, or a client-projects slug, and
  consumes the keyword map from seo-foundation when one exists. Measures rather than
  asserts: parses real HTML locally, runs Lighthouse's free SEO audits, computes actual
  image savings, and extracts the term gap against the live top 10. Outputs a 6-tab Google
  Sheet (Page Audit, Findings, Metadata, Content Inventory, Internal Links, Media) plus a
  written report built as a one-line diagnosis and three prioritized fixes, not forty
  findings. Says "not connected" rather than inventing Search Console data. Scope is
  deliberately Tier 2 only - on-page and content. For SEO THEORY, benchmarks, diagnosis or
  the course ("is SEO dead", "teach me SEO") use seo-advisor. For KEYWORD research, intent
  classification or the keyword map use seo-foundation. To WRITE the article use
  blog-writer. For a prospect-facing sales audit with a hook email use
  website-audit-system. Technical, off-page and AI-search execution are out of scope.
argument-hint: [URL, client-projects slug, or a draft path - optionally "audit" / "optimize" / "refresh"]
---

# SEO On-Page

Optimizes or audits the **content layer** of a page or a site: whether it answers the query
it targets, whether the metadata earns the click, whether the structure survives retrieval,
whether anything links to it, and what to do with the pages that no longer earn their place.

Two jobs:

1. **Optimize** a page or a draft: produce the corrected on-page layer, ready to paste.
2. **Audit** a page or a site: produce a prioritized diagnosis of what to fix and in what
   order.

The output is a working artifact, not a memo: a 6-tab Google Sheet plus a written report.

## Where this sits

`seo-advisor` knows things. This skill does things. Same split as `marketing-advisor` to
`sales-playbook`, and `seo-advisor` to `seo-foundation`.

```
seo-foundation      ->   seo-onpage        ->   blog-writer / content-engine
  what they search        whether the page        the next article
  and which page wins     actually delivers
```

`seo-foundation` is Tier 1 and says so in its own frontmatter. It ends at the keyword map:
this cluster belongs to this URL. This skill picks that URL up and asks whether it is any
good. It is Tier 2 of the course - sections 11 to 20 - and nothing else.

## Operating principles (read once)

- **Measure, do not assert.** "This hero image is too heavy" is worthless. "This hero is
  412KB; re-encoded to WebP at the same visual quality it is 71KB, a 341KB saving on the
  LCP element" is a finding someone can act on. Every script here exists to turn a claim
  into a number.
- **Audit in impact order, not checklist order.** Intent, then cannibalization, then
  content, *then* the metadata. The fast satisfying fixes sit in the middle and it is very
  tempting to start there. Starting there means rewriting the titles on a page that targets
  the wrong query, which is effort spent making a wrong thing more clickable.
- **Three findings beat forty.** An audit that lists everything is the standard output of
  an automated tool, and it is why tool exports do not sell. Rank ruthlessly, say what is
  fine, and name the one structural question if there is one.
- **Distinguish floors from levers.** Core Web Vitals, HTTPS and mobile are floors. Failing
  hurts; exceeding buys nothing. Telling a client already passing LCP to chase 1.1 seconds
  is telling them to spend money for no return.
- **Say what you could not establish.** There is no Search Console access here (verified:
  `gws` has no Search Console service and no credential exists). Anything that needs CTR,
  impressions or decay data comes back `not connected` with the export steps, never a
  guess. Without GSC you are inferring rather than diagnosing, and the report has to say so.
- **Scripts propose, you decide.** The scripts count, parse and measure. Whether the first
  60 words actually answer the query, whether a section is padding, whether the intent
  matches - those are judgment and stay with you. A check that needs judgment returns
  `review` with the evidence attached, never a fabricated `pass`.
- **Do not change URLs.** The default verdict on any live URL is note-only. A slug that
  isn't quite the keyword is not a reason to break every inbound link. Changing needs one
  of the four named exceptions in `references/checks.md`.

## Boundaries / handoffs

| Hand off to | For |
|---|---|
| **seo-advisor** | Theory, benchmarks, diagnosis of a symptom ("traffic dropped, why"), the 42-section course, and anything technical, off-page or AI-search strategy. It owns the cited 320-source corpus. Cross-cite it, never restate its numbers as if they were measured here. |
| **seo-foundation** | Keyword research, intent classification, SERP-overlap clustering, and the keyword-to-URL map. This skill consumes that map; it does not build it. If no map exists, offer to run it first. |
| **blog-writer** | Writing the actual article. This skill validates and fixes an article's on-page layer; it does not write the prose in Aleem's voice. |
| **website-audit-system** | A prospect-facing sales audit with a hook email, or a Firecrawl crawl plus PageSpeed scored across UX/SEO/Performance/Conversion. That is the cold-outreach motion. This is a paid client deliverable. |
| **content-engine** / **post-creator** | Turning the cluster plan into a running content system. |
| **research** / **web-scraper** | Competitor content extraction beyond the top 10, and target discovery. This skill calls both directly. |

State the handoff when you make it. Do not silently stop.

## Context to load first

Read `references/method.md` first - it is the pipeline and is near-always what you need.
Then load the mode reference below. **Max 3 reference files per invocation.**

---

## Mode Detection

| Mode | Trigger keywords | Load |
|---|---|---|
| **audit** (default) | "audit this page/site", "on-page audit", "why isn't this ranking", a bare URL, a client slug | `method.md` + `report-structure.md` |
| **optimize** | "optimize this page", "rewrite my titles", "fix this post", a draft path, or blog-writer handing over a draft | `method.md` + `checks.md` |
| **terms** | "what am I missing versus page one", "term gap", "what do the top results cover", "content score" | `terms-workflow.md` |
| **clusters** | "topical authority", "pillar page", "build a content cluster", "what supporting posts do I need" | `clusters-and-links.md` |
| **links** | "internal linking", "orphan pages", "nothing links to this", "anchor text", "link depth" | `clusters-and-links.md` |
| **media** | "image SEO", "alt text", "compress these images", "hero is too heavy", "video SEO", "transcripts" | `media.md` |
| **refresh** | "content decay", "update old posts", "consolidate", "prune", "what do I do with 200 pages", "content inventory" | `refresh-tracks.md` |
| **review** | "review this on-page work", "is this audit any good", an existing audit or checklist is supplied | `review-rubric.md` |

If the ask spans two modes, do the primary first and offer the second. A request that
starts as one page usually wants the site - check before crawling 200 URLs.

---

## Workflow

The full pipeline is in `references/method.md`. Phases 0-9, in course/20's impact order.
Summary:

| Phase | What happens | Who does it |
|---|---|---|
| 0 | Resolve inputs - URL, draft, or slug; find the keyword map and persona | you |
| 1 | Orientation - what is sold to whom, page count, GSC status, the 5-10 pages that matter | you |
| 2 | Fetch and measure every target page | `fetch_page.py` + `onpage.py` + `lighthouse.py` |
| 3 | Intent match and cannibalization against the keyword map | you |
| 4 | Content quality, evidence density, and the term gap | `terms.py` + you |
| 5 | Titles, meta descriptions, headings - write the replacements | you |
| 6 | Internal linking, orphans, click depth, E-E-A-T | `links.py` + you |
| 7 | Media weight, format, alt, transcripts | `media.py` |
| 8 | Inventory and tracks - keep, update, merge, remove | `inventory.py` + you |
| 9 | Ship the Sheet and the report | `push_sheet.py` + you |

**Phase 1 is not optional and not skippable.** Phases 2 onwards measure things; phase 1 is
what tells you which things are worth measuring. Auditing all 200 pages equally is how you
end up with forty findings and no diagnosis.

**Checkpoint after phase 4.** Present the one-line diagnosis before writing any
replacement metadata. If the diagnosis is wrong, every fix downstream is aimed at the wrong
problem, and this is the cheapest place to catch it.

**Cost.** Phases 2, 4 and 6 are free - local parsing, free Google Autocomplete, free
Lighthouse, and cached SERPs. `terms.py` spends one Serper credit per query only if that
query is not already in `seo-foundation`'s cache. Say the number before spending it.

## Deliverables

**A 6-tab Google Sheet** via `push_sheet.py` - schemas in `references/sheet-schemas.md`.

**A markdown report** at `client-projects/<slug>/10-seo-onpage.md`, numbered to sit after
`09-seo-foundation.md`. Structure is course/20's four-part output, expanded - full template
in `references/report-structure.md`:

```
0. What we know, and how we know it   (Fact | Source | Confidence, then the gap list)
1. The diagnosis                       (one line, and it has to be a diagnosis)
2. The three highest-impact fixes      (each with evidence and an honest expected effect)
3. What is fine                        (almost always omitted, and it is what proves you looked)
4. The structural question             (if there is one)
5. Findings by area                    (the ten Tier 2 areas, only where there is something to say)
6. The 90-day sequence
What we could not establish
Handoff
```

Google Doc on request via `content-engine/scripts/save_content.py` (multi-tab: one tab per
area plus a summary tab). It strips smart quotes and em dashes across the whole payload and
flattens markdown links to bare text, so keep URLs in the Sheet, not in Doc-bound prose.

---

## Scripts

All run unsandboxed (they need real network). Keys come from the repo `.env` automatically.
Use bare `python` - it resolves to 3.12. **Not `py -3`**, which is a different, near-empty
3.14 install on this machine.

```bash
python scripts/fetch_page.py URL [--refresh] [--headers]        # raw HTML, whole, cached
python scripts/onpage.py --url URL --primary-keyword "..."      # the analyzer
python scripts/onpage.py --draft post.md --primary-keyword "..."  # the blog-writer path
python scripts/lighthouse.py URL [--strategy mobile]            # free SEO + a11y + perf audits
python scripts/terms.py --query "..." --url URL                 # term gap vs the live top 10
python scripts/links.py --site https://acme.com [--max-pages 100]  # graph, orphans, depth
python scripts/media.py --url URL [--max-images 30]             # measured image savings
python scripts/inventory.py --site https://acme.com [--gsc-csv export.csv]
python scripts/push_sheet.py --payload payload.json --validate-only   # no title needed
python scripts/push_sheet.py --payload payload.json --title "On-Page Audit - Acme"
```

**Always pass `--primary-keyword`.** Without it `onpage.py` can check structure but not
whether the structure is about the right thing, and half the checks degrade to `review`.

Every script has `--selftest`, and every one of them actually implements it. The
fixture-based ones (`onpage`, `terms`, `inventory`, `push_sheet`) prove the logic without
network. The live ones (`fetch_page`, `lighthouse`, `media`, `links`) exist to distinguish
"the upstream endpoint changed" from "this page genuinely has no images", which look
identical otherwise.

**The cache is what makes iteration free.** Pages are cached in `.cache/pages/` keyed on URL
only, and `terms.py` reads `seo-foundation`'s existing `.cache/serp/`. Re-running the whole
audit after a fix costs nothing. Pass `--refresh` only when you want fresh bytes.

**Two `.env` naming faults to know about, not silently patch:**

- `PAGESPEED_API_KE` is missing its trailing `Y`. `lighthouse.py` reads both spellings so it
  works either way, but `website-audit-system/scripts/pagespeed.py` reads only the correct
  name and has therefore been running on Google's anonymous quota. Tell Aleem; do not edit
  `.env` without asking.
- The Jina key is `JINA_AI_API_KEY`, not `JINA_API_KEY`.

---

## Edge Cases

| Scenario | Action |
|---|---|
| No Search Console access | The normal state here, and it caps what can be concluded. CTR, impressions, decay and cannibalization-by-impressions all return `not connected`. Print the export steps, offer `inventory.py --gsc-csv`, and say plainly in the report that this half is inferred. Never estimate a click number. |
| No keyword map exists | Intent match and cannibalization are guesses without one. Offer to run `seo-foundation` first. If declined, proceed and mark the report `Confidence: Partial` with intent findings flagged as inferred from the SERP rather than from a map. |
| The page is JS-rendered and comes back near-empty | `fetch_page.py` escalates to crawl4ai automatically and records which engine won. If both come back empty, that is itself the finding - report it as a rendering problem and hand off to a technical pass rather than auditing an empty document. |
| Asked to change URLs to be more keyword-rich | Push back. Note-only is the default. Four exceptions justify a change (genuinely broken or misleading, restructuring anyway, contains something that must be removed, migrating for other reasons). "It would be tidier" is not one of them, and the cost is every inbound link. |
| A client wants a word-count target | There isn't one, and padding to hit a number is exactly the pattern the helpful-content system catches. Report the count as an observation, never as a verdict. Answer coverage is the real question: name what the top 3 cover that this page does not. |
| Asked whether a page appears in AI Overviews | Not observable from any data source here - verified by `seo-foundation` across 5 query shapes, Serper never returns it. Report `unknown`, list the observable structural components, and tell them to check the query in incognito. |
| The audit finds only trivial issues | Say that. "The on-page layer is fine, the problem is upstream" is a legitimate and valuable finding, and inventing three fixes to look thorough is padding. Hand off to `seo-foundation` (wrong keywords) or a technical pass (crawl or speed). |
| Asked for technical, off-page or AI-search execution | Out of scope by design - those are separate skills Aleem is building. Produce the on-page layer, then say which skill owns the rest. CWV appears here only as a floor check on media weight. |
| Two pages target the same cluster | That is the cannibalization finding, and `push_sheet.py` blocks the write. Resolve it before shipping: Consolidate (merge and 301 to the winner, never to the homepage) beats Differentiate beats Prune. |
| A "refresh" turns out to be a date change | Refuse to call that an update. Real freshness is new data, new sections for questions that emerged, removed advice that is no longer true, and a re-read of the SERP for intent drift. Fake freshness is a recognized pattern and does not work. |
| Draft mode, no live URL | Everything works except `lighthouse.py`, `links.py` (no site to crawl) and the live half of `media.py`. Say which checks did not run rather than reporting them as passing. |

---

## Reference Map

```
references/
├── method.md              # THE PIPELINE: phases 0-9 end to end. Load this first.
├── checks.md              # the check registry: id -> threshold -> source -> verdict logic
├── terms-workflow.md      # the term-gap loop and the Revise-Don't-Rewrite edit contract
├── clusters-and-links.md  # pillar/cluster sizing, internal-link opportunity discovery
├── media.md               # image weight, format, alt, video and transcripts
├── refresh-tracks.md      # keep / update / merge / remove and the inventory schema
├── sheet-schemas.md       # exact tab and column definitions + the payload shape
├── report-structure.md    # the four-part output, expanded, with a worked diagnosis
├── review-rubric.md       # REVIEW MODE: the scorecard
└── what-not-to-do.md      # the kill list - read before delivering
```

Numbers cited as `[sN]` resolve via `seo-advisor/_research/sources.json`, and `course/NN`
refers to `seo-advisor/references/course/NN-*.md`. This skill deliberately has no corpus of
its own: it executes the method that corpus already established, and duplicating 320
sources would only let the two drift apart.

**Resolve `[sN]` by the `index` field, not by array position.** `sources.json`'s own `note`
field, `research-synthesis.md` and `seo-advisor/SKILL.md` all say `sources[N-1]`. That is
wrong - 256 of the 320 entries have `index != position + 1`. Use
`{s["index"]: s for s in sources}`, which is what `seo-advisor/_research/render_answer.py`
already does.

**`[sN]` is not portable across skills.** `blog-writer` has its own separate 83-source
corpus using the same `[sN]` syntax, so `[s34]` there and `[s34]` here are different
sources. Everything in this skill cites seo-advisor's namespace only.

## Writing Rules

- **Internal (to Aleem):** direct, analytical, no fluff. Bullets over paragraphs.
- **Client-facing:** authoritative and plain. Write like an operator, not a tool vendor.
  Translate the jargon - "LCP" means nothing to a client, "the biggest thing on screen takes
  4.1 seconds to appear" does.
- **No emojis. No em dashes in body text** (headings may use them). Commas or periods.
- **Never mention NexusPoint or Aleem** inside the client's report. It is their document.
- **Every number resolves** to a measurement made here, an `[sN]` citation, or a named
  assumption. If it does none of those, cut it.
- **Tag the tier on borrowed claims.** The corpus is 18 confirmed against 302 practitioner
  and that ratio matters. `[confirmed]` is Google documentation or peer-reviewed;
  `[practitioner]` is a vendor blog or a correlation study. Flattening them into one
  confident voice is the failure mode.
