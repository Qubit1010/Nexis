# Instagram Cold DM Sequence — Source-Backed Playbook

> **Source basis:** Cited from `references/research-synthesis.md` (Q3). Real data: CreatorFlow benchmark data, InfluenceFlow B2B targeting metrics, Jotform DM templates, Outbound Squad multi-channel sequences.

## The hard truth from the data (2026)

Instagram DMs outperform LinkedIn and email on raw response. The conversion ceiling is HIGHER but only if you avoid bot-pacing and platform deliverability traps.

| Metric | Number | Source |
|---|---|---|
| Instagram DM open rate | **~90%** (vs ~20% email) | CreatorFlow |
| Reply rate (engaged audience) | **Up to 60%** | CreatorFlow |
| Targeted creator/founder DM response | **24-32%** (vs 3-5% cold email) | CreatorFlow |
| DM-to-sale conversion | **7-20% average** | CreatorFlow / Jotform |
| Hyper-targeted 1:1 DM conversion | **18%** | InfluenceFlow |
| Generic broadcast conversion ceiling | **~5%** | CreatorFlow |
| Speed-to-reply impact | **+391% conversion if you reply within 1 min vs 30+ min** | CreatorFlow |
| Response drop past 200-word DM | **-30%** | CreatorFlow |

**Implication for Aleem:** Instagram is the highest-leverage cold channel — IF he avoids the bot signals (volume, pacing, copy-paste) AND moves fast on replies.

---

## Platform safety rules (don't get shadowbanned)

**Sourced from research synthesis Q3 section 4.** Violate these and your DMs silently route to Message Requests, where prospects never see them.

| Rule | Detail | Source |
|---|---|---|
| **Daily DM cap** | 30-50/day for established accounts (6+ mo old, 10k+ followers, 2%+ engagement). 20-30/day for newer accounts. **Never exceed 150/day.** | CreatorFlow |
| **Pacing** | Space messages 2-5 min apart minimum. Sending 50 DMs in 30 min = bot signal = soft-ban. | CreatorFlow |
| **No copy-paste** | Identical messages across multiple prospects = #1 shadowban trigger. Every message needs genuine variation. | CreatorFlow |
| **Pre-warm cold prospects** | Follow + engage with their content for **3-5 days before DMing**. This improves delivery rates by **40-50%**. | CreatorFlow |
| **No spam triggers** | "Free money," "click here," "limited time offer," 3+ URLs, ALL CAPS, !!!, 10+ emojis. | CreatorFlow |

**For Aleem:** The pre-warm rule is the biggest behavioral change from current setup. Current `instagram-outreach` skill scrapes and DMs cold. Need to add a "warm queue" — prospects to follow + engage with for 3-5 days before Touch 1.

---

## The documented 4-touch sequence

**Sourced from research synthesis Q3 section 1.** This is the cited "Partnership Discovery Flow" structured to build trust before pitching.

| Touch | Day | Move |
|---|---|---|
| **Touch 1** | Day 1 | The Observation. No ask. |
| **Touch 2** | Day 3 | The Value Add — share a resource, no ask. |
| **Touch 3** | Day 5 | The Soft Pitch + CTA — specific 20-min call ask. |
| **Touch 4** | Day 7 or 14 | The Re-engagement / Last Touch. |

**Cadence note:** This is tighter than current Aleem sequence (Day 3-4 / 8-10 / 15) — sourced data suggests faster cadence performs better on Instagram given the platform's faster conversation tempo.

---

### Touch 1 (Day 1) — The Observation

**Source-cited template:**
> "Hey [Name], [Specific observation about their content]. Thought you should know. [Your Name]"

**B2B-specific source template:**
> "Hey [Name], I noticed you recently posted about [specific pain point]. We work with creators in your space to solve exactly that. Would you be open to a quick chat about how we do it? No pressure either way."

**Aleem-adapted variants (lead with AI automation per `offer/ai-automation-positioning.md`):**

> Hey [Name], saw the post about [specific thing - their Sunday Shopify recon, their manual handoff bottleneck, etc]. We build the AI workflow that kills that exact problem - took 12 hrs/week off another [niche] founder last month. Wanted to flag it. No pressure.

> [Name] - your reel on [specific topic] was sharp, especially the bit about [specific line]. That's literally the thing I just automated for another [their role]. Wanted you to know it's solvable. No ask.

> Hey [Name], thought you'd want to see this - we just took 14 hrs/week of manual ops off a founder running [similar business]. Stack was [specific tools matching theirs]. Built it in 9 days. Wanted to flag it lives in your world. No pressure.

**Rules:**
- Under 100 words (CreatorFlow data — 30% reply drop past 200 words)
- Reference one SPECIFIC thing (post, reel, story) — not a bio observation
- 1-2 emojis max (Aleem's style: probably zero)
- No CTA in Touch 1. The point is to NOT ask.

---

### Touch 2 (Day 3) — The Value Add (no ask)

**Source-cited template:**
> "[Name], wanted to share [relevant resource/article/tool] that might be useful. [Brief reason why]. No ask, just thought of you. [Your Name]"

**Aleem-adapted variants:**

> [Name] - quick value drop, no ask. Wrote up the exact AI workflow that took 12 hrs/week off [Peer]: [link to Loom or Notion doc]. Thought you'd find it useful given the [their pain].

> [Name] - here's a 90-sec walkthrough of how we automate [the specific thing they're probably doing manually]: [Loom link]. No ask. Just figured it'd save you the research.

> [Name] - the [specific thing from Touch 1] you mentioned reminded me of this. Pattern I see in 8/10 [their niche] founders: [specific operational pattern]. We built a fix for it that 3 teams are now using. Sending the template: [link]. Use it free. No catch.

**Rules:**
- Still no ask
- Must actually deliver value (Loom, template, framework, mini-audit) — don't just say "let me know if you want it"
- Loom recommended over text — beats text for IG DMs (sourced anecdotally; specific stat not in our research)

---

### Touch 3 (Day 5) — The Soft Pitch + CTA

**Source-cited template:**
> "[Name], back on [initial observation]. We work with creators in your space and genuinely think there's something here worth exploring. Open to a quick 20-minute call next week? [Calendar link]"

**Aleem-adapted variants:**

> [Name] - back to the [specific thing from Touch 1]. We work with [their niche] founders on this exact problem. Open to a 20-min Ops Teardown? I look at your stack, tell you the first thing I'd automate, you decide if it's worth building. Tuesday 2pm or Thursday 11am? [calendar link]

> [Name] - circling back. You're the kind of founder we built [the workflow] for. 20 minutes - I'll screen-share the actual automation we shipped for [Peer]. You'll know in the first 5 min if it ports to your stack. Tuesday or Thursday work? [link]

> [Name] - one last value drop. We did a teardown of [a similar peer's stack] this week and found 9 hrs/week of automatable work. Worth doing the same for you? 20 min, I'll show you what's possible. [link]

**Rules:**
- Anchor the call ask to a DELIVERABLE (Ops Teardown, screen-share, mini-audit) — not "hop on a quick chat"
- Two specific times (Tuesday 2pm OR Thursday 11am) > calendar link alone
- Don't pitch the offer here — pitch the CALL (which has its own value)

---

### Touch 4 (Day 7 or 14) — Re-engagement

**Source-cited templates:**

Day 7 (if Touch 3 was Day 5, this is 48 hrs after):
> "No worries if you missed my last message—I know you get a lot of DMs. Just wanted to circle back on [brief partnership description]. Still think it could be great for your audience."

Day 14 (last touch):
> "Last ping, promise! Just didn't want this to get lost. We're moving forward with something in your space and think you'd be perfect. If timing isn't right now, would love to reconnect in [specific timeframe]."

**Aleem-adapted variants (lean honest + no-oriented):**

> [Name] - quick check before I assume this isn't a fit. The [specific workflow] thing we covered, is it still on your plate or did you guys figure it out? Either answer is fine - just want to know whether to keep this thread alive.

> [Name] - last message from me, no hard feelings. If automating [the specific thing] ever lands on the priority list, I'm easy to find. Wanted to say what you're building looks like it's heading somewhere real.

> [Name] - one more no-oriented question and I'll disappear: would it be a terrible idea to grab 15 min Tuesday so you at least see what's possible? If yes, no worries, I'll move on. If no, [link].

**Rules:**
- Acknowledge the gap honestly ("haven't heard back" / "last ping")
- Give them an out (the "permission to disappear" move)
- Optional: no-oriented final ask (Voss: makes "no" easy to say, which paradoxically raises yes rate)

---

## CTA / call-ask language for Instagram (sourced)

Different from LinkedIn — Instagram CTAs need to be LOW-FRICTION (don't make people leave the app for forms).

| Style | Source-cited example |
|---|---|
| **Frictionless meeting** | "Would you be open to a 15-minute call to explore if this makes sense? No obligation—just a conversation." |
| **Soft ask** | "Worth a conversation?" |
| **Resource delivery** | "If interested, let me know and I'll send all details." |
| **Link conversion (when sharing a link)** | "Get the exact product here 👇" or "Get the link here 👇" — converts at 15-20%. ("Check this out" only converts at 8-12%.) |

**For Aleem's call ask specifically:** Anchor to a Loom screen-share teardown ("I'll walk through what I'd automate first") rather than a generic "hop on a call." Sourced as higher-converting frame.

---

## Tone differences (Instagram vs LinkedIn)

**Sourced from Q3 section 3.** Critical for the OpenAI generator to internalize:

| Dimension | LinkedIn | Instagram |
|---|---|---|
| Tone | Professional-peer | Casual-peer |
| Capitalization | Standard | Lowercase OK ("yo", "hey") |
| Contractions | OK | Required ("you're", "I'm", "here's") |
| Emojis | Zero in cold | 1-3 OK (NEVER 10+) |
| Sign-offs | "- Aleem" or none | None — never sign off |
| Length | Up to 500 chars | Strict <100 words |
| Formatting | 1-3 lines | Broken into 2-3 short sections with white space |
| Robotic phrasing | Slightly tolerated | Kill-on-sight |
| Open-ended questions | OK | Required |

**Sample tone shift on the same message:**

❌ LinkedIn-style on Instagram:
> "Hey [Name], I noticed your recent post and wanted to reach out. We help businesses similar to yours optimize their operational workflows through AI automation. Would you have 15 minutes to discuss?"

✅ Instagram-style:
> hey [Name] - saw the reel on [specific thing]. that exact bottleneck is what we automate for [niche] founders. just took 12 hrs/week off another founder doing the same thing. wanted to flag. no ask.

---

## Speed-to-Lead rule (the highest leverage tactic)

**Sourced finding from CreatorFlow:** Responding within **1 minute** of a prospect reply gives **391% higher conversion** vs 30+ min response.

**Aleem operational rule:**
- During work hours: phone notification on for IG DMs. Reply within 1-5 min.
- Outside work hours: set up an auto-reply that doesn't sound automated — something like "I'm offline right now, will respond first thing tomorrow — what timezone are you in?" (Captures their context and signals legitimacy.)
- For replies during the closing-relevant window: switch to live-conversation playbook (`scripts/live-conversation-playbook.md`)

---

## Pre-warm workflow (the missing piece)

The current `instagram-outreach` skill scrapes and DMs cold. The data says this is leaving 40-50% delivery rate on the table.

**Proposed addition (flag for the linkedin-outreach script update):**

1. **Scrape leads** (existing) — gather 150 founders/COOs in target niche
2. **NEW: Pre-warm queue** — for each lead, before any DM:
   - Follow them
   - Like their last 1-2 posts
   - Leave one substantive comment on a recent post (not "great post!" — actual value)
   - Wait 3-5 days
3. **Then Touch 1** — by now you're a familiar profile, not a cold account

This is the single biggest change to make to the existing IG pipeline.

---

## Daily workflow (Aleem's operational version)

1. **Morning batch:** Pre-warm 30 new leads (follow + engage). Marks them "Warming - Day 1" in the CRM.
2. **Mid-morning:** For leads "Warming - Day 4+", send Touch 1 (max 30-40 DMs/day, spaced 2-5 min apart).
3. **Sequence touches:** Daily check of CRM for leads needing Touch 2, 3, 4. Send batch (also spaced).
4. **Live replies:** Notification-driven. Reply within 1-5 min if at desk.
5. **Track in Google Sheets CRM:** existing `instagram-outreach` infrastructure + new "Pre-warm Date" field.

---

## Conversion math (so Aleem knows what to expect)

Based on sourced 2026 benchmarks for targeted (not broadcast) DM:

```
Per 100 prospects properly pre-warmed + sequenced:
- 100 receive Touch 1 (after 3-5 day pre-warm)
- ~24-32 respond positively (CreatorFlow targeted-DM stat)
- ~7-20 convert to a call/sale (CreatorFlow DM-to-sale)
- Realistic close rate on Aleem's offer: 30-50%
- Expected: 2-10 closed clients per 100 properly-run IG prospects
```

This is BETTER than LinkedIn's 1-2 per 100 — IG has higher upside if pre-warm is done.

**To hit 4 clients/month from IG:** Run ~40-80 prospects/month through the full sequence. That's 10-20 pre-warm starts per week, sustainable.

---

## Worst-performing IG DM patterns (sourced kills)

From CreatorFlow / Jotform as documented failures:

1. **Robotic/formal phrasing** — "Thank you for your inquiry regarding our services..."
2. **Emoji-stuffed** — "Hey 👋 girl 💁♀️! Here's 🎉 your meal 🍽️ plan 📋..."
3. **Buried lead / too long** — opens with backstory, link buried at the bottom
4. **Generic pitch** — "Hey! We have an amazing opportunity for you. Check out our brand."
5. **"Bro"** — kill-on-sight, especially when DMing women
6. **"Love your content"** — #1 copy-paste tell
7. **3+ URLs in single DM** — spam filter trigger
8. **Copy-pasted identical messages** — #1 shadowban trigger

Full kill list: `references/what-not-to-do.md`.

---

## What this file is NOT

This is the COLD sequence. Once a prospect replies:
- **Live conversation** → `scripts/live-conversation-playbook.md`
- **Discovery call after they agree** → `scripts/discovery-call-script.md`
- **Objection handling** → `frameworks/objection-riffs.md`

For the OPENER per prospect:
- `frameworks/opener-archetypes.md` (Instagram leans heavily on Archetype 1 + 4)
