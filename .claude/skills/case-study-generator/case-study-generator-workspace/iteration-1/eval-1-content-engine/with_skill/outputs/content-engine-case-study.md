# Content Engine: How NexusPoint Built an AI Content Creation OS That Scores, Researches, and Writes for 3 Platforms

**Category:** Internal AI System / Content Operations
**Built by:** NexusPoint
**Powered by:** OpenAI gpt-4o, Python, Google Workspace (Sheets + Docs), NotebookLM, Claude Sonnet

---

## The Problem

Anyone building a personal brand or business presence goes through the same cycle: find something to talk about, figure out if it is worth the effort, do the background reading so you don't sound shallow, actually write the thing, then post it and hope. Most people never make it past step one consistently.

The default approach is to scroll Twitter or LinkedIn, pick whatever is trending, paste a prompt into ChatGPT, and publish whatever comes out. The result sounds like everyone else. Nothing is researched. Nothing is scored against what the audience actually wants. Nothing is saved, logged, or repurposed. One piece, one platform, one-and-done.

Four specific problems:

1. **Idea sourcing is fragmented.** Ideas live in a news database, a YouTube analysis file, a saved-topics sheet, and a saved-articles sheet -- four separate sources with no central view. Without a system, you pick the loudest signal, not the best opportunity.
2. **No scoring before writing.** An idea that looks good on the surface might be a cooling trend with high competition and weak pillar fit. But you don't know that until you've already written it and posted it to silence. The time is already burned.
3. **Generic AI output destroys voice.** Paste a topic into ChatGPT without guardrails and you get a LinkedIn post that could be anyone. It uses filler phrases, hedges every claim, and sounds nothing like the person behind it. Fixing it takes longer than writing from scratch.
4. **Nothing gets repurposed.** A blog post gets posted to the website and dies. There is no system that automatically derives a LinkedIn carousel, an Instagram Reel script, and a newsletter edition from the same core research. One idea generates one piece when it should generate five.

---

## What It Is

Content Engine is an end-to-end content creation operating system. It pulls ideas from four data sources, scores every idea on a 10-dimension framework, runs live web research before a single word is written, generates platform-native finished content for LinkedIn, Instagram, and blog, and repurposes one piece into several via a flywheel. Everything is logged to Google Sheets and saved to Google Docs.

It runs across two layers:

- **A Next.js dashboard** -- visual interface for ideation, research, content creation, scheduling, and logging. One click to refresh ideas, run research, generate a finished piece, save to Google Docs, and schedule.
- **A Claude skill** -- natural language interface for the larger workflows: repurposing one piece into three platforms, generating a week-long content calendar, or running the full blog-to-social flywheel in one command.

Both layers share the same voice rules, platform specifications, and content pillars. The dashboard is for granular, hands-on creation. The skill is for speed and orchestration.

Every run, the system:
- Pulls 15-40 ideas from 4 sources in a single command
- Scores every idea on a 12-point scale (timeliness + competition + momentum + pillar fit + conversion potential + saved-topic bonus)
- Researches selected topics via NotebookLM at light (8-12 sources), medium (20-25 sources), or deep (100-120 sources)
- Generates finished content in 7 platform formats with voice rules enforced, not hoped for
- Repurposes one blog into a LinkedIn doc carousel, LinkedIn text post, Instagram Reel script, Instagram carousel, Story, and email newsletter
- Saves every piece to Google Docs and logs every publish to Google Sheets

---

## The 5 Modes

### Mode 1 -- Ideate: Score Before You Write

The hardest part of content is knowing what to write. Ideate mode solves this by pulling from four sources simultaneously and scoring every idea before it reaches the user.

**The 4 sources:**

- **Daily News Brief (SQLite)** -- AI/tech articles from the internal news pipeline (NewsAPI, Hacker News, RSS feeds). The most timely, breaking opportunities with pre-written hooks and key points.
- **YouTube Brief (JSON)** -- Content opportunities and trending topics extracted from tracked YouTube channels. What the algorithm is surfacing before it is saturated, with estimated interest and competition levels.
- **Saved Topics (Google Sheet)** -- Manually bookmarked ideas in a "Content Opportunities" sheet. The curated backlog with pre-logged timeliness, angle, and format.
- **Saved Articles (Google Sheet)** -- Specific articles saved for future reference. Source URLs, TLDRs, and publication names ready for commentary.

The pull is one command: `python pull_ideas.py`. It reads all four sources, normalizes the data, tags every idea with platform affinity (Instagram-first vs LinkedIn-first vs Blog-first based on format, timeliness, and interest), and returns a single JSON payload.

**The 10-dimension scoring framework:**

| Dimension | Points |
|-----------|--------|
| Timeliness: breaking | 3 |
| Timeliness: trending or high interest | 2 |
| Timeliness: evergreen or medium | 1 |
| Competition: low | 3 |
| Competition: medium or unknown | 2 |
| Competition: high | 1 |
| Momentum: rising | 2 |
| Momentum: steady or no signal | 1 |
| Momentum: cooling | 0 |
| Pillar fit: strong match | 2 |
| Pillar fit: moderate | 1 |
| Pillar fit: off-brand | 0 |
| Conversion potential: comparison / customer-story / teardown / "how I" | 2 |
| Conversion potential: opinion / news / educational | 1 |
| Conversion potential: pure viral-bait (reach only, no business outcome) | 0 |
| Saved topics bonus | +1 |

Max score: 12. Labels: 11-12 = Strong opportunity, 8-10 = Good pick, 5-7 = Decent, 4 and under = Skip.

Conversion potential reflects the 2026 research: comparison pieces convert roughly 3.2x feature content, and customer-voiced stories beat polished case studies roughly 3:1. Pure viral-bait drives reach but not business -- the system flags these explicitly as "VIRAL-BAIT -- reach only, pair with a direct offer or rank lower."

Each scored idea surfaces with: topic, platform recommendation, format, goal, buyer stage, angle type, hook, why-now signal, content pillar, and source. Cooling ideas are flagged and dropped. Saved topics get a +1 bonus. The system tells you what is worth writing and why -- not just a list of headlines.

---

### Mode 2 -- Create: Research First, Then Write

Create mode enforces a hard rule: research before writing. No generic AI output. No hallucinated statistics. No stale takes.

**Step 1 -- Research via NotebookLM**

The topic is sent through a fresh web-research pass into a dedicated NotebookLM notebook. Three depth levels:

| Depth | Sources | Use Case |
|-------|---------|----------|
| Light | 8-12 | Quick LinkedIn posts, opinion pieces |
| Medium | 20-25 | Blog articles, carousels, data-backed content |
| Deep | 100-120 | Pillar content, long-form comparison pieces, whitepapers |

Each research pass is topic-scoped -- it searches fresh for what is published now, not what was in a static corpus last quarter. The output returns imported source IDs plus a notebook ID for later synthesis.

A second pass synthesizes the chosen sources into prose, pulling specifics: data points with sources, competing angles already in the market, and content gaps (what nobody has written yet). This is the differentiation layer -- the system surfaces what to say that nobody else is saying.

**Step 2 -- Generate with voice enforcement**

Platform, format, and content mode are selected. The system constructs a comprehensive prompt that includes:
- All research data (keywords, data points, gaps, competing angles)
- Platform-specific format specs drawn from 2026 research (LinkedIn Text Post: 150-300 words, hook in first 125-150 characters, single-line spacing; Instagram Carousel: 6-8 slides, 8-word max slide 1; Blog: 800-1500 words, H2 every 200-350 words, AI-citable structure)
- Content mode instructions (Opinion: strong take, contrarian position; News: timely, specific, actionable; Tutorial: numbered steps, one failure mode; Story: real event, specific numbers, resolution)
- The full voice rule set: the Unswappable Formula (Personal Experience + Strong Opinion + Cross-domain Insight + Clear Identity), 7 voice pillars with at least 2 required in every piece, and a explicit anti-pattern blocklist ("In today's rapidly evolving", "game-changer", "leverage", neutral summaries with no personal stake)

Output: a finished, publish-ready piece. Not an outline. Not a draft to clean up. Something that goes directly to the platform.

---

### Mode 3 -- Repurpose: One Idea, Multiple Platforms

Feed in any existing piece and a target platform. The system rewrites for the new format using structural translation, not copy-paste summarization.

The repurposing rules are platform-aware and 2026-research-backed:

- Blog to LinkedIn doc carousel: Extract 6-12 standalone insights, one per slide, with a strong standalone cover. Accompanying post text of 50-150 words.
- Blog to LinkedIn text post: Extract the core argument into 150-300 words, hook in the first 125-150 characters, no external link in the body.
- Blog to Instagram Reel: 15-30 second cold-open script with kinetic caption beats, spoken dialogue under 10 words per beat, [B-ROLL] notes, comment-to-DM CTA.
- Blog to Instagram carousel: 6-8 slides, visual-first, hook in max 8 words on slide 1, one idea per slide.
- Blog to Story: 2-3 slides, quick behind-the-build or reaction, optional poll sticker.
- Blog to Email: 120-200 word newsletter edition.

Each repurposed piece maintains the core insight but is fully rewritten for the new platform's tone and structural rules.

---

### Mode 4 -- Plan: The Week Ahead

Generate a 5-7 day content calendar from scored ideas. The system runs ideation internally and surfaces the calendar.

Rules enforced:
- No platform repeated more than 3 out of 7 days
- At least 1 blog per week
- Saved-topics ideas prioritized (pre-qualified interest signals)
- Repurposing opportunities flagged inline ("Day 3 Instagram = repurposed from Day 1 Blog")

Each calendar day tracks: platform, format, topic, goal, buyer stage, angle, hook, and target keyword (blog only). A rhythm check line confirms platform balance: "3 LinkedIn, 2 Instagram, 2 Blog -- good balance" or flags gaps.

---

### Mode 5 -- Full: The Repurposing Flywheel

The most powerful mode. One command picks the highest-scoring idea, researches it, writes it as a blog, then derives every platform piece from that blog.

1. Internal ideation picks the top-scoring idea (scoring runs silently)
2. Research runs at medium depth (20-25 sources) via NotebookLM
3. Blog written at 800-1500 words with SEO structure, AI-citable data points, and H2 sections
4. Platform pieces derived from the blog:
   - LinkedIn doc carousel (6-12 slides, standalone cover)
   - LinkedIn text post (150-300 words, hook-first, no body link)
   - Instagram Reel script (15-30s cold-open, kinetic captions, [B-ROLL])
   - Instagram carousel (6-8 slides)
   - Story (2-3 slides teasing the piece)
   - Email newsletter edition (120-200 words)

One idea. One research pass. Seven platform-native pieces. Every piece can be saved to Google Docs and logged to Google Sheets in a single save pass.

---

## What's Built and Working

| Feature | Status |
|---------|--------|
| Multi-source idea pulling (News Brief + YouTube Brief + Saved Topics + Saved Articles) | Live |
| 10-dimension opportunity scoring (0-12 scale, 5 tiers) | Live |
| Platform affinity tagging (format + timeliness + interest-driven) | Live |
| NotebookLM-powered topic research (3 depth levels: 8-120 sources) | Live |
| Structured research synthesis (data points + competing angles + content gaps) | Live |
| Platform-native content generation (7 formats across Blog, LinkedIn, Instagram) | Live |
| Voice enforcement with Unswappable Formula + 7 pillars + anti-pattern blocklist | Live |
| Repurposing flywheel (Blog to LinkedIn carousel + text post + Instagram Reel + carousel + Story + Email) | Live |
| 5-7 day content calendar generation with rhythm enforcement | Live |
| Google Sheets content log (date, platform, format, goal, hook, doc URL per row) | Live |
| Google Docs auto-save with formatted sections | Live |
| Source row marking (saved topics/ideas marked "Used" after content created) | Live |
| Cooling idea flagging + viral-bait warnings | Live |
| Weekly schedule view with inline editing | Live |
| Per-platform research-backed format specs (aligned to 2026 benchmarks) | Live |
| Saved topics + saved articles bonus scoring | Live |

---

## Cost Breakdown

Content Engine has two cost layers: the research pass (NotebookLM + OpenAI web search) and the content generation pass (OpenAI gpt-4o for writing). Logging and saving to Google Sheets and Docs are free (Google Workspace integration).

| Component | Service | Cost Model | Estimated Cost |
|-----------|---------|------------|----------------|
| Idea pulling | Python (local SQLite + Google Sheets API) | Free | $0.00 |
| Opportunity scoring | Claude Sonnet (in-skill, no API) | Free | $0.00 |
| Topic research -- light | NotebookLM + OpenAI web search (8-12 sources) | API per query | ~$0.01-0.02 |
| Topic research -- medium | NotebookLM + OpenAI web search (20-25 sources) | API per query | ~$0.03-0.05 |
| Topic research -- deep | NotebookLM + OpenAI web search (100-120 sources) | API per query | ~$0.08-0.12 |
| Content generation (per piece) | OpenAI gpt-4o | Per token | ~$0.01-0.03 |
| Repurposing pass (6 derived pieces) | OpenAI gpt-4o + Claude Sonnet | Per token | ~$0.05-0.10 |
| Save to Google Docs + log to Sheets | Google Workspace CLI (gws) | Free | $0.00 |

**Full mode economics:** one blog + research (medium) + 6 derived pieces runs roughly $0.10-0.18 total. Seven platform-native pieces of content for under $0.20. At 1 full run per week: under $1/month.

*(Actual costs depend on model pricing, research depth, and output length. Ask for the specific numbers if you have tracked them.)*

---

## The Architecture

**Frontend:** Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui
**Backend:** Next.js API routes (TypeScript), Python scripts via Node child_process
**Storage:** SQLite (local cache for news brief data), Google Sheets (schedule + content log), Google Docs + Drive (content archive)
**AI:** OpenAI gpt-4o (research synthesis + content generation), Claude Sonnet (idea scoring + skill orchestration)
**Research:** NotebookLM (notebook creation + source import + synthesis), OpenAI web search
**Data sources:** Daily News Brief SQLite database, YouTube Brief JSON analysis file, Google Sheets (Saved Topics + Saved Articles tabs)
**Integrations:** Google Workspace CLI (gws) for Sheets/Docs/Drive, NotebookLM Python client

**Commands:**
```
python pull_ideas.py                                         -> Pull + score ideas from all 4 sources
python research_notebooklm.py --topic "..." --depth medium   -> Research topic via NotebookLM (Mode A)
python research_notebooklm.py --topic "..." --notebook ID --sources "id1,id2"  -> Synthesize from sources (Mode B)
echo '<JSON>' | python save_content.py                       -> Save generated content to Google Doc
echo '<JSON>' | python log_post.py                           -> Log content to Google Sheets
```

**Google Sheets tabs:** Content Log (all published content with dates/platforms/URLs), SM Schedule (weekly calendar with 21 tracked fields per post), Content Opportunities (curated idea backlog), Saved Articles (articles bookmarked for future content)

---

## End-to-End Walkthrough

Here is what a full-mode run looks like from start to finish:

1. User triggers full mode: "full content run." The system runs ideation internally (pull_ideas.py) and picks the top-scoring idea from today's batch.

2. Today's pull returns 32 ideas: 12 from the news brief (date: 2026-06-25), 8 from YouTube brief, 7 from saved topics, and 5 from saved articles. 3 cooling ideas are flagged and dropped from contention.

3. The top-scoring idea hits 10/12: an opinion piece on why MCP servers are replacing the plugin ecosystem. Breaking timeliness (3 points), low competition (3 points), steady momentum (1 point), strong Pillar 1 fit -- AI and Automation (2 points), moderate conversion potential (1 point, opinion category). No saved-topic bonus. Platform affinity tag says LinkedIn-first.

4. Research fires at medium depth. NotebookLM creates a fresh notebook, pulls 22 sources via OpenAI web search, and imports them. The synthesis pass returns: primary keyword "MCP server ecosystem", 4 data points with sources, 3 competing angles (all focus on technical comparison, none on the business/ecosystem shift -- that is the gap), 8 hashtags.

5. The blog is written: 1,100 words, H2s every 250-350 words, 2 data points cited inline, the content gap (business/ecosystem angle) is the central argument. SEO title under 60 characters. AI-citable structure with self-contained factual sentences.

6. The flywheel spins. From the blog, six derived pieces are generated:
   - LinkedIn doc carousel: 8 slides, cover hook: "MCP is not a protocol upgrade. It is a business model shift." Accompanying post text: 85 words.
   - LinkedIn text post: 240 words, hook in first 130 characters, single-line spacing, open question CTA.
   - Instagram Reel script: 22-second cold-open with "You are still installing plugins. Here is what you are missing." 5 kinetic caption beats, [B-ROLL] notes at each transition, comment-to-DM close.
   - Instagram carousel: 7 slides, slide 1 hook in 6 words, one insight per slide, value-native CTA on final slide.
   - Story: 2 slides -- slide 1: "Just wrote about MCP vs plugins", slide 2: "Link in bio if you want the full take."
   - Email newsletter: 165 words, why-this-matters-now opener, 2 key insights, one actionable takeaway.

7. Save pass: 7 pieces saved to Google Docs (one doc per piece, titled "Content -- [Platform] [Format]: MCP ecosystem -- 2026-06-25"). 7 rows appended to Content Log sheet. Source row in Content Opportunities marked "Used."

Total time from command to 7 saved and logged pieces: roughly 3-5 minutes.

---

## The Prospect Takeaway

Content Engine is NexusPoint's internal content creation system. Every LinkedIn post, Instagram carousel, and blog article published under NexusPoint's brand runs through this system or a version of it.

The architecture is not specific to NexusPoint's content pillars or voice. The pillars, voice rules, platform specs, scoring weights, and data sources are all configuration. The underlying system is the same:

- Aggregate idea sources from wherever the business generates signal (CRM, internal docs, news, analytics, competitor feeds)
- Score every opportunity against what actually matters for that brand's audience and revenue goals
- Research before writing, using live data not assumptions or stale knowledge
- Generate with voice rules enforced structurally, not left to chance
- Repurpose one researched piece into several platform-native formats automatically
- Log everything to the tools the team already uses (Sheets, Docs, Notion, whatever)

The same architecture works for:

- A B2B SaaS company that needs to turn product updates into blog posts, LinkedIn thought leadership, and customer-facing newsletters
- A marketing agency that creates content for 10+ clients and needs voice-enforced generation with per-client pillars
- A consultancy where partners need to publish consistently but should not spend time on research or formatting
- An e-commerce brand turning product launches and industry trends into Instagram Reels, carousels, and email campaigns
- Any founder or operator who knows their industry well but cannot spend 8 hours a week on content creation

The idea sources change. The voice rules change. The platform formats change. The scoring dimensions change. The flywheel -- aggregate, score, research, generate, repurpose, log -- is the same.

If your business creates content for marketing, sales, or thought leadership, and you are still doing the research manually, pasting into ChatGPT without voice guardrails, and repurposing by hand, this is what replacing that looks like.

---

*Built and maintained by NexusPoint. Last updated: June 2026.*
