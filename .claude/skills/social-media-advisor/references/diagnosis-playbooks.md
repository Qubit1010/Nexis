# Diagnosis playbooks

Symptom to cause to route. **Diagnose before prescribing**, and in this subject that means
ruling out two boring explanations before entertaining any interesting one.

**The two boring explanations, always checked first:**

1. **A measurement change.** The metric was redefined, the date range shifted, or the number was
   never comparable in the first place. YouTube redefined a "view" on **24 August 2026** `[P*]`
   [s198]; there is no single engagement-rate formula `[C]` [s1]; and creators systematically
   misjudge who actually sees their content `[C]` [s52].
2. **A structural or platform-wide change.** Exposure is allocated by a ranker `[C]` [s18][s38],
   attention concentrates by cumulative advantage `[C]` [s34][s56], and platforms change ranking
   without notice.

Only after both are excluded is it worth discussing the content.

---

## "Our reach dropped"

**Ask in this order:**

| Step | Question | If yes |
|---|---|---|
| 1 | Did the metric or date range change? | Stop. It is a measurement artifact. `[P*]` [s198] for YouTube specifically |
| 2 | Did it drop for everyone, or only this account? | Platform-wide means it is not a content problem. Check the platform's newsroom |
| 3 | Is the account newly ineligible for recommendation? | **Instagram exposes this directly in Account Status** `[P*]` [s311]. Check before theorising |
| 4 | Did the content mix change toward reposts or recycled material? | Three platforms now deprioritise unoriginal content `[P*]` [s314][s193][s284] |
| 5 | Did posting cadence or format change? | Correlational at best. Do not assert causation |
| 6 | None of the above | Say the cause is not identifiable from available data, and name what would need measuring |

**Never open with "shadowban".** Reduced distribution is real and platforms acknowledge
restricting rule-breaking content `[C]` [s29], but silent suppression of ordinary marketing
accounts has no evidence. See `what-not-to-do.md`.

**Never treat a single post as a signal.** Outcomes are substantially luck-driven `[C]` [s53].

---

## "Our engagement died"

First: **which engagement?** There is no standard formula `[C]` [s1], so establish what is being
counted before diagnosing. A change in a platform's own metric definition looks identical to a
performance collapse.

Then separate **reach** from **engagement rate**. Reach falling with a stable rate is a
distribution problem (above). A stable reach with a falling rate is an audience or content
problem.

Then check whether the wrong thing is being optimised. Engagement and business value diverge
`[C]` [s71], and liking and commenting have different drivers `[C]` [s68], so an "engagement
drop" driven entirely by likes may be irrelevant to the outcome the client cares about.

---

## "We're not growing / followers are flat"

**Reframe first.** Growth and reach are different problems: virality is untied to audience size
`[C]` [s55], and follower count relates to engagement non-monotonically `[C]` [s5]. A client
whose reach is fine does not necessarily have a problem worth solving.

Then:

- **Is flat growth actually the structural default?** Cumulative advantage concentrates attention
  regardless of behaviour `[C]` [s34][s56]. Slow growth from a small base is the expected case,
  not the failure case.
- **Is the platform right for the audience?** Audiences overlap heavily across platforms `[C]`
  [s2], so a second platform may be reaching the same people.
- **Is this a cold-start problem?** Instagram states it added ranking input favouring smaller
  creators `[P*]` [s314]; TikTok is recommendation-first `[P*]` [s310]. LinkedIn is the hardest
  cold start of the deep five.

---

## "Should we be on [platform]?"

Answer from `07-strategic-foundation.md` and `08-audience-persona.md` if a client slug exists,
never from platform popularity. Then:

1. **Is the audience there, and there in a buying frame?** Population reach is not intent, and a
   population statistic is not a performance claim.
2. **Does `13-brand-strategy.md`'s "what this rules out" section exclude it?** A platform can be
   wrong for a brand however well it performs.
3. **Is the native register reachable in this voice** (`14-brand-voice.md`)?
4. **Can they sustain the production?** Most platform failures are capacity failures.
5. **Read the "Fails when" section** of the relevant `platform-specs/` file.

**Recommend against most of them.** A list of ten platforms is not advice. If the honest answer
is one platform plus a Group, say that.

---

## "Is this statistic real?"

Route to `what-not-to-do.md` and follow the factcheck procedure in `SKILL.md`. The honest verdict
is usually "no traceable primary source", not "false".

---

## "Marketing-advisor told me X"

Name the disagreement rather than overruling or deferring. That skill's platform numbers are
practitioner-tier, `content-advisor` and `copy-conversion` already classify them as unsourced
convention, and its `[sN]` citations currently resolve to nothing because its `sources.json`
does not exist. Give both readings and a recommendation. See `what-not-to-do.md` Part 5.

---

## When the answer is "not knowable from here"

Say it, and say what would make it knowable. Three legitimate versions:

- **The magnitude is not published.** Audits establish that exposure is reallocated without
  quantifying how much `[C]` [s11][s18]. Direction without magnitude is a real answer.
- **The corpus is thin here.** Reddit, Threads and Bluesky. See `platform-specs/secondary.md`.
- **It needs a live check.** Platform behaviour older than roughly two quarters. Route to
  `notebook-live-query.md`.
