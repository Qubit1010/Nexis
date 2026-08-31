# Subject-scoped context doc — spec and sourcing

The marketing-skills pack assumes one product, one file, at `.agents/product-marketing.md`.
Nexis serves multiple subjects, so BUILD Stage A writes a scoped equivalent per subject instead —
same 12-section template, different path, and critically, different sourcing than v1's engine.

## Paths

| Subject | Context doc path |
|---|---|
| Client `<slug>` | `client-projects/<slug>/product-marketing.md` |
| Aleem, personal brand | `agency/personal-brand-product-marketing.md` |

## Raw material to draft from, per subject

**Client:** `client-projects/<slug>/01-overview.md`, `02-what-they-want.md` — these are
pre-chain intake notes, written before any numbered marketing-chain doc existed, so they're
genuinely raw. Also pull the agency-brain vault's `clients/<slug>/brief.md`,
`brand-voice.md`, and `decisions.md` if populated (path:
`C:\Users\qubit\OneDrive\Documents\agency-brain\clients\<slug>\`). If the client's original Drive
onboarding doc or discovery notes are linked from `client-projects/<slug>/README.md`'s Drive kit
section and accessible, pull from those too.

**Aleem's personal brand:** `context/me.md`, `context/current-priorities.md` — his own standing
facts, not a chain-derived synthesis. Also the agency-brain vault's `wiki/nexuspoint-overview.md`,
`wiki/offer-and-positioning.md`, `wiki/portfolio.md`, `wiki/services-and-difficulty.md`
(path: `C:\Users\qubit\OneDrive\Documents\agency-brain\wiki\`). Also his actual published post
history — read from the same Content Log Google Sheet v1's `log_post.py` writes to
(`SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q"`, `Content Log` tab). This is genuinely
raw material: it's his real output, not a document another skill synthesized about him.

## Explicitly excluded — never read these for context-building

`07-strategic-foundation.md`, `08-audience-persona.md`, `13-brand-strategy.md`,
`14-brand-voice.md`, `17-conversion-copy.md`, `18-content-strategy.md`, `09-seo-foundation.md`,
and their `agency/personal-brand-voice.md` / `agency/personal-brand-pillars.md` equivalents.

These are all *already-synthesized* documents — the whole reason content-engine v1 exists is that
another skill (`brand-voice`, `content-strategy`, etc.) already distilled a subject's voice and
audience from raw material once. Reading them here would make v2's context doc a reformat of the
same underlying analysis, not an independent derivation — and the entire premise of testing v2
against v1 is that they draw genuinely different conclusions from genuinely different starting
points. If a request tries to shortcut BUILD by pointing at these files instead, say so plainly
and decline rather than quietly complying.

## The 12-section template

Fill exactly the structure defined in
`.claude/skills/marketing-skills/product-marketing/SKILL.md` (Product Overview, Target Audience,
Personas, Problems & Pain Points, Competitive Landscape, Differentiation, Objections &
Anti-Personas, Switching Dynamics, Customer Language, Brand Voice, Proof Points, Goals). Push for
verbatim customer language in §9 wherever the raw material has it — exact phrases beat polished
paraphrase, since v2's hook patterns trace back to this section specifically.

## Provenance stamp

Every context doc built by this skill gets a header noting it was built by `content-engine-v2`
BUILD, the date, and the subject — so a future reader (human or skill) knows its scope and
sourcing discipline before extending it, and doesn't mistake it for output from the vanilla pack
skill or a hand-written doc.
