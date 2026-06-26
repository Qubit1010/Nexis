# Template 05 — Hybrid (recommended production method)

**Angle:** The synthesis of two live test episodes (EP35 + Deal Falling Apart). Takes the best
decision from each of the four templates and fuses them into a single, opinionated method:
**04's segment selection lens → 01's hook craft → 03's platform-native writing → 02's strategic
tagging**. This is the method to port into Min's production system.

**Source methods:** All four templates. Where they conflict, this template's rules below are
the tiebreaker. Read each source template if you need the full reasoning behind a step.

Read `references/output-spec.md` for the exact shape. Read the client's main voice file for
limits, absence signals, and ICP. This template defines how to fill that shape with the highest
average across all five rubric dimensions.

---

## Why this method

Two episodes, same scorecard result:

- **04** consistently found segments the others missed (the "texts feel sharp" nugget in Deal
  Falling Apart; the "6 months of runway" clip in EP35) because it selects on saveability and
  sends — the metrics that actually move distribution — not on topic prominence.
- **01** wrote the sharpest hooks, the ones most likely to earn the first 3 seconds, because it
  reverse-engineers the quotable line first and builds the hook around it.
- **03** wrote captions and posts that felt closest to publish-ready, because it treats
  Instagram / LinkedIn / Facebook as genuinely different surfaces with different reader modes.
- **02** added strategic clarity by naming the psychological trigger per segment, which ensures
  the set covers the ICP's full emotional landscape (fear + belonging + identity) rather than
  three takes on one theme.

No single template nailed all four. This one does.

---

## Method

### Step 1 — Segment selection (04 logic: saveability + sendability + completion)

Read the transcript and rank potential segments on three signals:

- **Saves (~3x a like):** Is it a specific, useful truth an agent wants to find again?
  Checklists, frameworks, named steps, and sharp reframes are the most saveable formats.
- **Sends (3-5x a like):** Would an agent DM this to a peer mid-crisis or send it to someone
  considering the move? "This is us" and "she needed to read this" are send triggers.
- **Completion:** Does it have a tight arc that pays off before the scroll?

Pick 3-5. Then for each segment, note **two cut options**:
- The full segment as defined in the voice file (30s-2min).
- A **tighter in-point** (15-45s) where the punch actually lands — give the editor both.

Flag which format each segment is (checklist, reframe, confession, framework) — this drives
hook selection in Step 2.

### Step 2 — Hook writing (01 logic: reverse-engineer + archetype rotation)

For each segment, find the single most quotable line in the transcript. That line is the
hook's anchor. Now write the 5 hooks by rotating the 6 archetypes — use the one that fits,
don't force all six:

1. **Number-led** — "5 steps to stabilize a deal that is falling apart."
2. **Contrarian** — "The commission split is not the most important variable."
3. **Transformation** — "From panic to plan. Here is the sequence."
4. **Authority** — "After enough years you learn the difference between dead and unstable."
5. **Admission** — "My boss is a real bitch. Then I remember the boss is me."
6. **Future-shock / stakes** — "One angry reply can kill a fixable deal."

Rules:
- **Never open with "I"** as the first word. Lead with the tension, the number, or the "you."
- Front-load the high-impact word. Scroll-stop lives in the first two words.
- The 5 hooks must be genuinely different angles, not 5 rewordings.
- Run every hook against the absence signals before keeping it.

**Self-score gate:** before moving on, score each hook 1-5 on scroll-stop. If any score below
3, rewrite it. Don't ship the first draft.

### Step 3 — Captions (03 logic: true platform-native, three different jobs)

Write **three genuinely different captions** per segment. Combine 03's platform-nativeness
with 02's "three jobs" principle:

| Caption | Platform | Job | Format |
|---------|----------|-----|--------|
| A | Instagram | Teaching or save-bait | Punchy hook line / numbered list or short stacked paragraphs / soft CTA. One idea per line. Scannable on a phone. ~80-120 words. |
| B | LinkedIn | Thought-leadership POV | Bold claim or specific moment to open. Short paragraphs, white space. End on an extractable principle or open question. ~100-150 words. |
| C | Facebook | Warm / community / peer | Conversational. A little more narrative. Speaks to the agent like a friend or peer. Invites a reply. ~80-130 words. |

Rules:
- Self-contained — no "listen to the full episode" as the only CTA.
- All three use the same segment, but the angle, rhythm, and length differ by platform. If
  all three read the same, rewrite until they don't.
- Check the absence signals on every caption before writing it to the file.

### Step 4 — Long-form posts (03 platform-native + 04 dwell-time benchmarks)

Write 3-5 long-form posts per segment. Mix LinkedIn and Facebook. Format each for its
platform's native reading behavior:

**LinkedIn posts:**
- Open with the most interesting sentence — a bold claim, a specific moment, or a short
  provocative question. Not a scene-setter.
- One sentence per line. Short sentences followed by slightly longer ones. White space is part
  of the layout.
- 150-300 words (per voice file default; Red may adjust).
- No link in the post body (kills reach).
- End on a principle, a short question, or a call to reflect — not a promo.
- Optimize for **dwell time** (61s+ dwell = ~13x engagement).

**Facebook posts:**
- Conversational opening — like you're talking to an agent in the room.
- Slightly more narrative/story structure is fine. Still use line breaks; avoid walls of text.
- 100-250 words.
- End with an invite: a question, a soft CTA, or "tag someone who needs this."

Label every post `**LinkedIn**:` or `**Facebook**:` at the start of the line.

### Step 5 — Strategic tagging (02 logic: per-segment metadata)

After writing each segment's assets, add a **Segment metadata block**:

```
**Pillar:** <Feel Secure | Grow with Ease | Belong Fully>
**Trigger:** <loss aversion | belonging | autonomy | social proof | identity>
**Format:** <checklist | reframe | confession | framework | story>
**Tighter in-point:** ~<timestamp range>, ~<duration>
**Kinetic captions:** mandatory
```

This block serves two purposes: it makes the set cross-check itself (are we covering all three
pillars? all ICP levers?), and it gives Min's production system the metadata to auto-route
clips to the right template slot.

### Step 6 — QA before writing the file

Run these checks on every segment's full output before writing:

- [ ] Every hook avoids "I" as first word
- [ ] All 5 hooks are different archetypes / angles (not rewordings)
- [ ] Caption A / B / C are genuinely platform-different (different rhythm, length, job)
- [ ] Long-form LinkedIn posts use line-break formatting (not dense paragraphs)
- [ ] Long-form Facebook posts feel conversational and peer-level (not corporate)
- [ ] Zero absence-signal violations (no em dashes, no buzzwords, no emojis unless knob ON)
- [ ] Every piece stands alone (no "listen to the full episode" as the only CTA)
- [ ] Tighter in-point flagged for editor
- [ ] Segment metadata block written

Fail any check → fix it before writing.

---

## File header (use this template)

```
# <Episode title> — Candidate Set 05: Hybrid (recommended)
**Client:** <name>  ·  **Method:** Hybrid — 04 segment selection + 01 hooks + 03 platform-native writing + 02 strategic tagging
**Episode:** <slug>  ·  **Generated:** <date>

> One paragraph: which segments were chosen and why (saveability/sends lens), noting which
> template's logic this episode leaned on most. Name the tighter in-point for at least one
> segment so it's clear the editor-facing callout is live.
```
