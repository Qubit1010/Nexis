# Writing the Reel Voice Script

The script is the spine of the reel. The animation is timed to it, so a tight,
well-paced script does most of the work. This file is the craft: how to write a
40-50s script that hooks, lands, and stays on brand.

## The length math (get this right)

Ground truth: the CodeGraph script was 125 words and ElevenLabs read it at **59s**,
well over the 50s target. That is a pace of ~**2.1 words per second**, much slower
than the 2.6-2.8 you might assume. Size against ~2.2 wps:

- ~45s reel ≈ **95-100 words**
- ~50s reel ≈ **105-110 words** (the ceiling, do not exceed)
- Aim for **90-105 words.** It is far better to come in at 42s than to risk 55s.

Lesson from CodeGraph: when in doubt, cut. Short sentences. One idea per sentence.
If a sentence isn't earning its place, delete it. The reel rewards punch, not
coverage. (If a finished VO still comes back long, you can speed the audio ~1.15x
with pitch preserved, but writing tight up front is better.)

## The 6-beat arc

The reel has six scenes in a fixed order. Write the script as six short beats that
map one-to-one onto them. Each beat is the `voiceText` for that scene.

1. **Intro (hook) — ~1 sentence, 3s.** The whole reel lives or dies here. Lead with
   the payoff or a sharp question. The viewer decides in 3 seconds whether to keep
   watching. Examples: "What if you could cut your AI's workload by 58%?" /
   "Most cold emails die in the first line. Here's the fix."
2. **Problem — 1-2 sentences.** Name the pain the viewer feels. Make it concrete and
   a little visceral. This is where the keyword `chips` flicker, so if the pain has
   nameable symptoms (commands, metrics, failure modes), surface them.
3. **Solution — 1-2 sentences.** Introduce the fix. This is when the infographic
   pans on screen, so the line should invite the viewer to look ("Here's the one
   change that fixes it" / "So I started using X. It does Y in one shot").
4. **Stats (proof) — 1-2 sentences.** State the numbers out loud as the count-up
   cards animate. "58% fewer tool calls, 47% fewer tokens, 22% faster." Say the
   numbers in the same order they appear in `stats[]` so the audio matches the cards.
5. **Punch — 1 sentence.** The payoff/reframe. The "why this matters" line.
   "Your AI should drive outcomes, not quietly inflate your bill."
6. **Outro (CTA) — 1-2 sentences.** Soft close + follow ask. "If your agents feel
   slow and expensive, this is worth a look. Follow for more."

Not every post has hard stats. If there are no numbers, the stats beat can still
deliver 2-3 qualitative claims, or you can lean the script toward a 3-point list
that the cards display as labels. Real benchmark numbers always hit hardest — pull
them from the source whenever they exist.

## Brand-voice rules (hard constraints)

These are not stylistic preferences — they protect Aleem's brand and the pipeline.

- **No em dashes anywhere.** Use commas or periods. Em dashes break the house style
  and corrupt downstream encoding. The validator fails on any `—`.
- **Never say the agency name ("NexusPoint") and never reference his university or
  BSAI degree** in the spoken script. This is personal-brand content — it reads as
  one sharp builder sharing what he learned, not an agency ad. The end-card logo
  sting is the only brand mark, and it is visual, not spoken.
- **First person, conversational.** "When I run agents on a big codebase..." Not
  "Developers often find that...". Aleem is talking to one person.
- **No hype-speak, no emojis, no exclamation spam.** Confident and plain. One strong
  claim beats three soft ones.
- **End on a soft CTA.** "Follow for more" is the default. Pair it with a curiosity
  or qualification line so the follow feels earned, not begged.

## Hook formulas that work

Pick whichever fits the post. The hook is its own sentence and it is the intro
`voiceText`.

- **Number payoff:** "What if you could cut X by [N]%?"
- **Contrarian:** "Everyone tells you to [common advice]. It is wrong."
- **Cost of inaction:** "[Audience] is quietly losing [thing] every [time period]."
- **Curiosity gap:** "There's one [setting/change/tool] that [big result]. Most people never touch it."
- **Direct problem:** "Your [thing] is [failing] because [reason]. Here's the fix."

## Worked example (CodeGraph — the proven reel)

Full script (125 words — slightly long, which is why it ran 59s), then the per-scene
split. Note how each scene's `voiceText` is a clean slice and they concatenate back
to the full script exactly.

> What if you could cut your AI coding agent's workload by 58%? When I run AI agents
> on a large codebase, they burn time and tokens blindly scanning files. Every grep,
> glob, and read adds up fast. So I started using CodeGraph. It pre-indexes your
> whole codebase into a single map the agent can query in one shot, instead of
> crawling file by file. The gains were real. 58% fewer tool calls, 47% fewer
> tokens, and problems solved 22% faster. It even auto-syncs as I code, so the agent
> is never out of date. Here is why it matters. Your AI should drive outcomes, not
> quietly inflate your bill. If your agents feel slow and expensive, this one is
> worth a look. Follow for more.

| Beat | voiceText |
|------|-----------|
| intro | "What if you could cut your AI coding agent's workload by 58%?" |
| problem | "When I run AI agents on a large codebase, they burn time and tokens blindly scanning files. Every grep, glob, and read adds up fast." |
| solution | "So I started using CodeGraph. It pre-indexes your whole codebase into a single map the agent can query in one shot, instead of crawling file by file." |
| stats | "The gains were real. 58% fewer tool calls, 47% fewer tokens, and problems solved 22% faster. It even auto-syncs as I code, so the agent is never out of date." |
| punch | "Here is why it matters. Your AI should drive outcomes, not quietly inflate your bill." |
| outro | "If your agents feel slow and expensive, this one is worth a look. Follow for more." |

This came in slightly long. A tighter rewrite would drop "It even auto-syncs as I
code, so the agent is never out of date" from the stats beat (or move it into the
solution as a clause) to land closer to 48s. When you draft, do a quick word count
and trim toward the low end of the range.

## After you write it

Always run the validator (`node scripts/validate_content.mjs <slug>`) before handing
the script to Aleem. It is faster to fix a word-count or em-dash issue now than after
he has already burned an ElevenLabs render on it.
