# When a pack claim conflicts with Nexis's own corpus

The marketing-skills pack states some numbers as flat fact that Nexis's own research-backed
skills have already investigated and rejected as unsourced. The clearest case found while
building this skill:

`.claude/skills/marketing-skills/social/SKILL.md` states: *"Captions increase watch time by
25-40%. Most social video is watched without sound."*

`content-engine` v1's `references/platform-formats.md` explicitly bans this exact category of
claim by name — `content-advisor` "refuses the 85%-on-mute claim outright" as unsourced, and the
25-40% captions figure has no more backing than that one does.

## The rule

Apply Nexis's own standing norm to every pack-sourced number, not just this one: **give the
direction, attribute the number, never assert it as fact.**

When the marketing-skills pack states a figure and either:
- `social-media-advisor` or `content-advisor` directly contradicts it, or
- neither has a confirmed source for it either way,

then label it explicitly as a "marketingskills pack convention" rather than presenting it as
verified — something like "the pack's convention is that captions matter for watch time; the
exact percentage isn't independently confirmed" rather than restating the 25-40% as settled.
Where the two sources are in direct conflict, defer to the Nexis corpus's classification — it's
research-backed with citations; the pack's numbers are generic marketing lore with none.

## Lower-risk pack numbers

`social/references/platform-limits.md`'s figures (character counts, hashtag caps, official
platform limits) are mostly mechanical facts rather than engagement claims, so they carry less
of this risk — but spot-check against `platform-specs/<platform>.md` where both cover the same
platform before using either as ground truth, since the two were compiled independently and could
have drifted.

## Why this matters here specifically

v2 exists to test a different methodology honestly. If it silently imports the pack's
unsupported engagement claims as if they were fact, any quality gap the A/B test surfaces could
just be "v2 asserts made-up numbers, v1 doesn't" — a finding about honesty discipline, not about
which writing approach is actually better. Keeping this rule intact is what keeps the comparison
about the thing it's supposed to be about.
