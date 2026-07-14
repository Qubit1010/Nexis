# What Not To Do

Sourced kill list. Citations resolve via `research-synthesis.md` / `_research/sources.json`.

- **Don't default every target to one engine.** The cost spread is 10-50x; the wrong pick either overpays
  or fails. Route per target and escalate on block [Q1 12].
- **Don't skip the API check.** If the page is fed by a JSON/XHR endpoint you can replicate, calling it is
  10-100x faster and more reliable than parsing HTML — and often ToS-allowed where scraping isn't [Q1 2].
- **Don't trust HTTP 200 as success.** A login-wall or CAPTCHA page returns 200 with zero rows — the #1
  silent failure. Check the payload shape/row-count before declaring success; escalate on empty [Q1 9].
- **Don't hand-roll a Cloudflare bypass in-process.** It's 5 simultaneous layers that shift monthly;
  escalate to an engine/unblocker that bundles all five instead [Q2 19][20][21].
- **Don't think a residential proxy alone hides you.** A clean IP with a `requests` TLS fingerprint, wrong
  header order, or contradictory `Accept-Language` still gets flagged — most detection is self-inflicted at
  the config layer [Q2 24][28].
- **Don't rotate IPs mid-session.** An authenticated session that teleports to a new IP is an instant flag;
  use a sticky session for multi-step/auth flows, per-request rotation only for stateless fetches [Q2 24].
- **Don't scrape at a fixed cadence with no jitter.** Exactly one request / 500ms is *easier* to detect
  than natural variance; jitter your delays, backoff with full jitter on 429/503 [Q2 30][32].
- **Don't measure politeness per script.** Five "polite" concurrent jobs on one domain still DoS it — cap
  concurrency per target, think load-per-target [Q2 33][35].
- **Don't reach for LLM extraction on a stable, known DOM.** CSS/XPath is fractions of a penny and
  milliseconds; LLM is dollars and seconds. Use `css` for stable structure, `llm` only where layout varies
  or drifts [Q3 37].
- **Don't trust LLM-extracted data without schema validation.** LLMs return a price as a string, drop a
  required field, or hallucinate values. Validate against the schema and retry with the error [Q3 45].
- **Don't dedupe before you've defined record identity, or enrich before validating.** Dedup too early
  collapses distinct items; enrich too early multiplies bad data [Q3 50].
- **Don't overwrite raw with cleaned.** Keep raw alongside curated — it's your only debug trail when a
  normalization rule turns out wrong [Q3 48][50].
- **Don't scrape gated / logged-in / paywalled content, or assert blanket legality.** Public data is
  broadly defensible (hiQ, Meta v Bright Data) but ToS/contract + copyright + GDPR still bind; the real
  exposure is publisher contracts, not the CFAA [Q7 118][123][Q8 126].
- **Don't scrape social platforms with this skill.** They forbid it in ToS and block hard; use the house
  `lead-generator` / `facebook-lead-nav` paths instead [Q8 127].
- **Don't quote this category's pricing or actor IDs as fixed.** Tools re-price monthly and actor
  input-schemas change; verify before quoting to a client [Q8 130].
