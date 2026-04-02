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
and the blog. The repurposing flywheel (Blog -> LinkedIn -> Instagram) is the core of
the `full` mode — one topic becomes three platform-native pieces.

## Context to Load First

Always load: `context/me.md`

For `create` and `full` modes, also load:
- `.claude/skills/marketing-advisor/references/content-strategy-playbook.md`
- `.claude/skills/marketing-advisor/references/nexuspoint-positioning.md`
- `.claude/skills/content-engine/references/platform-formats.md`
- `.claude/skills/content-engine/references/content-pillars.md`

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
| Saved topics bonus | +1 |

Max = 10. Labels: 9-10 = "Strong opportunity", 7-8 = "Good pick", 5-6 = "Decent", <=4 = "Skip"

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
2. For Blog or LinkedIn posts, run research to get fresh data and find the content gap:
   ```bash
   python .claude/skills/content-engine/scripts/research_topic.py --topic "[topic]"
   ```
3. Internally form a content brief (don't show unless user asks):
   - Goal: infer from pillar + platform context, or ask
   - Target keyword: from research `primary_keyword` (blogs only)
   - Angle: use `content_gap` from research as the differentiated perspective
   - Hook: refine using research insights
   - Key points: source key_points augmented with 2-3 `data_points` from research
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

Repurposing rules:
- Blog -> LinkedIn text post: extract core argument, sharpen hook for LinkedIn, 300-800 words
- Blog -> Instagram carousel: break into 5-8 slides, visual-first, slide 1 = stop-scroll hook
- Long LinkedIn post -> Instagram caption: distill to 1-2 sentences + hook
- Any insight -> Instagram carousel cover + caption

Rewrite fully for each platform's tone. Maintain the core insight but don't just paste.

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

The most powerful mode. Pick the highest-scoring idea, write it as a blog, then derive
the social pieces from the blog content. All 3 pieces share the same core insight but are
native to their platform.

1. Internal ideation: pick top-scoring idea (don't display the scoring process)
2. Run research: `research_topic.py --topic "[chosen topic]"`
3. Write Blog (800-2000 words, SEO-optimized, embed research data naturally)
4. Repurpose Blog -> LinkedIn text post (extract core argument, sharpen for LinkedIn)
5. Repurpose Blog -> Instagram carousel (visual-first, 5-8 slides from blog insights)

Output structure:
```
## Blog — [SEO title]
[Full article]

---

## LinkedIn — Text Post (repurposed from blog)
[Post]

---

## Instagram — Carousel (repurposed from blog)
Slide 1: [hook — max 8 words]
Slide 2: [insight]
...
Slide N: [CTA]
Caption: [100-300 chars]
Hashtags: [from research]
```

After all 3: "Want me to save all three to Google Docs and log them?"
Save = 3 separate docs. Log = 3 rows in Content Log.

---

## Voice Rules (apply to ALL written content)

These aren't style preferences — they define Aleem's personal brand voice. Every piece of
content must feel like it was written by a 21-year-old founder/student who's building
real things, not a corporate content team.

- Write as Aleem: first person ("I", "my", "I built", "I tried")
- "How I" not "How to" — share experience, not generic advice
- No em dashes — use commas or short sentences instead
- No emojis in Blog or LinkedIn — Instagram max 2
- Specific > vague: replace "many companies" with actual numbers from research data
- Hook first — never bury the lead in any platform
- No filler openers: never start with "In today's rapidly evolving AI landscape..."
  or any variant of that pattern

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
| `research_topic.py` fails | Proceed without research, note it, still write content |
| User creates content off-brief | Accept it — briefs are the default source, not required |
| Save script fails | Output content inline: "Save failed — copy this manually." |
| Briefs are >1 day old | Note the date, ask if they want to regenerate first |
