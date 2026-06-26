# Template 01 — social-media-skills (reverse-engineer + voice-match)

**Angle:** Treat the transcript like raw footage and reverse-engineer the strongest
standalone moments, then run them through proven social-media-skills craft: archetype hooks,
voice-matching on absence signals, one-sentence-per-line rhythm, and a scoring QA gate.

**Source methods:** `social-media-skills` plugin — `reels-scripting`, `hook-generator`,
`voice-builder`, `post-formatter`, `post-scorer`. (Plugin at
`C:\Users\qubit\.claude\plugins\marketplaces\social-media-skills`.)

Read `references/output-spec.md` for the exact shape. Read the client's main voice file for
limits and absence signals. This template defines *how to fill that shape*.

---

## Method

### 1. Segment = strongest standalone hook moment (reverse-engineer)
Scan the transcript for lines that already *are* a hook — a screenshot-worthy claim, a candid
admission, a contrarian truth. The segment is built **around** that line, not around topic
order. Cut 3-5 where the quotable line can carry a clip on its own. Prefer moments with built-in
tension (a confession, a myth being broken, a number).

### 2. Hooks via the 6 archetypes
For each segment, write the 5 hooks by rotating these archetypes (use the one that fits the
moment, don't force all six):

1. **Number-led** — "3 things nobody tells you about leaving corporate for real estate."
2. **Contrarian** — "Real estate is not an escape. It's a harder kind of responsibility."
3. **Transformation** — "From corporate burnout to top producer. Here's the part people skip."
4. **Authority** — "I've brokered thousands of agents. This is who actually makes it."
5. **Admission** — "My boss is a real bitch. Then I remember the boss is me."
6. **Future-shock / stakes** — "Quit without 6 months of runway and the math breaks you."

Rules from `hook-generator` / `reels-scripting`:
- **Never open with "I"** as the first word (weak scroll-stop). Lead with the tension or the "you."
- Keep within the hook word limit. Front-load the high-impact word.
- The 5 hooks should be genuinely different *angles* on the same clip, not 5 rewordings.

### 3. Voice-match on absence signals (voice-builder)
Match Brenda by what she *avoids* as much as what she says. Run every line against the voice
file's absence signals. The fastest tell of a fake voice is a buzzword or an em dash she'd
never use. Mirror her cadence: calm, grounded, candid, Mama-Bear protective.

### 4. Captions + posts with post-formatter rhythm
- One idea per line, generous line breaks, no wall of text.
- Vary sentence length: short, short, longer. No three-same-length clauses in a row.
- Captions self-contained; the 3 are different angles (e.g. story / tactical / direct-to-agent).

### 5. post-scorer QA gate (before you output)
Self-score each piece: does the hook stop the scroll? does it stand alone? any absence-signal
violation? If a piece fails, rewrite it before writing the file. Don't ship the first draft.
