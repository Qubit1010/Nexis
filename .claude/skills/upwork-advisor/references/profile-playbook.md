# Profile Playbook

Evidence in `research-synthesis.md` Q1 + Q2. Numbers in `upwork-scoreboard.md`.

## The split that governs everything

The profile does two separate jobs, and most people optimize the wrong half:

| Element | Job | Audience |
|---|---|---|
| Title, first 2 overview lines, **15 skill tags** | **Get found** (search + AI matching) | The algorithm |
| Portfolio, photo, video, rest of overview | **Convert the click** | A human who already landed |

Fixing the portfolio when nobody sees the profile is wasted work. Diagnose which half is broken
first: no profile views = search problem, views but no invites = conversion problem.

---

## Audit sequence (run in this order)

### 1. Title — three layers
`general service | specific specialty | primary tools` [Q1]

Weak: "Full-Stack Developer & AI Enthusiast"
Strong shape: "AI Automation Engineer | Agentic Workflows | Claude, Python, n8n"

Check: does it contain the words a client would actually type? Does it read specialist, not
generalist? The algorithm favors specialists [Q2].

### 1b. Hard platform constraint: NO external links in the overview

**Upwork rejects the overview if it contains any external URL.** The error is: "Links to external
websites are not allowed in your profile overview. You can add work samples and portfolio links in
the Portfolio section on this page."

This bites the obvious move of listing recent client sites as proof. Never put a domain in the
overview, not even bare (`example.com` without `https://` still trips it).

**Instead:** describe the work by type ("Recent builds: trading education platforms, media agency
sites, SaaS products") and let the Portfolio section carry the actual links. That section wants them
anyway, and a portfolio piece with a visual and a measurable outcome converts better than a bare
domain in a wall of text.

*Source: hit live 2026-07-26 while pasting a rewritten overview. Not in the research corpus, which
has no coverage of Upwork's overview content-validation rules.*

### 2. First two lines of the overview
This is a **search preview**, not an introduction [Q1][Q5]. It must carry:
- who you help
- the outcome you deliver
- **one quantitative proof point**

Kill: "I am a passionate developer with X years of experience..." Self-centered "I" openers and
generic greetings underperform in the same way they do in proposals [Q5].

### 3. Skill tags — exactly 15
Mirror the vocabulary from the job posts you actually want [Q1][Q2]. This is not a place to list
everything you can do: **irrelevant tags dilute relevance and cause de-ranking** [Q2]. Cutting tags
is often a net gain.

### 4. Completeness (baseline, not bonus)
100% complete, professional well-lit headshot, availability status active, verified skill
certifications [Q1][Q2]. **6+ portfolio items** is the completeness signal for ranking [Q2]; 3-5 is
the quality floor [Q1]. If forced to choose, quality first, then add to 6+.

### 5. Portfolio pieces — the four-part shape
Each piece carries a visual, the client's problem, your specific solution, and a **measurable
outcome** [Q1]. A screenshot with a title is not a portfolio piece.

### 6. Intro video
30-60 seconds [Q1]. Trust-building for the click-through half only, so it never fixes a visibility
problem.

---

## The invitation lever (new in 2026)

Discovery is increasingly push, not pull: an AI agent builds shortlists and issues invites, so
**invite-to-hire ratio is a signal** [Q2].

- Accept only high-probability invites.
- **Decline poor-fit invites immediately, with an explanation.** This trains the matcher on your
  actual expertise and improves future matches [Q2].
- Ignoring invites is the worst option: it hits both responsiveness and the ratio.

Responsiveness generally: log in daily, keep availability current, respond **within a few hours** or
take a speed penalty [Q2].

---

## ⚠️ Verify before advising: specialized profiles

One source says specialized profiles were **phased out in May 2026**, with the main profile
dynamically surfacing relevant work instead [Q1]. That date is already past, and it's a single
source for a structural change.

**Do not give specialized-profile advice from this file alone.** Ask Aleem what he actually sees in
his account, or check Upwork's live support docs. Then correct this file and the synthesis.

---

## Audit output format

When auditing a real profile, return:

1. **Verdict** — one line: which half is broken (visibility or conversion), and the single biggest fix.
2. **Element-by-element table** — Current / Problem / Rewrite, for anything that fails the checks above.
3. **The rewrite itself** — actual title and first-two-lines copy, not a description of what to write.
4. **Ranked fix list** — highest-leverage first, with the signal each one moves.

Offer the Google Doc export (`scripts/save_upwork_plan.py`) only for a full rewrite, not a spot check.
