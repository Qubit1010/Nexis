# The Method - phases 0 through 8

The pipeline, in order. Each phase names who does the work: a **script** where the step is
mechanical, **you** where it needs judgment. Getting that division wrong in either
direction is the main way this goes badly. A script that fakes judgment produces confident
nonsense; a human redoing arithmetic burns the time that should go into reading SERPs.

---

## Phase 0 - Resolve the inputs

Find what already exists before asking the client for anything.

```bash
ls client-projects/<slug>/
```

Look for `*strategic-foundation.md` and `*audience-persona.md` (glob on the suffix, the
numeric prefix is a convention rather than a guarantee). If they exist, read them. They
are the difference between keywords that belong to this client and keywords that belong to
their industry in general.

If they do not exist, resolve whatever was supplied using the same table
`strategic-foundation` uses:

| Input | Command |
|---|---|
| Google Doc URL/ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX / XLSX | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then read the `.md` |
| Website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 12 --extract raw` |
| Name only | `python .claude/skills/research/scripts/research.py --query "<name> <hint>" --depth medium --mode entity` |

Offer to run `strategic-foundation` first when there is no persona. Say why: without it
you are guessing at the customer's vocabulary, and vocabulary is what keyword research
operates on. If the user declines, proceed and mark the report `Confidence: Partial`.

**Establish before moving on:** what they sell, who buys it, where they operate (this sets
`--gl`/`--hl`), their site URL, and whether the site already has content.

---

## Phase 1 - Harvest the persona

Two blocks in `08-audience-persona.md` carry almost all the value:

**"Questions they actually ask"** is already grouped by intent - Informational, Commercial
investigation, Transactional, Post-purchase. These are seeds that came from real customer
language rather than from a keyword tool's autocomplete of an industry term.

The persona uses four buckets; this skill uses six (see `intent-taxonomy.md`). Add **Local**
if the client serves a geography, and **Generative AI intent** for the long conversational
phrasings people now type into chat assistants.

**"They say / they never say"** is the vocabulary table. The left column is what to build
keywords from. The right column is what to keep out, and it matters more than it looks -
targeting industry jargon the customer never uses is the most common way a keyword list
looks professional and produces nothing.

Pull 5-10 **seed topics** from this plus the client's own service list. Seeds should be
things the business does, in customer words, not clever long-tail phrases. The expansion
finds those.

---

## Phase 2 - SERP-competitor discovery

Full procedure in `competitor-discovery.md`.

```bash
python scripts/collect.py competitors \
  --seeds "seed one,seed two,seed three" \
  --business-competitors "rival1.com,rival2.com" \
  --out competitors.json
```

Three to five seeds so a domain has to *recur* to count. The script drops aggregators and
platforms, ranks what is left, and reconciles against the business competitor list from the
strategic foundation.

**The delta is the finding.** Domains that own page one but are not on the business list
are beating this client in search without competing commercially. Rivals absent from page
one are invisible in search. Both go in section 2 of the report.

---

## Phase 3 - Collect candidates

The rule is **collect, do not judge**. Target 200+ raw candidates. Judging early is what
produces a tidy list of forty obvious keywords, which is the failure mode this phase exists
to prevent.

**Mechanical layers** (script):

```bash
python scripts/collect.py expand --seeds "a,b,c" --out candidates.json
```

Autocomplete (alphabet, prefix and question patterns - free, no key, no credits), plus
People Also Ask and related searches from one SERP call per seed.

**Judgment layers** (you):

- **First-party.** The persona's question list. Search Console queries if the client owns
  the site and grants access - measured data beats every estimate, but it only exists for
  queries they already rank for.
- **Communities.** How customers phrase the problem in their own words:
  ```bash
  python .claude/skills/research/scripts/research.py \
    --query "<category> customers problems reddit forum" --depth deep --save
  ```
- **Competitor vocabulary.** Crawl the Phase 2 domains and read their page titles and
  navigation for topics they cover and this client does not:
  ```bash
  python .claude/skills/web-scraper/scripts/scrape.py \
    --url "https://<competitor>" --depth crawl --pages 25 --extract raw
  ```
- **AI fan-out.** Answer engines expand one prompt into 5-11 sub-queries `[practitioner]`.
  Ask directly: "what sub-queries would you search to answer this?" Those sub-queries are
  keywords, and they show zero volume in every tool that exists.

**Paid keyword tools are deliberately absent.** No free volume API exists in 2026, and
`course/07` argues volume is the wrong sort key regardless. Say this in the report rather
than leaving a silent gap.

Only exact duplicates get dropped. Near-variants survive - deciding whether two phrasings
are one thing is Phase 6's job, and it decides from SERP evidence rather than string
similarity.

---

## Phase 4 - Intent and the SERP read

This is where the credits go: one Serper call per keyword. **Tell the user the number
before spending it.**

```bash
python scripts/serp_features.py --file queries.txt --out serp.json --gl us \
  --client-domain clientsite.com
```

**Pass `--client-domain`.** It records where the client already ranks, which changes the
question from "can we win this" to "are we defending it". On the verification run 7 of 10
queries came back already ranking, and without the flag every one of them would have been
planned as new content the client already has.

Per query the script measures domain diversity, UGC on page one, platform slots, sitelink
density, dominant content type, freshness (best-effort - most results carry no date), PAA
count, and a winnability score from 1 to 5.

**You classify intent** from the SERP shape, not from trigger words alone. Trigger words
suggest; the results decide. See `intent-taxonomy.md`.

**You answer the two questions the script cannot:** do the ranking pages actually answer
the query, and could this client be *clearly* better. Both appear in each row's
`needs_human_read`.

**What comes back `unknown`, honestly:** AI Overview presence is never returned by this
data source, and it is half the click-availability test. Report it as unknown and tell the
user to check in incognito. Do not infer it.

Everything is cached, so Phases 5-7 re-read these SERPs for free.

---

## Phase 5 - Score

Rubrics in `scoring.md`. Score **Relevance** and **Intent value** 1-5 each, fast, by
instinct - you know the business by now. Click availability and winnability come from
Phase 4 as tiebreakers.

```
Priority = Relevance x Intent value
```

**Sort by that. Never by volume.** The trap here is optimizing for winnability and ending
up with easy, irrelevant terms that never produce a customer.

**Checkpoint: show the top 30 before going further.** If this ranking is wrong, everything
downstream is wrong, and this is the cheapest possible place to catch it.

---

## Phase 6 - Cluster

Full detail in `clustering-and-mapping.md`.

```bash
python scripts/cluster.py --file queries.txt --out clusters.json
```

Clustering is by **shared SERP outcome, not shared wording** - Google's own results judge
intent better than our intuition about language does. The script uses complete linkage, so
every member genuinely shares a SERP with every other member.

**Read `borderline_pairs` before accepting the grouping.** Those are the pairs within one
URL of the threshold, and they are the only calls worth your time. **Name each cluster** and
confirm its primary query - the script picks the most connected member, which is usually
right and occasionally not.

---

## Phase 7 - Map

Get the client's real URLs:

```bash
python .claude/skills/web-scraper/scripts/scrape.py \
  --url "https://<client>" --depth crawl --pages 50 --extract links
```

Match each cluster to the one page that should own it. Existing page where one fits, a
planned URL where none does. Set `Status` to exactly one of: `exists and fine`, `exists and
needs work`, `needs creating`, `merge into another`.

**The invariant: every cluster maps to exactly one URL, and no URL appears twice.** A
repeat URL is not a formatting problem, it is cannibalization, and it goes on the
Cannibalization tab with an action - Consolidate (merge + 301) beats Differentiate beats
Prune. `push_sheet.py` refuses to write until this holds.

Then pick the **first pillar**: one topic, the one they most need to own. Pillar of
2,500-4,000 words with 8-15 cluster pages and bidirectional internal links `[practitioner]`.
One complete cluster beats four half-built ones.

---

## Phase 8 - Ship

Assemble the payload (shape in `sheet-schemas.md`) and validate before writing:

```bash
python scripts/push_sheet.py --payload payload.json --validate-only
python scripts/push_sheet.py --payload payload.json --title "SEO Foundation - <Client>"
```

Then write the report to `client-projects/<slug>/09-seo-foundation.md` using the structure
in SKILL.md.

**Run `what-not-to-do.md` over the whole thing before delivering.** Include the measurement
baseline (Phase 7 of the report) - and flag the one irreversible setup step: GA4 data
retention defaults to 2 months and must be raised to 14, and it does not apply
retroactively `[confirmed]`.

Report the Serper credits actually spent. Every script prints it.
