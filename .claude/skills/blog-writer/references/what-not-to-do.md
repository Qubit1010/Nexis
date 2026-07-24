# What NOT To Do — the kill list

Stale, penalized, or dead-in-2026 blog tactics. Run advice through this before delivering. Every ban cites the synthesis (`[sN]` → `_research/sources.json`).

## SEO / structure
- **Don't write a separate "for AI" version of the page.** Google calls this scaled-content-abuse spam. Same content serves people and AI [s34].
- **Don't chunk the page into tiny AI-bait fragments.** Google is explicit: use normal paragraph + heading structure, not fragmentation [s34].
- **Don't keyword-stuff.** In AI search it actively *hurts* visibility (unlike classic SEO where it's merely useless) — Princeton GEO puts it at -10% **[practitioner]** [s24].
- **Don't chase an "ideal word count."** No evidence supports one [s78][s79]. Depth follows intent.
- **Don't gate your best content or hide it behind JS that doesn't render** — AI engines and Google can't cite what they can't read [s34].
- **Don't block the AI crawlers** (GPTBot/PerplexityBot/ClaudeBot/Google-Extended) if you want to be cited [s43].
- **Don't present practitioner numbers as measured fact.** The Princeton per-method boosts, the 40-60 word block, and format citation shares are heuristics — label them (see `research-synthesis.md` honesty flags) [s24][s76].

## Voice / human tone
- **Don't ship a one-pass draft.** Uniform cadence is the top AI tell; the rhythm/voice layer is mandatory [s55].
- **Don't use the banned phrases** ("game-changer," "leverage," "dive into," "it's not just X it's Y," "in today's fast-paced world," empty "Furthermore/Moreover/In conclusion" openers) — see `human-tone-rules.md` [s51][s66].
- **Don't use em dashes or smart quotes** in the body [voice-principles].
- **Don't write neutral explainers.** voice-principles Content Ladder forbids levels 1-4 (AI summaries, generic tutorials). Aim level 7+ (POV, case study, framework).
- **Don't fake authority.** No first-hand experience on a topic? Bridge to adjacent experience and frame as a hypothesis (voice-principles No-Experience Fallback). Intellectual honesty is the voice.
- **Don't rely on "AI humanizer" tools** to pass detection — false positives are real and gimmicks read worse than genuine voice [s54][s55][s62].

## Personal-brand identity (this skill writes as Aleem)
- **Never name the agency** (NexusPoint), and **never reference university / BSAI / degree / "student"** in the output. Reframe as "in my own work / from what I've shipped / building real systems" [voice-principles Pillar 5].
- **Don't invent client details or numbers.** Use ranges or relative anchors if the exact figure isn't real (voice-principles Specificity Rules).

## Honesty
If a stat isn't in `research-synthesis.md` / `_research/` (or a live query), say so — never invent or extrapolate. Flag any net-new number that came from a live query.
