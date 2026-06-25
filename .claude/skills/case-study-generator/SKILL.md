---
name: case-study-generator
description: Generate detailed, prospect-ready case studies from brief project info. Use this skill whenever the user mentions "case study", "write up [project/skill/tool]", "document this as a case study", "create a write-up for [something]", "I want to showcase [something]", or describes a project and says "make it look like the daily brief case study" or "format like lead gen case study". Also triggers for phrases like "turn this into a case study", "write a deep dive on", or "I need a detailed write-up of [project]". Even if the user just says a project name and "write it up", invoke this skill — it exists to turn sparse input into polished output.
---

# Case Study Generator

Generate detailed, prospect-facing case studies from brief project descriptions. Follows the exact format proven by `docs/daily-news-brief-case-study.md` and `docs/lead-gen-case-study.md`.

The case study format is designed to sell by showing — it walks through the problem, the system, the numbers, and the reuse potential. Every section builds the case that this was built thoughtfully and can be adapted for a client.

## Workflow

### Step 1: Assess the Input

Read the user's brief. Determine what's already covered and what's missing:

**Minimum needed to generate:**
- Project/tool name
- One-sentence description of what it does
- Tech stack (at least the main pieces)
- Who built it (person, team, or company)

**Nice to have (generates a stronger case study):**
- Specific numbers (cost per run, time saved, articles processed, leads scored)
- Pain points the project solves
- Real examples of output or usage
- Commands or workflow steps

If the brief is sparse (just a name + one-liner), ask 2-4 targeted questions to fill the gaps before generating. Don't ask everything — just what's most load-bearing for the narrative. Do this in the same turn as the assessment: "I can generate this. A few things that'll make it stronger: [2-4 specific questions]."

If the brief is detailed (a paragraph or more with context), go straight to generation.

### Step 2: Generate the Case Study

Follow the exact section structure in `references/template.md`. That reference defines every section, its purpose, formatting rules, and examples pulled from the two canonical case studies.

Key principles while writing:

- **Show, don't tell.** Instead of "it's fast," say "142 raw articles processed in under 60 seconds." Instead of "it saves money," say "$0.03 per daily run, under $1/month."
- **Every claim gets evidence.** If you say "deduplication removes 30-40%," back it with the algorithm description. If you say "4 problems," enumerate all 4 with specifics.
- **Numbers are load-bearing.** Pull real numbers from the brief. If a number isn't available, describe the mechanism instead — never invent a number. Flag gaps with "Ask for the actual number if you have it."
- **The prospect takeaway sells the architecture, not the instance.** The last section reframes the specific project as a pattern that works across industries. This is the soft pitch — don't skip it.
- **No fluff, no filler.** Every sentence earns its place. Read each paragraph and ask: would a prospect learn something useful from this?

### Step 3: Save

Write the output to `docs/<slug>-case-study.md`. Derive the slug from the project name: lowercase, hyphens for spaces, strip special characters. Examples: `daily-news-brief-case-study.md`, `lead-gen-case-study.md`.

If a file already exists at that path, warn the user and ask whether to overwrite or use a different slug.

After saving, show the user a brief summary: path saved, section count, and a note on any gaps flagged (numbers not provided, sections that could be stronger with more input).

## Input Formats

The skill handles whatever the user gives you:

**Minimal bullet points:**
> Case study for the Reel Engine. It turns infographic posts into 40-50s motion-graphics reels. Uses Remotion, ElevenLabs, Whisper. Built by NexusPoint.

→ Ask 2-4 clarifying questions, then generate.

**Conversational brief:**
> Write up the content engine. It pulls ideas from the daily brief and YouTube, scores them with opportunity scores, researches with OpenAI, writes content for LinkedIn/Instagram/blog, and logs everything to Google Sheets. Built on Next.js with OpenAI and Google Workspace integration. Generates about 15-20 content pieces per run at roughly $0.05 per piece.

→ Go straight to generation.

**Detailed spec:**
> [Multiple paragraphs with architecture, numbers, workflow, examples]

→ Generate without asking anything. The detail is already there.

## Output Quality Bar

Before saving, verify:
- [ ] All 10 sections present (title + metadata through footer)
- [ ] Problem section has exactly 4 specific, numbered problems
- [ ] Feature table uses Live/In Progress/Planned statuses
- [ ] Cost breakdown has specific numbers or honest "ask for this" notes
- [ ] Architecture section lists tech stack + commands
- [ ] Walkthrough uses concrete numbers, not placeholders
- [ ] Prospect takeaway reframes the architecture for client reuse
- [ ] No invented numbers — gaps are flagged, not filled with guesses
- [ ] Footer has "Built and maintained by [Who]. Last updated: [Month Year]."

## Reference

See `references/template.md` for the complete section-by-section format specification with examples from both canonical case studies.