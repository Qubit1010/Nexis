# Test post — "The AI Outreach Roadmap" (one filled single-image prompt)

Fully filled example for testing the Gem. Build the Gem from `gem.md` first (attach both Knowledge
images). Then paste the single block below and wait for the one infographic image.

This produces ONE 1080x1350 infographic, not a carousel. Fix it with
`regenerate, same layout, change [X]`.

---

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (top, bold grotesque, left-aligned):
"The AI Outreach Roadmap"
Highlight these words in orange (#E85D1A): "AI Outreach"
All other title words in black (#1A1A1A). "The" and "Roadmap" in regular weight.

SUBTITLE: "12 steps. Scrape to signed client. Real prompts inside."

BRAND: place the NexusPoint logo (from Knowledge) ~100-120px tall at the top-right of the title block.

PAGE BACKGROUND: #FAFAF8 (near-white) throughout.

HERO STEP (full-width strip below title):
STEP NUMBER: "STEP 00"
STEP NAME: "CRM"
STEP SUBTITLE: "set up once, run forever"
DESCRIPTION: "Create your outreach CRM sheet before anything else. Every lead, message, and follow-up lives here."
ACTION EXAMPLE: "$ gws sheets create --title 'NexusPoint Outreach CRM'"

---

PHASE 01 (accent: blue #3A88C5):
PHASE LABEL: "PHASE 01"
PHASE NAME: "FIND"
PHASE SUBTITLE: "where your leads come from"

  CARD 01:
  STEP NUMBER: "01"
  STEP NAME: "scrape"
  BODY: "Pull raw leads from LinkedIn, Instagram, or Facebook groups using the leads-to-CRM skill. 20-50 leads per run."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Push my new Instagram leads into the CRM with Touch 1 messages."

  CARD 02:
  STEP NUMBER: "02"
  STEP NAME: "enrich"
  BODY: "Add context to each lead. What they do, what problem they have, why now. Better context = better message."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Enrich the last 10 leads in my CRM with a pain point and a reason to reach out now."

  CARD 03:
  STEP NUMBER: "03"
  STEP NAME: "score"
  BODY: "Rank leads by ICP fit. Spend time on high-fit leads first, not whoever replied first."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Score my leads on ICP fit (1-10) based on business size, niche, and tech stack."

PHASE 02 (accent: orange #E85D1A):
PHASE LABEL: "PHASE 02"
PHASE NAME: "REACH"
PHASE SUBTITLE: "your first message"

  CARD 04:
  STEP NUMBER: "04"
  STEP NAME: "opener"
  BODY: "Send a platform-specific cold opener based on a genuine observation. No templates that smell like templates."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Draft a LinkedIn cold opener for [lead name] at [company]. Angle: their broken checkout flow."

  CARD 05:
  STEP NUMBER: "05"
  STEP NAME: "follow-up"
  BODY: "Send 2-3 follow-ups spaced 3-5 days apart. Most replies come on the second or third touch."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Write a follow-up for [lead] who hasn't replied to my opener. Don't mention the last message."

  CARD 06:
  STEP NUMBER: "06"
  STEP NAME: "reply"
  BODY: "When they respond, use the sales playbook skill to handle objections and move toward a call."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "They said: 'We already have someone for that.' What's my next move?"

PHASE 03 (accent: purple #7055A0):
PHASE LABEL: "PHASE 03"
PHASE NAME: "QUALIFY"
PHASE SUBTITLE: "turning replies into calls"

  CARD 07:
  STEP NUMBER: "07"
  STEP NAME: "discovery"
  BODY: "Run the 30-min Ops Teardown call. Uncover the real pain before pitching anything."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Prep me for a discovery call with [lead]. Their niche: e-commerce. Known pain: manual order tracking."

  CARD 08:
  STEP NUMBER: "08"
  STEP NAME: "proposal"
  BODY: "Send a Hormozi-framed proposal within 24 hours of the call. Use the proposal generator skill."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Create a proposal for [lead]. Project: AI order automation. Budget signal: $2,000-5,000."

  CARD 09:
  STEP NUMBER: "09"
  STEP NAME: "close"
  BODY: "Follow up on the proposal with a calm, confident close. One question, not a pitch."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Draft a follow-up to my proposal for [lead] who went quiet after 3 days."

PHASE 04 (accent: teal-green #2DAA84):
PHASE LABEL: "PHASE 04"
PHASE NAME: "DELIVER"
PHASE SUBTITLE: "signed client to great outcome"

  CARD 10:
  STEP NUMBER: "10"
  STEP NAME: "onboard"
  BODY: "Spin up the Drive folder, onboarding doc, and welcome email the day they sign. Use client onboarding skill."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "We just signed [client]. Set up the full onboarding kit for them."

  CARD 11:
  STEP NUMBER: "11"
  STEP NAME: "build"
  BODY: "Execute the project. Track tasks in the project workspace. Surface blockers early."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Mark 'initial wireframes' done for [client] and show me what's next."

  CARD 12:
  STEP NUMBER: "12"
  STEP NAME: "retain"
  BODY: "After delivery, pitch a retainer. One great project becomes recurring revenue with the right ask."
  ACTION LABEL: "PASTE INTO CLAUDE"
  ACTION TEXT: "Draft a retainer pitch for [client] after we delivered their AI chatbot. Monthly maintenance + updates."

---

RULES: near-white background (#FAFAF8); cards white (#FFFFFF) with thin grey border (#E5E5E5); phase header bars solid accent color, all text white; card header strips solid accent color, step name and number in white; action boxes light-grey (#F4F4F2) with small copy icon bottom-right; all text legible at 1080x1350; no emojis; no em dashes.
One image only.
```

---

Fix any issue with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
