# The universal prompt contract

This skill emits **one prompt that works everywhere**, rather than a tuned variant per model. That
is only possible because the models' disagreements are asymmetric: for almost every conflict, one
convention is optimal on one model and merely *suboptimal* on the others, rather than broken. The
rules below pick the convention that never breaks.

Researched 2026-09-08. `[vendor]` is the model maker's own documentation. `[practitioner]` is a
third-party guide with no primary confirmation found. Where nothing was found, it says so.

---

## Rule 1. Positive framing only. Never state exclusions.

**This is the rule that makes universality possible, and the one most likely to be broken by
reflex.** Write the state you want, never the thing you are excluding.

| | Position on negatives |
|---|---|
| Gemini / Nano Banana `[vendor]` | Explicitly recommends **against** them. Say "empty street", not "no cars" |
| Midjourney `[practitioner]` | Prose negatives are unreliable and can summon the subject. Exclusions belong in a `--no` flag, and each word there is parsed separately, so `--no modern clothing` reads as "no modern" plus "no clothing" |
| ChatGPT / GPT-image `[vendor]` | *Recommends* stating them: "no watermark, no extra text, no logos" |

Only OpenAI wants them, and only as a recommendation, not a requirement. A GPT-image prompt without
an exclusion list still works, it just gives up one lever of control. A Gemini or Midjourney prompt
*with* prose negatives is actively worse. So positive framing wins the trade.

**Rewrite every exclusion as a description:**

| Instead of | Write |
|---|---|
| no watermark, no signature | a clean unbroken surface, edge to edge |
| no text | the composition carries no lettering, shapes alone |
| no people | the scene is unpeopled, objects only |
| no clutter | a spare composition with generous empty space |
| no lens flare, no glow | flat even light with defined edges |

The honest cost: on GPT-image specifically you lose a blunt instrument. In practice a positively
described clean state gets there, and it is the only phrasing that survives being pasted elsewhere.

## Rule 2. Aspect ratio in words, never pixels or flags.

State it as "vertical 4:5 portrait" or "wide 16:9 landscape" inside the prompt body.

- Gemini `[vendor]` takes a **named ratio** and supports 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16,
  16:9, 21:9. Words are its native form.
- Midjourney `[practitioner]` wants `--ar 4:5`. It still reads the words, and `--ar` is trivially
  added by the user if they want it. Note `--ar` is not a crop: it changes how the model composes
  from the start.
- GPT-image `[vendor]` wants pixel dimensions with real constraints: both edges divisible by 16,
  max edge under 3,840, ratio at most 3:1, total pixels 655,360 to 8,294,400, with 2560x1440 named
  as the recommended reliability ceiling. **The trap this avoids:** 1080x1350, the reflex social
  size, is *illegal* there, because neither edge divides by 16. Words sidestep the whole problem;
  the tool picks a legal size itself.

## Rule 3. Structure: subject, action, setting, composition, style, palette, text.

This ordering satisfies all three at once.

- Gemini `[vendor]` publishes exactly this as its formula: `[Subject] + [Action] +
  [Location/context] + [Composition] + [Style]`.
- Midjourney `[practitioner]` weights early tokens heavily, so leading with the subject rather than
  the style is what it wants anyway.
- OpenAI `[vendor]` suggests scene, then subject, then details, then constraints, but explicitly
  states that "minimal prompts, descriptive paragraphs, JSON-like structures, instruction-style
  prompts, and tag-based prompts can all work well" as long as intent is clear. Its ordering is a
  preference, not a requirement, so following Gemini's stricter formula costs nothing.

Write in flowing descriptive prose. Make every clause a decision. "Beautiful", "high quality",
"4k", "masterpiece" fail on all three models and should never appear.

## Rule 4. Literal text in quotation marks, with the typography described.

Both vendors recommend the same thing, which makes this easy.

- Gemini `[vendor]`: enclose the text in quotes, describe the font ("bold, white, sans-serif").
- OpenAI `[vendor]`: put literal text in quotes or ALL CAPS, specify typography, and spell out
  awkward words letter by letter for character accuracy.
- Midjourney `[practitioner]` is the weakest of the three at text. If a design depends on precise
  typography, generate the art without it and set the type afterwards.

**Text is no longer the reliability cliff it was.** GPT Image 2 is vendor-described as "well suited
for text-heavy images", and Nano Banana Pro is built for "sharp, legible text" in posters and
diagrams. Third-party guides put GPT Image 2 above 95 percent text accuracy, though no primary
benchmark was found for that figure, so treat the number as unconfirmed. Advice written before 2026
telling you to avoid text in AI images is stale. Keep text short for **legibility and design**, not
because the model cannot spell.

## Rule 5. Name the palette in hex.

Models handle "deep teal (#0F766E)" better than "teal", and hex is required whenever a brand
palette is in play. This is model-agnostic and carries everywhere.

---

## What is deliberately given up

Being honest about the trade, since this skill used to tune per model:

- **GPT-image's exclusion lists.** Rule 1 gives up a real control. Mitigated by describing the
  clean state instead.
- **Midjourney's parameter strip.** No `--s`, `--chaos`, `--weird`, `--style raw`. A user who wants
  those appends them; the prompt body underneath is already correct.
- **GPT-image's exact pixel control.** Words instead of dimensions, which as Rule 2 shows is
  usually an improvement rather than a loss.

None of these break a render. Each is a lever, not a requirement.

## Model variants worth knowing

`[vendor]` The Nano Banana family splits by job. **Nano Banana Pro** (Gemini 3 Pro) handles complex
reasoning, precise layout and high-fidelity text. **Nano Banana 2 / 2 Lite** (Gemini 3.1
Flash / Flash-Lite) are tuned for fast editing and style transfer. For a poster carrying text, Pro
is the one. Google also names its own open limitations: text fidelity, factual accuracy inside
diagrams, multilingual grammar, edit artifacts, and character consistency across edits.

## Sources

- OpenAI, GPT image models prompting guide (vendor):
  https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- Google Cloud, Ultimate prompting guide for Nano Banana (vendor):
  https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
- Google, Nano Banana Pro prompting tips (vendor):
  https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- PromptMake, Midjourney prompt guide 2026 (practitioner):
  https://promptmake.net/blog/midjourney-prompt-guide-2026
- PromptMake, Midjourney v7 guide (practitioner):
  https://promptmake.net/blog/midjourney-v7-guide
- Prompt Architects, Midjourney `--no` exclusion reference (practitioner):
  https://prompt-architects.com/blog/233-midjourney-no-exclusion-parameter
- Atlabs, GPT Image 2 prompting guide (practitioner, source of the 95%+ text figure):
  https://www.atlabs.ai/blog/the-ultimate-gpt-image-2-prompting-guide

**Refresh trigger:** these rules depend on current model behaviour. If a new generation ships, or a
prompt written from this file visibly underperforms on one tool, re-run the pass. The universal
contract holds only while the disagreements stay asymmetric.
