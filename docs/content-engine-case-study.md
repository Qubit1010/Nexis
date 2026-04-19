# Content Engine: How NexusPoint Built a Full-Stack Content Creation OS

**Category:** Internal AI System / Content Operations  
**Built by:** NexusPoint  
**Powered by:** Next.js 16, OpenAI gpt-4o, Python, Google Workspace, Claude Code

---

## The Problem

Most founders and agency operators treat content creation as an afterthought — a thing that happens when there's time. The process looks like this: open Twitter, see what's trending, open ChatGPT, paste a vague prompt, get generic output that sounds like nobody, post it hoping something sticks.

There are four specific problems with that:

1. **Idea sourcing is scattered.** You're checking multiple feeds, bookmarks, and notes — no central place to see everything scored by opportunity.
2. **Generic AI output destroys voice.** ChatGPT doesn't know who you are. The output could be anyone. It's not.
3. **No workflow exists.** Idea → research → draft → schedule → log — these all happen in different tools with no connective tissue.
4. **Nothing gets repurposed.** One piece of content gets posted once and dies.

NexusPoint built Content Engine to solve all four.

---

## What Content Engine Is

Content Engine is an end-to-end content creation operating system. It runs as two layers:

- **A Next.js dashboard** — a visual interface for discovering ideas, researching topics, generating platform-native content, managing a weekly schedule, and logging everything to Google Sheets and Docs.
- **A Claude skill** — a natural language interface for orchestrating larger workflows: repurposing one piece into three, generating a week-long content calendar, or running the full blog-to-social flywheel in one command.

Both layers share the same voice rules, platform specs, and content pillars. The dashboard is for granular, hands-on creation. The skill is for speed.

---

## The 4 Core Workflows

### 1. Idea Discovery

The hardest part of content is not writing — it's knowing what to write about. Content Engine solves this by pulling from four separate sources simultaneously and scoring every idea before you see it.

**The 4 sources:**

- **Daily News Brief** — AI/tech articles pulled from the internal news pipeline (NewsAPI, Hacker News, RSS feeds), stored in SQLite. The most timely and breaking opportunities.
- **YouTube Brief** — Content opportunities extracted from tracked YouTube channels. What the algorithm is already surfacing, before it's saturated.
- **Saved Topics** — A Google Sheet where ideas get manually bookmarked. The curated backlog.
- **Saved Articles** — Specific articles saved for future reference, also in Google Sheets.

Every idea from every source gets scored on a 10-point scale:

| Dimension | Points |
|-----------|--------|
| Timeliness (breaking / trending / evergreen) | 0-3 |
| Competition level (low / medium / high) | 0-3 |
| Momentum signal (rising / steady / cooling) | 0-2 |
| Pillar fit (strong / moderate / none) | 0-2 |
| Saved topic bonus | +1 |

The dashboard renders a ranked, filterable list. Cooling ideas drop to the bottom. High-scoring ideas sit at the top. No more deciding what to write — the system surfaces it.

---

### 2. Research + Content Generation

Once an idea is selected, the workflow is: research first, then write.

**Step 1 — Research**

Click "Run Research" and the system calls OpenAI gpt-4o with a live web search. It returns:
- Primary SEO keyword (under 60 characters)
- Secondary keywords
- 3-5 data points with sources
- Competing angles (what others are already saying)
- Content gap (what's missing — the differentiation opportunity)
- Related questions people are asking
- 5-10 relevant hashtags

No hallucinated statistics. No stale information. Fresh, sourced data before a single word is written.

**Step 2 — Generate**

Select platform, format, and content mode (news, opinion, story, or tutorial). Click "Generate."

The system sends a comprehensive prompt to gpt-4o:
- The research data (keywords, data points, gaps, hashtags)
- Platform-specific specs (LinkedIn Text Post: 300-800 words, 3-line hook, single blank-line spacing; Instagram Carousel: 5-8 slides, 8-word max slide 1; Blog: 800-2000 words, SEO structure)
- Content mode instructions (Opinion mode: strong take, contrarian position, explain conventional wisdom then counter it)
- All 7 voice pillars defined explicitly
- Anti-patterns blocked outright

Output: a finished, publish-ready piece — not an outline, not a draft to clean up. Something that can go directly to the platform.

---

### 3. Schedule

The Schedule page connects directly to a Google Sheets tab ("SM Schedule"). It renders a weekly calendar view showing every planned post grouped by day.

Each scheduled post tracks 21 fields: date, platform, post type, media type, content theme, topic, script, image prompt, video prompt, hashtags, publish time, status, editor, and more.

From any idea card in the Ideate page, you can click "Schedule" and the modal pre-fills the topic, platform, format, and angle — so adding it to the calendar is a 15-second operation.

Filter by platform and status (Draft / Scheduled / Published / Cancelled). Navigate between weeks. Edit any post inline. The whole calendar is the Google Sheet — no new tool, no separate login.

---

### 4. Log + Archive

After generating content, one click opens the log modal. Fill in: platform, format, goal, hook, doc URL.

The system:
- Appends a row to the "Content Log" tab in Google Sheets
- Saves the full content to a Google Doc in the "Nexis Content" Drive folder
- If the idea came from a saved topic, marks that source row as "Used" so it doesn't resurface

The result is a searchable archive of every piece of content ever created — date, platform, format, title, goal, hook, link to the full doc. Nothing gets lost.

---

## The Repurposing Flywheel

The dashboard handles single-piece creation. The Claude skill handles scale.

**Full Mode** — triggered by "full content run": the system picks the top-scoring idea, runs research, writes a full blog post (800-2000 words), then automatically repurposes it into a LinkedIn post (extract core argument, sharpen hook) and an Instagram carousel (5-8 slides, visual-first). Three pieces from one command.

**Repurpose Mode** — feed in any existing piece and a target platform. The system rewrites for the new format, not just summarizes. Blog to LinkedIn: extract the core argument. Blog to Instagram: break into slides, visual-first, hook in 8 words.

**Plan Mode** — "plan my week" generates a 5-7 day content calendar from scored ideas. Rules enforced: no platform repeated three days in a row, at least one blog per week, saved-topics ideas prioritized, repurposing opportunities flagged.

---

## Voice Consistency

This is the hardest problem in AI-assisted content creation, and most tools ignore it entirely.

Content Engine solves it by encoding the brand voice directly into the generation prompt — not as a vague instruction like "write in my style," but as explicit, structured rules:

**The Unswappable Formula:**  
(Personal Experience) + (Strong Opinion) + (Cross-domain Insight) + (Clear Identity)

**7 Content Pillars — at least 2 must appear in every piece:**
1. Lived Experience — real events, specific anchors, actual numbers
2. Strong POV — disagree with something, take a side
3. Cross-domain Synthesis — connect AI to philosophy, history, or an unrelated field
4. Taste & Judgment — make calls, state what NOT to do, don't hedge
5. Identity & Voice — student founder in Pakistan, context as constraint not credential
6. Practical Stakes — answer "what breaks?" not just "what's possible?"
7. Content Specific — explain the topic with practical use cases

**Anti-patterns explicitly blocked:**
- "Here are N ways to..." with no personal stake
- Neutral summaries without the creator's experience
- Generic advice not anchored to real context
- Filler: "In today's rapidly evolving...", "game-changer", "leverage"

The result: LinkedIn posts, Instagram carousels, and blog articles that all sound like the same person — because the system enforces it, not just hopes for it.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| Idea discovery from 4 sources | Live |
| Opportunity scoring (0-10) | Live |
| Filter + sort ideas by source, score, date | Live |
| OpenAI-powered topic research (live web search) | Live |
| Platform-native content generation | Live |
| Voice enforcement + pillar selection | Live |
| Weekly schedule (Google Sheets sync) | Live |
| Add + edit scheduled posts | Live |
| Content log (Google Sheets) | Live |
| Auto-save to Google Docs | Live |
| Repurpose flywheel (skill layer) | Live |
| Plan mode (5-7 day calendar) | Live |

---

## The Architecture

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui  
**Backend:** Next.js API routes, Python scripts via Node child_process  
**Storage:** SQLite (local cache), Google Sheets (schedule + log), Google Docs + Drive (content archive)  
**AI:** OpenAI gpt-4o (research + generation), Claude Sonnet (skill orchestration)  
**Integrations:** Google Workspace CLI (gws), OpenAI API  

**Pages:** `/ideate` → `/create` → `/schedule` → `/log`

**Python scripts (skill layer):**
- `pull_ideas.py` — reads 4 sources, returns scored JSON
- `research_topic.py` — OpenAI web search, returns structured research data
- `save_content.py` — creates formatted Google Doc, returns doc URL
- `log_post.py` — appends to Content Log sheet, marks source as used

---

## End-to-End Walkthrough

Here's what the workflow actually looks like from start to finish:

1. Open the dashboard. Click "Refresh Ideas." The system reads the daily brief database, the YouTube brief file, and two Google Sheets tabs. Returns 15-25 scored ideas.

2. Filter to "News Brief" source. Sort by score. The top idea: "Why Claude Code agents outperform GPT wrappers for production workflows" — score 9/10 (breaking + low competition + rising momentum + strong pillar fit).

3. Click "Create." Platform: LinkedIn. Format: Text Post. Mode: Opinion.

4. Click "Run Research." 12 seconds later: primary keyword, 4 data points with sources, 3 competing angles, the content gap (nobody's written the production deployment angle), 8 hashtags.

5. Click "Generate." 8 seconds. Output: 620-word LinkedIn post opening with a specific client interaction, making a contrarian claim, backing it with data, ending with an open question.

6. Click "Log this post." Fill in goal (thought leadership), hook (first line). Click "Save to Docs." Google Doc created in Drive. Doc URL auto-fills.

7. Click "Schedule." Modal opens pre-filled. Set date, publish time, status: Scheduled. Save.

Total time from open dashboard to scheduled post: under 8 minutes. Research included.

---

## The Prospect Takeaway

Content Engine is NexusPoint's internal system. It runs on the same stack, patterns, and architecture that NexusPoint builds for clients.

The specific parts — the data sources, the voice rules, the platform specs, the scoring dimensions — all of those are configuration, not architecture. The underlying system is the same:

- Aggregate idea sources from wherever the business lives (CRM, news, internal docs, analytics)
- Score opportunities against what actually matters for that brand
- Research before writing, using live data not assumptions
- Generate with voice rules enforced, not hoped for
- Connect to the tools already in use (Sheets, Docs, Notion, whatever)

If your business creates content — for marketing, for sales, for thought leadership — and you want a system that does the research, enforces the voice, and handles the workflow without replacing the human judgment, this is what that looks like.

That's the conversation worth having.

---

*Built and maintained by NexusPoint. Last updated: April 2026.*
