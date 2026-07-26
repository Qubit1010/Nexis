# Job Search + Selection Playbook

Evidence in `research-synthesis.md` Q3 (+ Q4 economics, Q5 timing). Numbers in `upwork-scoreboard.md`.

> **This carries the weight that `projects/upwork-job-scout` was supposed to.** That project is
> inactive (no API access), so job triage is manual. The rubric below is the replacement. Never route
> Aleem to the job scout.

---

## The 60-second triage rubric

Score a job post before spending a single connect. **Two hard gates, then five scored criteria.**

### Hard gates (fail either = skip, no scoring needed)

1. **Payment unverified** → never bid [Q3]
2. **20+ proposals already in**, or post is **24-48h+ old** → the window is closed [Q3][Q5]

### Score the rest, 0-2 each (max 10)

| # | Criterion | 0 | 1 | 2 |
|---|---|---|---|---|
| 1 | **Client hire rate** | <30% (window-shopper) | 30-60% | **60%+** |
| 2 | **Client spend history** | $0 / new | under $1,000 | **$1,000+** |
| 3 | **Post quality** | one line, copy-pasted, or demands a free sample | generic but real | specific problem, real context, clear scope |
| 4 | **Competition + freshness** | 15-20 proposals | 5-15 | **under 5, posted within hours** |
| 5 | **Fit to your actual specialty** | adjacent at best | plausible | dead-centre, you have matching proof |

**Threshold: bid at 7.5/10 or above** [Q8]. Below that, the connect is negative-expected-value —
and if win rate is already low, bidding more only accelerates losses [Q4].

**Boost only if:** score is 8+, job value is **$1,000+**, and you have directly relevant proof [Q4].

---

## Reading the post for red flags

**Skip outright** [Q3]:
- One-sentence or obviously copy-pasted posts
- Any request for free, project-specific samples (predatory)
- Unverified payment

**"Anxiety signals"** — phrasing implying a bad prior experience ("last developer disappeared",
"need someone who actually communicates") or excessive urgency. These reliably predict scope creep
[Q3]. Not an automatic skip, but price and scope defensively, and expect to need
`upwork-reply-drafter`'s change-control moves early.

**Read reviews for content, not stars** [Q3]:
- Green: specific praise for clear communication and prompt payment
- Red: any mention of scope creep or payment disputes

---

## Finding the jobs in the first place

**Saved searches beat feed-scrolling** [Q3]. Build narrow ones and check them, rather than
refreshing a general feed.

- Use boolean exclusions to strip noise: `"React" -junior`, `"automation" -Zapier` if you don't want
  the low end.
- Filter on: payment verified, client hire rate 60%+, minimum budget matching your rate floor.
- Sort for recency and bid into the **0-5 minute window**; if you miss it, the **12-15 minute**
  rebound beats the 5-10 minute valley [Q5].

**The structural point:** speed only pays if the search is already narrow. Broad searches make you
fast at bidding on the wrong jobs.

---

## Budget on the post is an anchor, not a ceiling

If the scope justifies more, propose the real price with a one-line justification rather than
anchoring to their number [Q3]. Do not treat a low posted budget as automatic disqualification —
treat it as a scoping conversation.

The actual negotiation wording is **`upwork-reply-drafter`** territory (its Q2 covers holding rate
without discounting). This skill decides *whether to engage*; that one handles *what to say*.

---

## Output format for a triage request

When Aleem pastes a job post and asks whether to bid:

1. **Verdict line** — Bid / Bid + Boost / Skip, and the score out of 10.
2. **The scoring table** — the five criteria with the score and the one-line reason for each.
3. **Gate check** — call out explicitly if a hard gate failed (that ends it).
4. **If bidding:** the one angle that wins it, and the specific proof point to lead with. Then hand
   off: "want `upwork-proposal-generator` to write it?"
5. **If skipping:** what would have to be different for it to be worth a connect.
