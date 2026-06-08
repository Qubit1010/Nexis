# Platform Format Specifications (2026)

Use these specs as a checklist when writing content. Every piece must hit its platform's
structural requirements before it goes out.

**Source basis:** Aligned to the 2026 research in `marketing-advisor/references/` -
`linkedin-playbook.md`, `instagram-reels-playbook.md`, `content-strategy-playbook.md`,
`channel-benchmarks.md`, `what-not-to-do.md`. These are the canonical word counts and
rules; the dashboard's `generate/route.ts` PLATFORM_SPECS mirrors this file - keep them in
sync. Numbers are targets to beat, measured against real performance.

---

## Instagram

### Reel Script (highest-reach format - 55% of views from non-followers)
- **Duration:** 15-30 seconds is the sweet spot. Completion beats length: a 15s reel at 80%
  completion outperforms a 60s reel at 20%. Go longer only if retention holds.
- **Cold open:** Drop straight into the climax. NO "hey guys / today I want to talk about."
  Motion must be in the very first frame (a static-looking frame gets swiped past).
- **Structure:**
  - Hook (0-3s): spoken AND on-screen. Win this or lose 50% of viewers. Use "you", a number,
    a contrarian claim, or a direct question.
  - Payoff (3-25s): 3-5 punchy beats, one idea each. Short spoken lines (<10 words).
  - Close (final 2-5s): one value-native CTA (see CTA rules), often comment-to-DM.
- **Kinetic captions are mandatory** (60-85% watch on mute; captions add ~25% retention).
- **Write as spoken dialogue**, include [B-ROLL] notes. Optimize for **saves + sends**, not likes.
- **Cadence:** 3-5 Reels/week.

### Carousel (MOFU - drives saves/trust)
- **Slides:** 6-8 total.
- **Slide 1 (Cover):** Hook only, max 8 words. Must stand alone as a thumbnail and stop the scroll.
- **Slides 2-7:** One idea per slide. Single label + 1-sentence elaboration. Skimmable.
- **Final slide:** value-native CTA (e.g. "Save this if you're building one" or a comment-to-DM trigger).
- **Caption:** 100-250 characters. Expand the hook, end with a question or save prompt.
- **Hashtags:** 3-5 niche tags (never 30 - that is a spam penalty).
- **Tone:** Personal. "I noticed / I built / I tried", not generic advice.

### Standalone Caption (single image/text post)
- **Length:** 125-250 words.
- Line 1 = standalone STOP-SCROLL hook. Lines 2-6 build the argument (short, specific, personal).
  Then zoom out to the broader principle. Final line = value-native CTA or open question.
- **Line breaks** every 1-2 sentences. Max 2 emojis, only where they add emphasis.
- **Hashtags:** 3-5 niche.

### Story (BOFU - direct, low-reach)
- Max 2 sentences. Quick behind-the-build or reaction. Optional question/poll sticker.

### Instagram funnel
Reels (awareness) -> Carousels (saves/trust) -> Stories (direct). Reels rarely convert
directly; their job is reach. Capture leads with **comment-to-DM** ("comment X and I'll send it"),
which hands the DM conversation to the sales-playbook skill.

### Posting
- 3-5 posts/week. Best windows (local): 7-9am, 11am-1pm, 7-10pm. Post 15-30 min before a peak.

---

## LinkedIn

### Document Carousel (PDF) - THE #1 organic format (6.6-7% engagement rate)
Default to this for educational/framework content - it out-performs text and video.
- **Slides:** 6-12. One insight per slide, consistent layout.
- **Cover:** strong hook, high contrast, works as a standalone thumbnail.
- **Final slide:** value-native CTA + handle.
- **Accompanying post text:** 50-150 words of context before they open the doc.

### Text Post
- **Length:** 150-300 words (sweet spot). Narrative/story posts may run to ~500 words
  (1,300-3,000 chars, which perform ~38% better) only if the formatting is flawless.
- **Hook:** the first 125-150 characters (the part shown before "see more") decide everything.
  Bold claim, number, or a specific moment. Never waste line 1 on context. Contrarian hooks
  lift reach ~49%.
- **Body:** Hook -> why it matters -> 2-4 short insight beats -> resolution/principle.
- **No external link in the body** (cuts reach 50-70%). If you must link, tell the reader it
  is in the comments and add it 30-60 min after posting.
- **CTA:** one specific question that invites a real reply. Never "Follow me for more."
- **No emojis. No em dashes.** One idea per line, blank lines between. Write to be *read*
  (dwell time is the #1 signal: a 61s+ read earns ~13x the engagement of a 3s skim).
- **Hashtags:** 1-2 relevant, or none (3-5 cuts reach ~29%).

### Article (long-form)
- **Length:** 600-1200 words. H2 every 200-300 words. Open with a bold claim or a moment,
  zero throat-clearing. Claim -> evidence -> framework/lesson -> CTA.

### Newsletter
- **Length:** 400-600 words. Conversational. Why this matters now -> 2-3 insights with
  examples -> one actionable takeaway. (Newsletters bypass the feed, 40-60% open rates.)

### Distribution mechanics (apply to every LinkedIn post)
- **Golden Hour:** the first 60 min on 2-5% of your network decides reach; it needs ~5%+
  engagement to expand. Reply to every comment in that window. A 10+ word comment from you
  carries 5-7x the weight of a like.
- **Engage before you post:** comment on 5-10 niche posts in the 15 min before publishing.
- **Cadence:** 3-5 posts/week, Tue-Thu, 7-9am / 12-1pm / 2-4pm local. Personal profile only
  (8x the reach of a company page). Don't edit in the first 10-15 min (resets evaluation).

---

## Blog (Website)

### Long-form Article
- **Length:** 800-1500 words.
- **SEO + AI-citability:** use `primary_keyword` in a natural title under 60 chars. Structure
  for machines too - clear H2s, a crisp definition/summary near the top, and self-contained
  factual sentences. AI-search referrals (ChatGPT/Perplexity) convert ~3.49% (a 22% lift over
  organic), so being *quotable by an AI engine* is now a ranking goal.
- **H2 headers:** every 200-350 words (roughly 4-6 sections for an 800-1500 word piece); weave `secondary_keywords` in naturally.
- **Opening:** state the problem and the promise in ~3 sentences. Never "In today's rapidly
  evolving AI landscape" or any variant. Start with the problem or the story.
- **Structure:** Problem -> context -> solution/framework -> examples with real data -> takeaways.
- **Data:** embed 2-3 statistics from research `data_points`, cited inline.
- **People Also Ask:** answer 1-2 `people_also_ask` questions as H2s (featured-snippet + AI-cite bait).
- **Close:** 2-sentence zoom-out to the universal pattern + one clear next step.
- **Internal links:** to related posts/tools when genuinely relevant.

### Tutorial ("How I" format)
- **Length:** 600-1000 words. H1 "How I [did X]". Why it matters + quick result -> numbered,
  specific steps (with code/examples if relevant) -> result + what to try next. Show one failure mode.

### Opinion / POV
- **Length:** 400-700 words. H1 = a contrarian statement. Name the belief you reject (fresh
  phrasing each time, never "conventional wisdom") -> why it's wrong + your experience ->
  what you actually believe + invite disagreement.

### High-converting blog angles (prioritize)
- **Comparison "X vs Y"** pages convert ~3.2x feature pages.
- **Customer-voiced stories** (in the client's own words) beat polished case studies ~3:1.
Use these angles when the topic allows - they drive business outcomes, not just reads.

---

## Brand constraints (all platforms)
- Personal-brand content NEVER names the agency or references university/degree/student status
  or classrooms (hard rule). Reframe as "in my own work / from what I've shipped / building real systems."
- Hit the word-count floor: long-form (blog, LinkedIn article) must reach the minimum, not stop short.
  If under, deepen an example or add a sub-section, never filler.
- Every piece must pass the Unswappable Formula and voice rules in `voice-principles.md`.
