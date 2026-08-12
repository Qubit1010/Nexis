# ENTITY mode: identity and crawler control

Two halves of the same tier-1/tier-2 question: **is the site allowed to be fetched, and can the
engine work out who this business is?** Both are free to check, both are usually neglected, and
both gate everything downstream.

---

## The AI crawler matrix (course/40)

| User-agent | Owner | Purpose | 2026 default |
|---|---|---|---|
| **GPTBot** | OpenAI | training | **block** |
| **ClaudeBot** | Anthropic | training | **block** |
| **CCBot** | Common Crawl | training corpus | **block** |
| **Google-Extended** | Google | Gemini training | judgment - **does not affect Search ranking** |
| **OAI-SearchBot** | OpenAI | search/retrieval | **allow** |
| **ChatGPT-User** | OpenAI | user-initiated fetch | **allow** |
| **Claude-SearchBot** | Anthropic | search/retrieval | **allow** |
| **PerplexityBot** | Perplexity | search/retrieval | **allow** |
| ~~anthropic-ai~~ | Anthropic | **deprecated** | remove - a config citing it issues instructions nothing reads |

### The inversion, which is the expensive mistake

Blocking the **retrieval** bots while allowing the **training** bots forfeits the citations and
keeps the scraping. It is the exact opposite of what almost everyone intends, and it happens
because "block AI bots" sounds like one decision.

The asymmetry that usually settles the argument:

| Crawler | Pages crawled per referred visitor |
|---|---|
| Googlebot | ~**5** |
| Anthropic's training crawler (peak) | ~**70,900** |

Roughly **82%** of AI bot load is training and **~15%** is search. But AI-referred traffic
converts **4-5x** better than traditional search. So the defensible default is: block the
bandwidth, keep the citations.

### robots.txt is not enforcement

It is a request. Real enforcement is WAF or server-level IP rules (Cloudflare AI Crawl Control,
Kinsta Bot Protection), evaluated **before** robots.txt is ever read. `ai.robots_is_not_enforcement`
fires `review` whenever any block is declared, so a client is never told a polite request is a
lock.

**Verification, when it matters:** check server logs or Cloudflare analytics that allowed bots are
arriving and blocked ones are not. This skill cannot do that; say so.

### llms.txt

**Absent is a `pass`.** No engine honors it. Google explicitly ignores it and has compared it to
the keywords meta tag. Adoption is ~**10% of domains** across a 300,000-site sample. There is no
measured citation benefit.

**Present is a `review`, never a `fail`.** It is harmless. Leave it. Do not bill for it, do not
present it as an AI-search deliverable, and do not bill for removing it either - the correct
action on an existing one is none.

The one genuine use is developer documentation for coding assistants (Claude Code, Cursor). That
is a docs decision, not an SEO one.

---

## Bing, and why it is tier 1

**ChatGPT retrieves from Bing's index**, and roughly **90% of its citations come from pages ranked
21+ on Google.** Google position is close to irrelevant there. A site absent from Bing cannot be
cited by ChatGPT regardless of content quality.

course/39 calls submitting to Bing Webmaster Tools "the highest-value ten minutes in this
section". This skill returns `unknown` for `bing.indexed` and `bing.sitemap_submitted` because
both need the client's own free account. Hand over the steps; do not guess from a `site:` count,
which Bing returns as an estimate.

**IndexNow** is free, open, needs no account, and notifies Bing instantly on publish.

---

## Entity identity (course/40)

An entity an engine cannot resolve cannot be attributed. LLMs form entity understanding in two
phases: pre-training (Wikipedia, Wikidata, Common Crawl) and inference-time retrieval. You can
influence both, on different timescales.

**Recognition speed, fastest to slowest: Wikidata, schema disambiguation, Knowledge Panel,
Wikipedia.** Timeline is weeks to months. Frame it as infrastructure, never a quick win.

### The five artifacts

| Artifact | What it is | Check |
|---|---|---|
| **Entity Home** | one canonical page that defines the entity, with a stable `@id` URI. Usually About. | `entity.home_declared` |
| **Organization schema with `sameAs`** | pointing at Wikidata, Crunchbase, LinkedIn | `entity.sameas_present` (via seo-technical) |
| **Wikidata entry** | the achievable path - a Q-number | `entity.wikidata_qid` |
| **Consistent co-occurrence** | one description, one founder spelling, everywhere | `entity.description_consistency` |
| **Knowledge Graph presence** | a KGMID plus a confidence score | `entity.kg_recognized` |

### Wikidata: free, no key, and the disambiguation trap

`wbsearchentities` needs no credential. But a match is not the same as *the* match.

**Measured live:** searching "Example Faire" returns **Bristol Renaissance Faire**
(Q4968993) *above* the correct entity. A naive implementation takes hit #1 and attaches
the client to a competitor's entity.

So the verdict logic is: `pass` only when the right entity ranks first; **`review` when a
same-name or similar entity outranks it**, with both named; `fail` when there is none and the
brand plausibly qualifies.

### Knowledge Graph API

Free at **100,000 read calls/day**. Returns a KGMID (`/m/` = migrated from Freebase pre-2015,
`/g/` = created after) plus a `resultScore`.

**Currently returns 403 `SERVICE_DISABLED`** on Google Cloud project `368115608502`. The key in
`.env` is valid; the API is simply not enabled. One click:
`https://console.developers.google.com/apis/api/kgsearch.googleapis.com/overview?project=368115608502`

Until then `entity.kg_recognized` is `unknown` and carries that URL. It is the cheapest gap in the
whole skill to close.

### `sameAs` that does not resolve

`entity.sameas_resolve` fetches every `sameAs` URL and fails on a 404 or a redirect-to-homepage.
Free, fast, and almost nobody checks it. A `sameAs` pointing at a dead profile actively muddies
the entity it exists to clarify.

---

## What this mode hands off

| To | For |
|---|---|
| `seo-technical/schema.py` | all JSON-LD validation, including `organization_sameas` and `stable_ids`. Read its output; never re-derive. |
| `seo-technical/emit.py` | writing a corrected robots.txt AI block. It already owns `AI_POLICY`. |
| `seo-technical/render_diff.py` | whether the raw HTML is empty - a client-rendered site can rank in Google and be invisible to ChatGPT. |
