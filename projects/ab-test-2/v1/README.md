# ReplyLab

A local workbench for drafting replies to inbound client enquiries, and for telling whether your
drafting prompt is actually getting better as you change it.

It runs completely without an API key. With no key it uses a deterministic stub drafter, so the
whole loop, the database, and the measurement are real and walkable offline. Add a key and the
same app drafts with Claude.

## Run it

```bash
npm install
npm run dev          # UI on http://localhost:3200, API on http://localhost:4200
```

Open http://localhost:3200. A banner will tell you it is in stub mode.

To draft for real, copy `.env.example` to `.env`, put your key in `ANTHROPIC_API_KEY`, and
restart. Nothing else changes.

```bash
npm test             # 64 tests
npm run typecheck
npm run build
npm run seed:demo    # optional: fills data/demo.db with fabricated data so the
                     # Scoreboard has something to show. Never touches your real database.
```

To browse the demo data: `REPLYLAB_DB=data/demo.db npm start` then run `npm run dev:ui` separately.

## The three things it does

**Draft.** Paste an enquiry's subject and body. ReplyLab drafts a reply using the currently
active prompt version.

**Review.** Read the draft, edit it in place, mark it good or bad.

**Measure.** This is the part that matters, and the reason the data model looks the way it does.

## How the measurement works

Prompt versions are **immutable**. Editing the prompt never overwrites anything, it creates
version N+1 and makes it active. Every draft permanently records which version produced it. So a
rating is always attached to the exact prompt text that earned it, and old ratings never get
silently re-attributed to new prompt text.

The Scoreboard then shows one row per version:

- **Good rate** with a bar on a shared 0-100% axis.
- **A 95% Wilson confidence interval**, drawn as a whisker. This is the point of the whole
  screen. One good rating out of one gives a bar at 100% and a whisker from roughly 21% to 100%.
  Without the whisker that version looks like a breakthrough. With it, it looks like what it is,
  which is not yet evidence.
- **A "not enough data" flag** under 5 ratings.
- **Kept %**, the median share of the model's words that survived your editing. A second signal
  that costs you nothing to produce, and it arrives whether or not you remember to click a
  rating.

Two honest caveats, also stated in the app itself:

1. The numbers are **observational, not an experiment**. Different versions were rated on
   different enquiries, so a gap in good rate can come from an easier batch rather than a better
   prompt. Overlapping whiskers mean the comparison is not yet conclusive.
2. The cleanest comparison you can make by hand is to **re-draft the same enquiry** under a new
   version, which holds the input constant. The Desk has a "Re-draft with v{n}" button for that,
   and earlier drafts for an enquiry are listed underneath with their version and rating.

## Model

`claude-opus-5`, $5.00 per 1M input tokens and $25.00 per 1M output tokens. The provenance of
both facts is documented at the top of `server/pricing.ts`. Per-draft cost is computed from the
API's reported token usage and shown in the metadata strip under each draft.

## Layout

```
server/     Express API, SQLite, providers, and the scoreboard maths
src/        React UI
tests/      Vitest suite
scripts/    opt-in demo data
.builder/   how this was built: blueprint, architecture, design system, test plan, review
```

Stack rationale is in `.builder/blueprint.md`. Every non-obvious call is logged in
`.builder/decisions.md`.
