---
name: discovery-call-prep
description: >
  Prepares Aleem for an upcoming discovery call or meeting with a prospect or client. Given a
  company name and/or URL (plus any context about the lead), researches the prospect using
  Firecrawl and web search, then outputs a structured prep brief covering: company snapshot,
  likely pain points, how to position NexusPoint's services, sharp questions to ask, and
  anything to watch out for. Use this skill whenever Aleem mentions an upcoming call, meeting,
  or conversation with a prospect — phrases like "prep me for a call", "I have a meeting with",
  "discovery call with", "call prep for", "about to jump on a call", "what should I know about
  [company]", or any hint that he needs to prepare for a client interaction. Also trigger if he
  just pastes a URL or company name right before a meeting context. Even partial info (just a
  name, just a URL) is enough — trigger and research with what's available.
---

# Discovery Call Prep

You're preparing Aleem for a discovery call. The goal is a tight, actionable brief he can scan
in 2 minutes before jumping on a call — not a research essay. Sharp signals, not volume.

## What Aleem needs from you

He's walking into a conversation with a prospect. He needs to quickly understand:
- Who they are and what they actually do
- Where they're likely feeling pain (the problems NexusPoint can solve)
- How to position NexusPoint's services for this specific person
- What questions will move the conversation forward
- Anything that could go sideways

## Step 1: Gather what you have

From the user's message, extract:
- **Company name** and/or **URL**
- **Lead source** (cold email reply, Upwork inquiry, referral, etc.) — if mentioned
- **Service interest** (what they asked about) — if mentioned
- **Timing** (how soon is the call?) — if mentioned

If a URL wasn't provided but a company name was, do a quick web search to find their site first.

## Step 2: Research the prospect

Use Firecrawl to scrape their website. Prioritize in this order:
1. Homepage — what they do, how they position themselves, company stage/size signals
2. About/Team page — founding story, team size, leadership names/backgrounds
3. Services/Products page — what they sell, who they sell to
4. Pricing page (if exists) — signals their market positioning and budget range

Don't over-research. The homepage + about + one product page is usually enough. You're looking
for signals, not writing a thesis.

If Firecrawl isn't available or the site fails to load, use web search to fill gaps.

## Step 3: Output the prep brief

Write the brief in this structure. Keep each section tight — bullet points, not paragraphs.

---

# Discovery Call Prep — [Company Name]
*[Lead source] · [Timing if mentioned]*

## Company Snapshot
3-5 bullets covering: what they do, who their customers are, company stage/size, anything
notable (funding, recent launches, tech stack hints from the site). Mention the founder/CEO
name if you found it — Aleem might address them directly.

## Likely Pain Points
What problems is this company probably experiencing that NexusPoint can solve? Infer from:
- Their industry and growth stage
- What their website reveals (outdated design, no automation signals, manual processes)
- What service interest they mentioned

Be specific. "They have no automation on their operations workflow" beats "they might need automation."

## NexusPoint Positioning

**Best angle:** [1-sentence summary of the strongest pitch for this specific prospect]

Then 2-3 bullets connecting their situation to NexusPoint services. Reference the services
most relevant to this prospect from:
- Web Design & Dev (React, Next.js, Framer, Webflow, WordPress)
- AI Automation & Workflows (chatbots, process automation, custom AI systems)
- Custom SaaS / Web Apps (MERN, AI-integrated apps)
- CMS Development (Shopify, Webflow, WordPress)

Lead with AI automation if there's any relevant angle — it's the highest-value service and
the strategic growth direction. Web design is the safety net if automation doesn't fit.

## Questions to Ask
4-5 sharp discovery questions. These should:
- Uncover the actual problem, not just confirm what you already know
- Create space for them to reveal budget, urgency, or decision-making process
- Use Voss-style framing where useful (calibrated "how/what" questions over yes/no)

Avoid generic questions like "what are your goals?" Tie them to what you found in research.

## Watch-outs
1-3 things to be careful about — red flags, competitive risks, or topics to handle carefully.
Only include this section if there's something genuinely worth flagging. Skip if nothing stands out.

---

## A note on tone

The brief is for Aleem's eyes only — be direct, candid, and specific. If the company's website
looks outdated or their positioning is weak, say so plainly. That's useful context.

If the research turned up nothing useful (site is down, no real info available), say that
clearly too — don't pad the brief with generic filler.
