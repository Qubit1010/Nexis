# Case Study Template — Section-by-Section Specification

This reference defines every section of the case study format, its purpose, formatting rules, and examples from the two canonical case studies. Follow this structure exactly when generating.

---

## Section 0: Title + Metadata

### Title
```
# [Project Name]: How [Who] Built [What It Does — Outcome-Focused]
```

The title follows a strict formula: name the thing, say who built it, say what it accomplishes. The outcome is the hook — it should make a prospect curious.

**Examples:**
- `# Daily News Brief: How NexusPoint Built an AI-Powered Intelligence Dashboard for $0.03 a Day`
- `# Lead Gen Pipeline: How NexusPoint Built an Automated Prospect Intelligence System`

### Metadata Line
```
**Category:** [Internal AI System / Client Project / Business Intelligence / etc.]
**Built by:** [Company or Person]
**Powered by:** [Primary tech, comma-separated — 4-6 main pieces]
```

The category should reflect what the system *is*, not what it does. Use one of these or coin something similar: Internal AI System, Client Acquisition, Business Intelligence, Content Production, Client Project, Automation Workflow.

**Example:**
```
**Category:** Internal AI System / Business Intelligence
**Built by:** NexusPoint
**Powered by:** Next.js 16, OpenAI (gpt-4o-mini + gpt-4o), SQLite, NewsAPI, Hacker News, RSS
```

### Separator
```
---
```
Use a horizontal rule between metadata and the first section. All major sections after also use `---`.

---

## Section 1: The Problem

### Purpose
Frame why this project exists. Don't just describe the problem — make the reader feel it. Someone reading this should think "yeah, I've dealt with that."

### Structure
- Opening paragraph: The universal version of the problem (2-3 sentences)
- "The default approach is..." paragraph: What most people do, and why it fails
- Exactly **4 specific problems**, numbered 1-4
- Each problem: **bold label** followed by 1-2 sentences of detail

### Rules
- Always exactly 4 problems. Not 3. Not 5.
- Problems must be specific to this domain. "It's slow" is too vague. "100+ stories break daily across 5 sources with no way to filter signal from noise" is specific.
- Each problem builds on the previous — they should feel cumulative, not like a random list.

### Example (from Daily News Brief)
```
Anyone who works in AI, tech, or a fast-moving industry faces the same daily problem: there's too much to read and no way to know what actually matters.

The default approach is to check Twitter, skim newsletters, and hope something important surfaces. But that process is slow, scattered, and inconsistent.

Four specific problems:

1. **Volume.** 100+ AI and tech stories break daily across NewsAPI, Hacker News, RSS feeds, and research journals. Nobody has time to read all of it.
2. **Duplication.** The same story gets published on TechCrunch, picked up on Hacker News, syndicated to three newsletters. You see it four times or zero times — never exactly once.
3. **No synthesis.** Aggregators show you headlines. They don't tell you what the pattern is, what's rising, or what the week's signal is across all that noise.
4. **No action.** Even a good summary doesn't tell you what to *do* with the information — what to write about, what angle is missing, what the community is already discussing.
```

---

## Section 2: What It Is

### Purpose
The elevator pitch. After reading this, someone should understand exactly what was built and what it produces.

### Structure
- One paragraph describing the system at a high level
- A bullet list of concrete outputs (4-7 items)
- A closing sentence about permanence/availability

### Rules
- Use specific numbers ("6 categorized coverage areas", not "several categories")
- The bullet list names what the system *produces*, not what it *does*
- End with a sentence about storage, availability, or integration

### Example (from Lead Gen Pipeline)
```
The Lead Gen Pipeline is a Python-based command-line system that takes a raw list of prospects and runs them through five sequential stages: import, score, enrich, personalize, and export.

By the end of the pipeline, every qualified lead has:
- A score from 0-100 across five qualification layers
- A tier assignment (HOT / STRONG / WARM / REJECTED)
- A verified email address
- Website intelligence (CMS, performance score, tech stack, SSL status)
- Company news and funding signals
- LinkedIn profile data (for HOT leads)
- Three personalized outreach hooks
- Full multi-touch sequences for cold email, LinkedIn, and Instagram — ready to send

One pipeline. One command. Everything needed to start outreach.
```

---

## Section 3: Pipeline / Steps / Stages

### Purpose
The meat of the case study. Walk through how the system works, step by step, with enough detail that a technical reader understands the architecture and a business reader understands the value.

### Structure
Each step is a `###` heading. Within each step:
- What happens in this step (1-2 sentences)
- The mechanism: how it works, what tools/APIs are involved
- Specifics: numbers, thresholds, decision rules
- The output of this step

### Rules
- Number the steps: `### Step 1 — [Name]`, `### Stage 2: [Name]`
- Every step mentions a concrete number (articles processed, API calls made, time taken, cost incurred)
- Decision rules are explicit: "WARM leads get email only. HOT leads get all 3 channels + Proxycurl."
- Use tables where comparison is useful (tier definitions, category mappings, scoring weights)
- Sub-bullets for component breakdowns

### Step naming patterns
For pipelines: `### Step N — [Action Verb + Noun]`
For stages: `### Stage N: [Noun Phrase]`
For sections within steps: `#### [Sub-name]`

---

## Section 4: What's Built and Working

### Purpose
A comprehensive feature inventory. This is the credibility section — it demonstrates that the system is real and complete.

### Structure
A markdown table with two columns: `Feature` and `Status`.

### Rules
- Status values: `Live`, `In Progress`, `Planned`
- Group related features together
- Be granular — "Multi-source fetching (NewsAPI + Hacker News + 5 RSS feeds)" is one row, "Title-based deduplication with engagement merging" is another
- 10-20 rows is typical
- Don't pad with obvious things. Only list features a prospect would care about.

### Example
```
| Feature | Status |
|---------|--------|
| Multi-source fetching (NewsAPI + Hacker News + 5 RSS feeds) | Live |
| Title-based deduplication with engagement merging | Live |
| Keyword-based categorization (6 categories) | Live |
| Per-category Haiku analysis (insight + TL;DR + sentiment + relevance) | Live |
| Cross-category Sonnet synthesis (5 trends + 10 ideas + sentiment) | Live |
| 7-day trend momentum tracking + sparklines | Live |
| Full-stack Next.js dashboard (10 sections) | Live |
| Article filtering by category + sentiment tag | Live |
| Full-text search across articles and TL;DRs | Live |
| Google Sheets integration for content ideas | Live |
```

---

## Section 5: Cost Breakdown

### Purpose
Show the economics. Prospects want to know this isn't expensive to run.

### Structure options

**Option A: Pipeline cost table** (for systems with multiple steps/calls)
```
| Step | Model/Service | Units per Run | Cost |
|------|--------------|---------------|------|
| [Step name] | [Service] | [N calls / tokens] | ~$X.XXX |
| ...
| **Total per run** | | | **~$X.XX** |
```
Follow with a sentence contextualizing the monthly/annual cost.

**Option B: Per-unit cost table** (for systems processing items/leads)
```
| Tier | Component 1 | Component 2 | Component 3 | Total |
|------|------------|------------|------------|-------|
| [Tier name] | ~$X.XX | ~$X.XX | ~$X.XX | ~$X.XX |
```
Follow with a sentence about scale economics.

### Rules
- Use real numbers from the brief. If a number isn't available, describe the cost model and flag it: "*(Actual cost depends on usage — ask for the specific number if you have it.)*"
- Contextualize: "$0.03/day" is meaningless without "under $1/month"
- Mention free tiers and fallbacks — prospects care about operational cost
- Be honest about what costs money and what doesn't

---

## Section 6: The Architecture

### Purpose
Technical specification. A developer should be able to understand the stack at a glance. A business reader should see it's built on real tools.

### Structure
```
**Frontend:** [Stack]
**Backend:** [Stack]
**Database:** [Stack]
**AI:** [Models via Provider]
**Data sources:** [List]
**Integrations:** [List]

**Commands:**
```
[command 1]  → [what it does]
[command 2]  → [what it does]
```

**Database tables / Key files:** [Brief description of data model or file structure]
```

### Rules
- Bold labels for each layer
- The commands block is a code fence showing the CLI surface
- Adapt the architecture labels to what makes sense: a CLI tool won't have "Frontend", a web app will
- Include concurrency or infrastructure notes if relevant ("4 parallel enrichment workers")

---

## Section 7: End-to-End Walkthrough

### Purpose
Make it concrete. Follow a specific run from start to finish with real-ish numbers. This is the most readable section — it turns the architecture into a story.

### Structure
- A numbered sequence of events (6-10 steps)
- Each step describes what happens at that point in a real run
- Specific numbers at every step: "142 raw articles come in", "Score: 8 HOT, 14 STRONG, 21 WARM, 13 REJECTED"
- The final step shows the output or result

### Rules
- Use past or present tense consistently
- Numbers should be realistic and internally consistent (if step 2 says 94 unique articles, step 3's category counts should add up to ≤94)
- Mention edge cases briefly (articles that don't categorize, leads that get rejected)
- The last step shows the user-facing outcome: what the person sees or does

### Voice
Not technical documentation. This reads like someone walking you through a demo:
> "142 raw articles come in. Dedup removes 48 duplicates (34% rate). 94 unique stories remain."
> Not: "The deduplication module processes the input array and returns a filtered collection."

---

## Section 8: The Prospect Takeaway

### Purpose
The soft pitch. Reframe this specific project as a reusable architecture pattern. A prospect reading this should think: "If they can build this for themselves, they can build something like it for me."

### Structure
- Opening paragraph: what this system is to the builder (internal tool, engine, dashboard)
- "The architecture is not specific to [domain]." paragraph: list 3-5 other industries or use cases where the same pattern applies
- Closing paragraph: the call to action, framed as a question or observation about manual processes

### Rules
- Never hard-sell. The case study itself does the selling.
- The industry applications must be plausible. Don't stretch — if the system is a news aggregator, say it works for "any business that needs to stay ahead of a fast-moving information landscape," not "any business."
- End with the implication: manual processes exist that this pattern can replace.

### Example pattern
```
[System] is [Who]'s internal [purpose]. [One sentence about how it's used.]

The architecture behind it — [list 2-3 key architectural patterns] — is not specific to [domain]. The same system works for:

- [Industry/use case 1 with concrete example]
- [Industry/use case 2 with concrete example]
- [Industry/use case 3 with concrete example]
- [Industry/use case 4 with concrete example]
- [Industry/use case 5 with concrete example]

[Closing observation about what this replaces or enables.]
```

---

## Section 9: Footer

```
*Built and maintained by [Who]. Last updated: [Month Year].*
```

Always italicized. Always single line. Month and year only — no day.

---

## Global Writing Rules

1. **Numbers over adjectives.** Replace "fast" with "under 60 seconds," "cheap" with "$0.03 per run," "a lot" with "142 articles."
2. **No invented numbers.** If a stat isn't in the brief, either omit it or flag it. Never guess.
3. **Consistent voice.** Authoritative, direct, no fluff. Write like a founder explaining their system to a peer.
4. **Section balance.** Each section gets roughly proportional treatment. Don't write 500 words on The Problem and 50 on The Architecture.
5. **Internal consistency.** Numbers across sections must agree. If the cost table says $0.03/run and the walkthrough says $0.05, that breaks trust.
6. **No emojis, no em dashes.** Hyphens only. This matches the house style.
7. **Bold for emphasis, not ALL CAPS.** Use `**bold**` for key terms and takeaways.