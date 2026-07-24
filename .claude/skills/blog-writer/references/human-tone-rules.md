# Human-Tone Rules — the anti-AI-tell pre-publish pass

Run every draft through this before the review gate. It merges the 2026 research (`research-synthesis.md` Q4) with Aleem's `content-engine/references/voice-principles.md` mechanics. Goal: reads unmistakably human, not because it games a detector, but because it has real voice, specificity, and rhythm. Detectors have real false-positive rates — fully human text gets flagged too [s56][s62] — so the durable fix is craft, not "humanizer" tools [s54][s55].

## The 4 levers that make text read human [s52][s55][s73]
1. **Authentic first-person voice** — real process, constraints, decisions. Aleem in first person: "I built," "I tried," "I noticed."
2. **Concrete specificity** — replace every vague claim with a number, name, or exact example (voice-principles Specificity Rules). Generic prose is the #1 thing detectors and readers flag.
3. **Varied cadence (burstiness)** — mix long sentences (12-18 words) with short (4-7). Monotone same-length sentences are the top AI tell [s55][s67]. Read aloud to catch it.
4. **A real POV** — take a side, name the standard take you reject (fresh phrasing each time). Neutral = replaceable = AI-sounding.

## Draft in layers, never one polished pass [s55]
One-pass uniformity is what triggers suspicion. (1) idea dump, (2) organize + add evidence/examples, (3) a final pass purely for rhythm + voice. The rhythm pass is non-optional.

## Phrase audit — purge these AI tells [s51][s66]
Banned outright:
- "game-changer", "leverage", "dive into", "unlock", "seamlessly", "elevate", "tapestry", "realm", "landscape", "navigate the world of", "robust", "delve"
- Filler openers: "In today's fast-paced world", "It's no secret that", "In the ever-evolving...", "When it comes to..."
- "It's not just X, it's Y" constructions
- "It's important to note that", "It's worth mentioning", "Needless to say"
- Empty transitions as sentence-starters: "Furthermore," "Moreover," "In conclusion," "Ultimately," — replace with your own connective tissue [s55]
- Symmetry tells: three parallel clauses of equal length in a row; "Whether you're a X, a Y, or a Z"

## Mechanics (hard rules, from voice-principles)
- **No em dashes or en dashes** anywhere in the body — use commas, periods, or short sentences. (Em dashes allowed only in headings.)
- **ASCII only:** straight apostrophes `'` and quotes `"`. Never curly/smart quotes — they corrupt when saved to Google Docs. (`save_content.py` normalizes, but write clean.)
- **No emojis** in a blog.
- Short sentences. White space. No corporate filler.

## The So-What test (per paragraph) [voice-principles]
"Why does this matter to someone reading it at 11pm, tired, 40 tabs open?" If the answer isn't in the paragraph, cut or rewrite. Apply at whole-piece, section, and paragraph level.

## The read-aloud self-check (final gate, before review)
Read the whole draft as if speaking it. Fix anything that:
- sounds like it could be on any agency's blog (add a specific anchor),
- has 3+ sentences of the same length back to back (vary),
- uses a banned phrase (replace),
- states a concept with no consequence or stake (ground it — what breaks if ignored?),
- opens a section with backstory instead of the answer (flip to answer-first).

## What this is NOT
Not detector-gaming, not paraphrase gimmicks, not stripping structure to look messy. Answer-first blocks, tables, and FAQ are structure, not AI tells — keep them. The human-ness lives in the prose *inside* the structure. A well-structured post in a real voice with specific detail passes as human because it is.
