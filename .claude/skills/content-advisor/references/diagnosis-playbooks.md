# Diagnosis playbooks — why content is not working

Load this in **diagnose** mode.

The job is to find the **root cause**, not to list everything that could be improved. A
diagnosis returning twelve findings has not diagnosed anything, and nothing on a twelve-item
list gets done.

**"Nothing is wrong with the content" is a legitimate finding**, and in this subject it is
the correct one more often than in any other. Content that nobody distributed and content that
nobody wanted look identical from the inside.

---

## The five root causes

Ordered by how often each is genuinely the answer, which is roughly the inverse of how often
each gets blamed.

| # | Root cause | Tell | Fix owner |
|---|---|---|---|
| 1 | **It was published, not distributed** | Traffic is flat from day one. No spike, no decay curve, just a floor. The plan has no day-one/week-one/day-thirty rows | `content-strategy` (distribution plan) |
| 2 | **It answers a question nobody asked** | Topics trace to the category or the competitor set rather than to the audience. Passes the swap test - a competitor could publish it unchanged | `strategic-foundation --mode persona`, then `content-strategy` |
| 3 | **The measurement is wrong, not the content** | The client is comparing across platforms, reading open rates post-2021, treating attribution as causal, or comparing completion rates across different video lengths | This skill. Fix the number before touching the content |
| 4 | **Cadence exceeded capacity, so quality collapsed** | Output is regular and thin. Or it was regular for four months and then stopped | `content-strategy` (capacity sizing) |
| 5 | **The format is wrong for the job** | Teaching content in a format that cannot teach; a case study told as a listicle; a complex argument in 60 vertical seconds | `content-advisor` spec mode, then `content-production` |

---

## Symptom → cause → route

| Symptom | Most likely cause | Check first | Route |
|---|---|---|---|
| "We publish constantly and get nothing" | 1, then 4 | Is there a distribution plan with owners? What happened in week one of the last three pieces? | `content-strategy` |
| "Engagement dropped" | 3 | Did the metric definition or denominator change? Did the platform restate anything? | this skill |
| "Our competitor's content goes viral" | 3 | Match on cascade size before comparing `[C]` [s14][s16] | this skill |
| "Views are down but the content is better" | 3 or 1 | Which view definition? Same placement? Same distribution? | this skill |
| "The blog gets traffic but no leads" | 5, then 2 | Is the funnel stage of the content matched to the CTA? | `content-strategy` |
| "Our videos have terrible completion" | 3 | How long are they? Completion is duration-biased by construction `[C]` [s31] | this skill |
| "Open rates fell off a cliff / spiked" | 3 | Apple MPP. Was the comparison period across 2021? Different Apple Mail share? | this skill |
| "Nobody watches past the first few seconds" | 5 | Is the opening doing the format's job? Check the spec | `content-production` |
| "We tried a podcast and it went nowhere" | 4, then 1 | Was it a standing weekly commitment the team could hold? | `content-strategy` |
| "Content stopped after four months" | 4 | Capacity, and approval latency specifically | `content-strategy` |
| "Everything sounds the same / generic" | 2 | Run the swap test. Does `14-brand-voice.md` exist? | `brand-voice`, then `content-production` |
| "AI content is not performing" | 2 or 5 | Almost never about AI. Check topic sourcing and format fit first | `content-strategy` |
| "We are not showing up in AI answers" | not this skill | | `seo-authority-ai` |
| "We rank but nobody converts" | not this skill | | `copy-conversion` |

---

## The gates

Run these before diagnosing anything else. Either one failing is the finding.

**The swap test.** Replace the client's name with a competitor's. If the piece still reads as
true, the problem is root cause 2 and no amount of format work will fix it.

**The distribution test.** Ask what happened in the seven days after the last three pieces
published. If the answer is "we posted it", the problem is root cause 1. This is the most common
diagnosis in this subject and the one clients least expect, because production feels like the
hard part.

**The measurement test.** Ask what the number counts. If the client cannot say - and most
cannot, because no dashboard tells them - stop and fix that first. Diagnosing content from a
number that does not mean what everyone assumes is how a whole strategy gets rebuilt for no
reason.

---

## What a diagnosis hands back

1. **The single most likely cause**, with what evidence would confirm it.
2. **What to check next**, concretely - not "review your analytics" but the specific number and
   where to read it.
3. **One fix**, routed to whichever skill owns it.

Not a list. If two causes are genuinely tied, say they are tied and give the cheaper test first.

**If the honest answer is that the content is fine and the operation around it is not, say
that.** It is usually true, it is usually unwelcome, and it is the reason to have run a
diagnosis rather than a critique.
