# The editing gate — Seven Sweeps + Expert Panel Scoring

Full source: `.claude/skills/marketing-skills/copy-editing/SKILL.md`. This file condenses it for
RUN's use and adapts the panel selection to social posts specifically, since the pack's own
defaults are landing-page/email/sales-page shaped.

v1 has no equivalent gate at all — every post it writes is delivered on the strength of the
engine document alone. This gate is v2's actual point of differentiation, so don't skip or
abbreviate it under time pressure; a post that skipped the gate isn't a v2 output, it's a v1-style
output wearing v2's voice.

## The Seven Sweeps

Run in this order. After each sweep, loop back through the ones already done — a fix in a later
sweep can undo what an earlier one fixed.

1. **Clarity** — confusing structure, jargon, ambiguous statements. Confirm the "Rule of One" (one
   main idea per unit) and the "You Rule" (the copy speaks to the reader) hold.
2. **Voice and Tone** — read for consistency; a personal-brand post that starts casual and drifts
   corporate has failed this sweep. Return to Clarity after.
3. **So What** — ask "so what?" of every claim. A feature without a benefit bridge fails. Return to
   Voice/Tone, then Clarity.
4. **Prove It** — every claim needs backup: a real number, a named result, a specific moment. "Best"
   or "leading" with nothing behind it fails. Return to So What, Voice/Tone, Clarity.
5. **Specificity** — vague words ("improve," "many," "fast") get numbers, timeframes, names. Return
   to Prove It, So What, Voice/Tone, Clarity.
6. **Heightened Emotion** — does the reader feel the pain or the desire, not just read about it?
   Return to Specificity, Prove It, So What, Voice/Tone, Clarity.
7. **Zero Risk** — friction near the CTA, unanswered objections, unclear next step. Then loop back
   through **all six remaining sweeps one final time**, in this exact order: Heightened Emotion,
   Specificity, Prove It, So What, Voice and Tone, Clarity.

## Expert Panel Scoring

Run only after the Seven Sweeps converge — this is a second, independent gate, not a substitute.

**Assemble 3-5 personas suited to the piece.** Default panels by post type:

- **Single LinkedIn/Instagram post:** the subject's actual target-audience persona (drawn from
  their `product-marketing.md` §2/§3 — "does this speak to me, do I trust it?"), a platform-craft
  expert (checks against the loaded `platform-specs/<platform>.md`), a brand-voice guardian
  (checks against `product-marketing.md` §10), a skeptical scroller (hook strength — would this
  earn the next line, per `social/references/short-form-video.md`'s 3-Second Rule logic applied
  to text).
- **Repurposed piece or carousel:** add a structural-translation checker — did this become a new
  argument for the new platform, or just get copy-pasted with line breaks added.

**Process:**
1. Each persona scores the piece 1-10 on their lane, with specific critiques — not just a number.
2. Revise, addressing the lowest scores first.
3. Re-score after revision.
4. **Repeat until every persona scores 7+ AND the panel average is 8+.** Both conditions must
   hold — a 9/10/9/6 average of 8.5 still fails on the 6.
5. **Cap at 3 rounds.** If the panel hasn't converged by then, stop and surface the remaining gap
   and lowest-scoring critique to Aleem rather than looping indefinitely — some posts genuinely
   need a human call, not more automated iteration.

## Delivering the record

Attach the sweep sign-off (a one-line confirmation each sweep ran and what it changed) and the
final panel scores to the delivered piece. This is what makes a v2 output auditable during the
A/B test — a reviewer needs to see the gate actually ran, not just trust that it did.
