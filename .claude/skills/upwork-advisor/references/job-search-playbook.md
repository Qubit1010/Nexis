# Job Search + Selection Playbook

Evidence in `research-synthesis.md` Q3 (+ Q4 economics, Q5 timing). Numbers in `upwork-scoreboard.md`.

> **This carries the weight that `projects/upwork-job-scout` was supposed to.** That project is
> inactive (no API access), so job triage is manual. The rubric below is the replacement. Never route
> Aleem to the job scout.

---

## The 60-second triage rubric

Score a job post before spending a single connect. **Two hard gates, then five scored criteria.**

### Hard gates (fail any = skip, no scoring needed)

1. **Posted more than 10 minutes ago** → skip. Validated on Aleem's own 905-proposal dataset:
   **7.1% hire rate within 10 min vs 1.3% after (5.3x, p = 0.000028)**. 70% of his historical
   proposals fell on the wrong side of this line. See the Live Query Addition in
   `research-synthesis.md` and `references/Upwork/upwork-bidding-protocol-2026.md`.
2. **Payment unverified** → never bid [Q3]
3. **20+ proposals already in** → the window is closed [Q3][Q5]

> **Why late bids feel fine but aren't:** late proposals still earn interviews at a normal rate, they
> just close at 10% instead of 66%. Interview rate alone will never reveal this. Judge on hire rate.

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

**A quota and the speed window are structurally incompatible.** A daily target means bidding when
*you* sit down; the window means bidding when the *job* appears. Alerts fix this, discipline does
not. Quota the screening (review 15-20 posts/day), never the sending.

### Timing by hour of day: a validated negative result

**Do not schedule bids around US business hours to improve conversion.** Measured on 905 real
proposals, hire rate grouped by US client window came out at 3.5% / 3.4% / 3.4% / 1.4% — three of
four windows within 0.1 points. Hour of day is close to noise.

What *does* vary by hour is **supply**: how many fresh jobs exist to bid on. For a PKT-based
freelancer targeting US clients, job-posting volume is densest around **PKT 20:00-01:00**
(US ET 10:00-15:00). Be alert-ready then because there is more to catch, not because the odds per
bid improve.

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
