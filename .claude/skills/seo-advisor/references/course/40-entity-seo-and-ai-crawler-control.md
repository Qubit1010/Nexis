# Authority, AI Search & Strategy - Section 40: Entity SEO and AI Crawler Control

*Be a recognized thing, not a matched string. And know which bots to let in.*

**Bottom line:** Entity SEO means establishing your business as a distinct, identifiable thing
in a knowledge graph rather than a keyword on a page. The mechanism is Wikidata, `sameAs`, and
consistent co-occurrence. Separately, training crawlers and search crawlers are **different
bots**, and blocking indiscriminately removes you from AI answers while trying to opt out of
training.

---

## Part 1: Entity SEO

### Strings versus things

A **string** is text. A **thing** is an entity with a stable identifier, defined attributes,
and relationships to other entities.

Google's Knowledge Graph currently holds roughly **1.6 trillion facts on 54 billion entities**.
In **June 2025 it removed over 3 billion entities (6.26%)** in a quality purge, which tells you
the graph is actively curated rather than merely accumulated. `[practitioner, single vendor
study]` Flagging that tier matters: the prune figure comes from one vendor's analysis, not from
Google.

When you are an entity, an engine knows your business is distinct from every similarly named
one, what category you operate in, who founded it, and what you are associated with. When you
are only a string, it is pattern-matching text and hoping.

### How models form entity understanding

Two phases. `[practitioner]`

**Pre-training** on Wikipedia, Wikidata and Common Crawl builds an internal entity model.
**Inference-time retrieval** reconciles freshly fetched pages against that internal model.

This is why Wikipedia carries disproportionate weight: stable identifiers, an editorial
notability gate, and a dense cross-reference graph, all three at once.

**Wikidata is the achievable version.** Its **Q-number** identifiers back both Wikipedia
infoboxes and Google's Knowledge Graph, and it has a far lower notability bar than Wikipedia.
It is the most direct path to a Knowledge Panel for a brand without a Wikipedia page.

**Recognition speed, fastest to slowest:** Wikidata, schema disambiguation, Knowledge Panel,
Wikipedia. `[practitioner]`

### Establishing entity identity

**1. Create an Entity Home.** Usually your About page. One canonical URL that is the definitive
statement of what your business is, with a stable `@id` URI in your schema so your facts form a
connected graph rather than data islands.

**2. Organization schema with `sameAs`.** Point at your Wikidata Q-number, Crunchbase, LinkedIn
and any other authoritative profile. This is the explicit machine-readable statement that all
these profiles are the same entity. Section 30 built this; here is why it mattered.

**3. Create a Wikidata entry** if you legitimately qualify. Notability requirements are real,
just lower than Wikipedia's. Do not fabricate references.

**4. Consistent co-occurrence.** From Section 34: models learn from repeated association of
your brand with your category in credible editorial contexts. Consistency of phrasing is the
mechanism.

**5. Monitor with the Google Knowledge Graph Search API.** You can query your own KGMID and
confidence score, which is the only direct feedback available on whether Google recognizes you
as an entity at all.

### Why entity work is durable

Everything else in this tier can shift with a model update. Entity identity is infrastructure:
once Google, Wikidata and the models agree on what your business is, that persists through
algorithm changes in a way page-level optimization does not.

It is also slow. Weeks to months, not days. Start it early precisely because of the lag.

---

## Part 2: AI crawler control

### The distinction that decides everything

**Training crawlers and search crawlers are different bots.** Confusing them is the most
expensive mistake in this area. `[practitioner]`

| | Training crawlers | Search / retrieval crawlers |
|---|---|---|
| Purpose | Build model weights | Index for real-time answers and citations |
| Referral value | Effectively zero | Sends high-intent traffic via citations |
| Share of AI bot load | **~82%** | **~15%** |
| Conversion of referred traffic | n/a | **4 to 5x higher** than traditional search |

Blocking `GPTBot` and `ClaudeBot` opts you out of training. Blocking `OAI-SearchBot` and
`Claude-SearchBot` removes you from AI answers entirely. People routinely do the second while
intending the first, then wonder why they vanished.

### The control matrix

| User-agent | Owner | Action | Why |
|---|---|---|---|
| **GPTBot** | OpenAI | **Block** | Training only, no referral value |
| **OAI-SearchBot** | OpenAI | **Allow** | Powers ChatGPT search citations |
| **ChatGPT-User** | OpenAI | **Allow** | User-triggered fetch |
| **ClaudeBot** | Anthropic | **Block** | Training. Peaked at **70,900 pages crawled per referred visitor** |
| **Claude-SearchBot** | Anthropic | **Allow** | Retrieval and citation |
| **PerplexityBot** | Perplexity | **Allow** | Retrieval, sends referrals |
| **Google-Extended** | Google | Judgment call | Gemini training opt-out. Does **not** affect Search ranking |
| **anthropic-ai** | Anthropic | **Deprecated** | Legacy. Configs still citing it are giving broken instructions |

`[practitioner]`

**The asymmetry argument:** Googlebot's crawl-to-referral ratio is about **5:1**. Anthropic's
training crawler peaked at **70,900:1**. Training bots take vastly more than they return, which
is the case for blocking them and the case for allowing their search counterparts.

**`Google-Extended` is a genuine judgment call**, and worth stating clearly because clients ask:
it opts you out of Gemini training and has **no effect on Google Search ranking**. Blocking it
costs you nothing in Search. Whether it costs you Gemini visibility is less clear, which is why
it is judgment rather than a rule.

### robots.txt is a request, not a lock

**`robots.txt` is voluntary.** Well-behaved crawlers honor it. It is not a technical control,
and treating it as one is a misunderstanding worth correcting explicitly with clients.

**Real enforcement requires WAF or server-level IP rules**, which are evaluated *before*
robots.txt is even read. Cloudflare AI Crawl Control and Kinsta Bot Protection expose one-click
toggles for this. `[practitioner]`

If a client says "block AI from our content", establish which they mean: a polite request, or
actual enforcement. They are different projects.

### llms.txt: the honest answer

A proposed Markdown site map for LLMs at `/llms.txt`.

**No major search engine or AI vendor honors it for ranking or access control.** Google
explicitly ignores it and has compared it to the long-discredited keywords meta tag, stating
there is "no measured reason" for citation gains. OpenAI points to robots.txt instead. Adoption
sits at about **10% of domains** across a 300,000-site sample. `[practitioner]`

**Its one genuine use** is developer documentation consumed by coding assistants like Claude
Code and Cursor, where it reduces context noise. That is a real use case and a narrow one.

**Do not sell llms.txt as an SEO deliverable.** Vendors sell generators for it. Google says it
does nothing. Charging for it is the clearest available test of whether an SEO provider is
reading evidence or reading marketing.

> **Why this matters:** these two halves are the durable and the reversible ends of AI
> visibility. Entity identity takes months and survives algorithm changes. Crawler
> configuration takes ten minutes and can silently delete you from AI answers if you get the
> bot names wrong. Both are worth precision.

## Do this now

**Entity work:**

1. **Designate your Entity Home**, usually the About page, and make it genuinely definitive.
2. **Add Organization schema with a stable `@id`** and `sameAs` pointing at every authoritative
   profile you have.
3. **Check whether you have a Wikidata entry.** If not and you qualify, create one with real
   references.
4. **Query the Google Knowledge Graph Search API** for your brand. Record whether you have a
   KGMID and its confidence score.
5. **Verify your entity description is identical** across every profile, per Section 34.

**Crawler work:**

6. **Read your current robots.txt** and list every AI user-agent mentioned.
7. **Check for `anthropic-ai`.** If present, your config is following deprecated guidance and
   should be reviewed entirely.
8. **Set the split deliberately:** block GPTBot and ClaudeBot, allow OAI-SearchBot,
   Claude-SearchBot, ChatGPT-User and PerplexityBot.
9. **Decide on Google-Extended** and write down the reasoning. It does not affect Search.
10. **Check your server logs or Cloudflare analytics** for actual AI crawler traffic. Confirm
    the bots you allowed are arriving and the ones you blocked are not.
11. **If you need real enforcement**, note that robots.txt is not it and scope WAF rules
    separately.

## Capstone step

Your capstone has a designated Entity Home with stable `@id` and `sameAs` schema, a Wikidata
entry or a documented reason it does not qualify, a recorded Knowledge Graph API check, and a
deliberate robots.txt AI crawler policy that blocks training bots while allowing every search
and retrieval bot, verified against real crawler logs.

## Key takeaways

- Entity SEO is about being a recognized thing: Entity Home with stable `@id`, `sameAs` to
  Wikidata and Crunchbase and LinkedIn, consistent co-occurrence. Slow to build, durable once
  built.
- Wikidata Q-numbers are the achievable path to Knowledge Graph recognition, and recognition
  runs Wikidata fastest, Wikipedia slowest.
- Training bots and search bots are different. **Block GPTBot and ClaudeBot, allow
  OAI-SearchBot, Claude-SearchBot and PerplexityBot.** Getting this backwards removes you from
  AI answers.
- robots.txt is a request, not a lock, and llms.txt is honored by nobody. Do not sell either as
  more than it is.
