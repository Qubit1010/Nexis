# What Not To Do

Sourced kill list. Citations in `research-synthesis.md`.

- **Don't trust a single source.** One engine or one page can be wrong or biased; triangulate across
  independent sources (fusion exists for this) [1][10].
- **Don't read vertically to judge credibility.** Scrutinizing a suspicious page's own content is how
  people get fooled; read *laterally* — check what others say about it [8][12].
- **Don't let the model cite anything outside the gathered sources.** LLMs invent plausible-looking
  citations — 50+ citation hallucinations were found across 300 ICLR 2026 submissions [98]. This skill
  only cites `sources.json`; if the sources don't cover it, say so.
- **Don't default every query to one premium engine.** Routing per query-class beats it by up to
  ~8.2× on cost; don't run `deep` (all engines + LLM synthesis) for a question `light` answers [93].
- **Don't confuse the search layer with the extraction layer.** Handing a known URL to a search API,
  or asking an extraction API to "find" something, burns credits on the wrong abstraction [92].
- **Don't over-stack operators for topical questions.** Dorks are for exact, scoped, Google-shaped
  retrieval; for "find pages that *mean* this," use Exa `neural` instead [85][94].
- **Don't email unverified guesses.** Permute, then verify via SMTP/MX; sending to guesses wrecks
  sender reputation [43][45][49].
- **Don't quote this category's pricing/vendor facts as fixed.** It re-prices constantly (Exa raised
  $250M, Tavily acquired by Nebius in 2026); verify before quoting to a client [93][95].
- **Don't skip the question-framing step.** A vague query wastes every downstream engine call; frame
  a precise question + sub-questions first [1][6].
