---
name: content-engine
description: >
  Powerful content creation engine for Aleem's personal brand (Instagram, LinkedIn, blog).
  Pulls ideas from 3 sources (daily-news-brief SQLite, youtube-daily-brief JSON, saved topics
  sheet), scores with opportunity scores, researches with OpenAI web search, writes finished
  content, repurposes across platforms, and logs to Google Sheets. Use when Aleem wants
  content ideas, wants to create/repurpose a post, needs a content calendar, or wants a
  full content run. ALWAYS use this skill when Aleem mentions creating content, posting on
  social media, writing a blog, asking what to post, or wanting to plan content for the week.
  Trigger phrases: "content engine", "create content", "content ideas", "what should I post",
  "write a post", "content calendar", "post for Instagram", "post for LinkedIn",
  "write a blog", "ideate content", "content plan", "full content run", "make me a post",
  "repurpose this", "what's worth posting today", "help me post".
argument-hint: [ideate | create <platform> <topic> | repurpose | plan | full]
---

# Content Creation Engine

Pulls today's AI/tech intelligence from 3 sources, scores ideas with opportunity scores,
runs web research before writing, and produces finished content for Instagram, LinkedIn,
and the blog. The repurposing flywheel (Blog -> LinkedIn + Instagram + story + email) is the core
of the `full` mode — one topic becomes several platform-native pieces.

## Context to Load First

Always load: `context/me.md`, `references/platform-formats.md`, `references/content-pillars.md`

For `create` and `full` modes, also load the 2026 research for the target platform(s) — load
only what the request needs (platform-formats.md is the distilled checklist; the
marketing-advisor playbooks are the deeper, cited 2026 source):
- LinkedIn -> `.claude/skills/marketing-advisor/references/linkedin-playbook.md`
- Instagram / Reels -> `.claude/skills/marketing-advisor/references/instagram-reels-playbook.md`
- Blog / cross-platform -> `.claude/skills/marketing-advisor/references/content-strategy-playbook.md`
- Always -> `.claude/skills/marketing-advisor/references/nexuspoint-positioning.md` (ICP/positioning)
- Consult as needed -> `marketing-advisor/references/channel-benchmarks.md` (targets) + `what-not-to-do.md` (kill list)

---

## Mode Detection

| Mode | Triggers | Action |
|------|----------|--------|
| **ideate** | "content ideas", "what should I post", "show me ideas", "ideate" | 3 sources -> score -> ranked advisory output |
| **create** | "create", "write a post for [platform]", "make me a [format]", "write a blog" | Research -> brief -> write finished piece |
| **repurpose** | "repurpose this", "turn this into", "make a carousel from" | Adapt existing content for other platforms |
| **plan** | "content calendar", "plan my week", "5-day plan" | 5-7 day calendar + rhythm check |
| **full** | "full content run", "create everything", "all platforms" | Blog first -> repurpose into LinkedIn + Instagram |

If ambiguous, default to `ideate`.

---

## Workflow

### Step 1: Pull Brief Data (all modes)

```bash
python .claude/skills/content-engine/scripts/pull_ideas.py
```

Read stdout directly. If the script fails or returns errors, note what's unavailable and
continue with what exists. If all sources fail, ask user to run `/daily-brief` first.

### Step 2: Mode Dispatch

---

#### ideate mode

Score each idea on these dimensions (Claude computes):

| Dimension | Points |
|-----------|--------|
| Timeliness: `breaking` | 3 |
| Timeliness: `trending` or `estimated_interest == "high"` | 2 |
| Timeliness: `evergreen` or `medium` | 1 |
| Competition: `low` | 3 |
| Competition: `medium` or unknown | 2 |
| Competition: `high` | 1 |
| Momentum: `rising` | 2 |
| Momentum: `steady` or no signal | 1 |
| Momentum: `cooling` | 0 |
| Pillar fit: strong match | 2 |
| Pillar fit: moderate | 1 |
| Pillar fit: off-brand | 0 |
| Conversion potential: comparison / customer-story / teardown / "how I" | 2 |
| Conversion potential: opinion / news / educational | 1 |
| Conversion potential: pure viral-bait / vanity (reach only, no business outcome) | 0 |
| Saved topics bonus | +1 |

Max = 12. Labels: 11-12 = "Strong opportunity", 8-10 = "Good pick", 5-7 = "Decent", <=4 = "Skip"

Conversion potential reflects the 2026 revenue-vs-vanity research: comparison/"X vs Y",
customer-voiced stories, teardowns, and "how I" pieces drive business outcomes; generic
thought-leadership and pure viral-bait drive vanity reach. Flag a high-reach/low-conversion
idea as "VIRAL-BAIT — reach only, pair with a direct offer or rank lower."

Display ranked list of top 5-8 ideas in this format:

```
CONTENT IDEAS — [date]
Sources: daily-brief ([N]) + youtube-brief ([N]) + saved topics ([N])

TOP PICKS

#1 [Score: X/10 — Strong opportunity]
Topic: [title]
Platform: [Instagram | LinkedIn | Blog]
Format: [carousel | text post | article | reel script]
Goal: [Brand awareness | Lead gen | Engagement | Thought leadership]
Buyer stage: [Awareness | Consideration | Decision]
Angle: [Educational | Data-backed | Founder story | Controversial take]
Why this platform: [1-2 sentences — audience fit + format advantage]
Hook: "[hook]"
Why now: [timeliness or momentum signal]
Pillar: [Pillar 1/2/3/4 name]
Source: [news-brief | youtube-brief | saved-topics]

[repeat for #2, #3...]

---
All ideas:
[compact table: # | Topic | Score | Platform | Format | Goal | Source]
```

Flag any idea where `momentum_signal == "cooling"` with "COOLING — trending down."

End with: "Say `create [platform] [number]` to write any of these, `plan` for a 5-day
calendar, or `full` to run the repurposing flywheel."

---

#### create mode

1. Parse platform + topic from user input. Platform is required — ask if missing.
2. For Blog or LinkedIn posts, run research to get fresh, topic-scoped sources. This does a
   live web-research pass into a clean NotebookLM notebook, then synthesizes from selected sources:
   ```bash
   # Mode A — fresh web research on the topic, returns the imported sources + notebook_id
   python .claude/skills/content-engine/scripts/research_notebooklm.py --topic "[topic]" --depth light|medium|deep
   # Mode B — synthesize prose from the chosen sources (ids from Mode A output)
   python .claude/skills/content-engine/scripts/research_notebooklm.py --topic "[topic]" --notebook "[notebook_id]" --sources "id1,id2,..."
   ```
   Depth maps to research effort: light (~8-12 sources, fast), medium (~20-25, deep), deep (~100-120, deep).
   Sources are topic-scoped by construction (fresh web search), so there's no static corpus to filter.
3. Internally form a content brief (don't show unless user asks):
   - Goal: infer from pillar + platform context, or ask
   - Angle: the differentiated perspective, drawn from the synthesized research prose
   - Hook: refine using research insights
   - Key points: source key_points augmented with specifics from the Mode B synthesis
   - CTA: matched to goal
4. Write the complete finished piece following `platform-formats.md` specs and voice rules.
   Do not produce an outline — write the actual content.
5. After delivering: "Want me to save this to Google Docs and log it? I can also repurpose
   it for [other platforms] if you'd like."
6. If yes to save: run `save_content.py` -> get doc URL -> run `log_post.py`

---

#### repurpose mode

Takes content the user pastes. Ask "Which platforms do you want this repurposed for?" if
not stated.

Repurposing rules (2026 — follow `platform-formats.md`):
- Blog -> LinkedIn **doc carousel** (primary, 6-12 slides, standalone cover) OR text post (150-300 words, hook in first 125-150 chars, no link in body)
- Blog -> Instagram **Reel** (15-30s cold-open script, kinetic captions, [B-ROLL]) and/or carousel (6-8 slides)
- Blog / long LinkedIn post -> Instagram standalone caption (125-250 words, value-native close)
- Any insight -> carousel cover + caption, or a story

Rewrite fully for each platform's tone and 2026 rules. Maintain the core insight but don't
just paste. Structural translation, not copy-paste.

---

#### plan mode

Generate a 5-7 day content calendar from scored ideas. Run ideation internally — don't
display the scoring process, just the calendar.

Rules:
- No platform repeated more than 3 out of 7 days
- At least 1 Blog per week
- Prioritize saved-topics ideas (pre-qualified interest signals)
- Where a blog appears, note the repurposing opportunity inline:
  "Day 3 Instagram = repurposed from Day 1 Blog"

Calendar format per day:
```
Day 1 — [Day, Date]
Platform: Blog
Format: Long-form article
Topic: [topic]
Goal: [goal]
Buyer stage: [Awareness | Consideration | Decision]
Angle: [angle type]
Hook: [hook]
Target keyword: [keyword — blog only]
CTA: [CTA]
Research needed: Yes
```

After calendar, add a rhythm check line:
"Rhythm check: 3 LinkedIn, 2 Instagram, 2 Blog — good balance."
Or flag if any platform has 0 entries this week.

Offer: "Want me to save this calendar to Google Docs?"

---

#### full mode — Repurposing Flywheel

The most powerful mode. Pick the highest-scoring idea, write it as a blog, then derive the
platform pieces from the blog. All pieces share the core insight but are native to their
platform and follow the 2026 rules in `platform-formats.md`.

1. Internal ideation: pick top-scoring idea (don't display the scoring process)
2. Run research: `research_notebooklm.py --topic "[chosen topic]" --depth medium` (Mode A), then
   `research_notebooklm.py --topic "[chosen topic]" --notebook "[id]" --sources "id1,id2"` (Mode B) to synthesize
3. Write Blog (800-1500 words, SEO + AI-citable, embed research data naturally)
4. Derive the platform pieces from the blog:
   - LinkedIn **doc carousel** (6-12 slides, standalone cover) — the #1 LinkedIn format
   - LinkedIn **text post** (150-300 words, hook in first 125-150 chars, no body link)
   - Instagram **Reel script** (15-30s cold-open, kinetic captions, [B-ROLL])
   - Instagram **carousel** (6-8 slides)
   - **Story** (2-3 slides teasing the piece)
   - **Email** newsletter edition (120-200 words) — optional, if a list is in play
5. comment-to-DM CTAs feed inbound to the **sales-playbook** skill; render Reels with the **reel-creator** skill.

Output structure:
```
## Blog — [SEO title]
[Full article]

---

## LinkedIn — Document Carousel (repurposed from blog)
Slide 1 (cover): [standalone hook]
Slide 2-N: [one insight each]
Final slide: [value-native CTA + handle]
Post text: [50-150 words]

---

## LinkedIn — Text Post (repurposed from blog)
[150-300 word post, hook first, no body link]

---

## Instagram — Reel Script (repurposed from blog)
Hook (0-3s): [cold open, spoken + on-screen]
[beats 3-25s, <10 words each, with [B-ROLL]]
Close: [value-native CTA]
Captions: [kinetic caption note]

---

## Instagram — Carousel (repurposed from blog)
Slide 1: [hook — max 8 words]
...
Slide N: [value-native CTA]
Caption: [100-250 chars]
Hashtags: [3-5 niche, from research]
```

After all pieces: "Want me to save these to Google Docs and log them?"
Save = one doc per piece. Log = one row per piece in Content Log.

---

## Voice Rules (apply to ALL written content)

@.claude/skills/content-engine/references/voice-principles.md

---

## Google Docs Save (user-gated only)

Build the JSON payload and pipe to save_content.py. Use one doc per platform piece.

```json
{
  "title": "Content — [Platform] [Format]: [topic] — [YYYY-MM-DD]",
  "sections": [
    {"heading": "Platform", "level": 1, "body": "[platform] — [format]"},
    {"heading": "Goal", "level": 2, "body": "[goal]"},
    {"heading": "Hook", "level": 2, "body": "[hook]"},
    {"heading": "Content", "level": 2, "body": "[full content]"}
  ]
}
```

```bash
echo '<JSON>' | python .claude/skills/content-engine/scripts/save_content.py
```

Then log the entry:
```bash
echo '{"platform":"...","format":"...","goal":"...","title":"...","hook":"...","doc_url":"..."}' | python .claude/skills/content-engine/scripts/log_post.py
```

If the save script fails, output the content inline with a note to copy manually.

---

## Edge Cases

| Scenario | Action |
|----------|--------|
| `pull_ideas.py` fails entirely | Ask user to run `/daily-brief` first, then retry |
| Only 1-2 sources available | Proceed with what exists, note what's missing |
| `research_notebooklm.py` fails or NotebookLM auth expired (`notebooklm login`) | Proceed without research, note it, still write content |
| User creates content off-brief | Accept it — briefs are the default source, not required |
| Save script fails | Output content inline: "Save failed — copy this manually." |
| Briefs are >1 day old | Note the date, ask if they want to regenerate first |
