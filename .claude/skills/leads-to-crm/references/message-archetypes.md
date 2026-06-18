# Touch 1 Message Archetypes (distilled for leads-to-crm)

This is the condensed opener guidance the Haiku generator is grounded in. The
canonical, fully-sourced version lives in the **sales-playbook** skill
(`.claude/skills/sales-playbook/frameworks/opener-archetypes.md`). Read that when
you want the citations or to evolve the prompts. This file exists so the message
generation has a self-contained reference without loading the whole playbook.

## Why rotate archetypes

Aleem's old scripts opened with the same skeleton every time (`Hey [Name], it
looks like [X], curious how you handle [Y]?`). Founders who get 50+ DMs a week
read that as cadence and delete on sight. The fix: rotate across a few distinct
opener patterns so a batch of 30 looks like 30 different people. `messages.py`
picks one archetype per lead, weighted by whether the lead has a usable bio/post
signal.

## The archetypes used here

**Anti-pitch (Josh Braun)** — Open by *removing* pressure with a soft
disqualifier ("probably not a fit, but had to ask") then one genuine question
about a specific manual task they likely still do by hand. The disqualifier is
the mechanism; don't soften it into a compliment. Works with minimal signal, so
it's the fallback.

**Specific observation** — Reference one concrete, real detail from their bio or
recent post (a phrase, their model, their niche), then ask one curious question
about their operations. Observation over flattery. No "I love your content."

**Genuine operational question** — Skip the observation, ask one sharp peer-level
question about how they handle a specific workflow at their stage. Founders
answer peer questions and ignore vendor questions; this bypasses the "what does
he want?" filter.

**No-pitch connection note (LinkedIn)** — Reference their post/role specifically,
say it matches a pattern you see with similar teams, say it'd be useful to
connect, end with "No pitch." Only works if you actually don't pitch in the note;
the value drop waits for after they accept.

## Non-negotiable rules (enforced in the system prompt)

1. **No pitch.** Never name NexusPoint, services, "AI automation", or websites in Touch 1.
2. **One ask max.** A single question OR a connect request, never both.
3. **No em-dashes**, ever. Comma or period. (They corrupt downstream and read as AI.)
4. **Count the "I"s** — more than two means rewrite. Make it about them.
5. **Length:** Instagram DM under ~80 words / 400 chars; LinkedIn note under 300 (aim < 280).
6. **Banned openers** (instant delete): "I came across your profile", "hope this
   finds you well", "love your content", "I was impressed", "Bro", "I wanted to reach out".
7. Instagram: at most 1 emoji, only if natural. LinkedIn: no emojis.

## Worked references

For full end-to-end examples (cold DM through to close), see the sales-playbook
worked examples: `references/worked-example-instagram.md` and
`references/worked-example-linkedin.md`. Those show what "good" looks like in
context and are the gold standard the generated Touch 1 should resemble.
