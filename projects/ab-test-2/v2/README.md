# Reply Drafter

Drafts replies to inbound client enquiries in your voice, lets you edit and judge each
draft, and tells you whether your prompt edits are actually making the drafting better.

Runs locally. **No API key required** — with no key set it runs on a deterministic offline
drafter and every feature, including the whole measurement pipeline, still works.

## Run it

Node 24 or newer. There are no dependencies to install.

```
npm start           # http://127.0.0.1:3300
npm test            # 116 tests
npm run demo        # builds a demo database with SYNTHETIC ratings, to see the scoreboard populated
```

To draft with live Claude instead of the offline drafter:

```
ANTHROPIC_API_KEY=sk-ant-... npm start
```

The key is read from the environment only. It is never stored, never logged, and never
returned by any endpoint. `/api/health` reports a boolean and nothing else.

## The loop

1. **Inbox** — paste an inbound enquiry.
2. **Draft** — generate a reply with the active prompt version.
3. **Review** — edit it into what you would actually send, then mark it good or bad.
4. **Prompt** — change the prompt. Saving creates a new version; it never overwrites one.
5. **Scoreboard / Bench** — find out whether the change helped.

## How it knows whether the drafting is improving

The obvious version of this feature is a thumbs-up counter trending over time. It lies, in
two ways, and most of the design here is about those two ways.

**The inputs are confounded.** Prompt v1 was rated on last week's enquiries and v2 on this
week's. If this week's were easier, v2 looks better and the prompt had nothing to do with
it. You would be measuring your inbox.

So there is a **bench**: a fixed, saved set of enquiries. Running the bench against a
prompt version drafts every one of them, so two versions are compared on byte-identical
inputs and the only thing that varied is the prompt. The scoreboard's scope selector keeps
bench numbers and real-inbox numbers apart, and labels the inbox ones as confounded rather
than quietly averaging them together.

Bench rating is **blind by default** — the version label is hidden while you judge, because
knowing which prompt wrote a draft is exactly how you talk yourself into believing your
latest edit helped.

**Small samples do not support confident numbers.** Eight ratings against six cannot
separate a real improvement from a coin flip, but "62.5% vs 58.3%" looks authoritative.

So every approval rate carries a **Wilson 95% interval**, drawn as a bar and plotted as
whiskers on the trend chart. A head-to-head returns `better` or `worse` only when the two
intervals do not overlap. Otherwise it says `no detectable difference` and explains that the
gap is within noise. Below five reviews on either side it returns `not enough data` and
declines to render a winner at all.

**Two signals, not one.** The verdict is what you said. The **edit ratio** — word-level
Levenshtein between the draft served and the text you kept, 0 to 1 — is what you actually
did. It costs nothing to collect, it is continuous rather than binary, and it is much
harder to fool yourself with. A version whose drafts you keep verbatim is winning even if
you were stingy with the thumbs-up.

**Mock and live drafts are never mixed silently.** Every draft records its provider, and any
version whose ratings mix offline-mock with live Claude output is flagged on the scoreboard.
Cost is reported only when every draft in the group carried a real one, so an offline run
can never render as "$0.00 spent" and be mistaken for a measurement.

## Model

`claude-sonnet-5`, at $2 per million input tokens and $10 per million output tokens.

Drafting a client reply is tone-matching, not reasoning. Opus 5 is 2.5x the price for
capability the task does not use; Haiku 4.5 is half the price, but this is client-facing
copy where voice is the entire product. Requests go out with
`output_config: { effort: "low" }`, which the docs recommend for latency-sensitive
non-coding work.

The model ID, the prices, the `output_config` nesting and the `anthropic-version` header
were all read from `platform.claude.com` on 2026-09-01 rather than written from memory.
Details and links are in `src/providers/anthropic.ts`.

## Layout

```
src/
  main.ts              entrypoint: starts both servers, seeds an empty database
  api.ts               HTTP routes, error mapping, local-only access control
  service.ts           business logic: versions, drafts, reviews, scoreboard, bench
  metrics.ts           edit ratio, Wilson intervals, the head-to-head verdict
  db.ts                schema
  http.ts              body reading and per-field validation
  web.ts               static server on 3300, proxies /api to 4300
  seed.ts              starter prompt and the six-enquiry bench
  providers/
    mock.ts            deterministic, prompt-sensitive offline drafter
    anthropic.ts       live Claude, with the model and pricing constants
    index.ts           picks one based on the environment
web/                   index.html, app.js, style.css. No framework, no build.
test/                  116 tests across metrics, providers, service, API, static, smoke
scripts/demo.ts        builds a demo database with synthetic ratings
```

## Notes

- `data/` holds the SQLite database and is gitignored.
- The servers bind to `127.0.0.1` only, never `0.0.0.0`. There is no login, because adding
  one to a loopback tool is theatre; the controls that matter are the Origin and Host checks
  in `api.ts` and `web.ts`, which stop other pages in your browser and DNS rebinding.
- Enquiry bodies are hostile input. They reach the DOM through `textContent` only.
