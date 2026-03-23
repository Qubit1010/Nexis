---
name: proposal-generator
description: "Generate client proposals using the Hormozi $100M Offers framework and create formatted Google Docs. Use when someone asks to create a proposal, draft a proposal, generate a client proposal, write a project proposal, build an offer, scope a deal, write a SOW, or anything related to proposal/offer creation for client work. Also triggers on: 'proposal for [client]', 'draft an offer', 'put together a proposal', 'scope this as a proposal'."
argument-hint: [scope brief or client name]
disable-model-invocation: true
---

# Proposal Generator

Generate high-converting client proposals using Alex Hormozi's $100M Offers framework. Creates a formatted Google Doc saved to the NexusPoint Proposals folder in Google Drive.

## When to Trigger

Activate when the user:
- Asks to create, draft, generate, or write a proposal
- Wants to build an offer or scope a deal
- Says "proposal for [client]", "draft a proposal for...", "put together an offer"
- Needs a SOW (statement of work) or project proposal
- Wants to convert a scope brief into a client-ready document

## Context Loading

Before generating, read these files for business context:
- `context/work.md` — NexusPoint services, pricing benchmarks, tech stack
- `context/team.md` — Who delivers what (for realistic timelines and team allocation)
- `.claude/skills/proposal-generator/references/hormozi-framework.md` — The full Hormozi framework (read this every time)

Optionally read `.claude/skills/proposal-generator/references/proposal-schema.json` for the JSON schema example if you need a refresher on the output format.

## Workflow

### Step 1: Intake Scope Brief

Parse the user's input (from `$ARGUMENTS` or conversation). Extract:
- **Client name** (required)
- **Industry/niche** (required)
- **Core problem** — what they need solved
- **Desired deliverables** — what they're asking for
- **Constraints** — budget range, timeline, tech preferences
- **Special notes** — anything else relevant

If any required field is missing, ask specifically for it before proceeding. Keep questions focused:
> "What's the client's name and industry?"
> "What's the core problem they need solved?"

Do not proceed without at minimum: client name, what they need.

### Step 2: Apply Hormozi Framework

Reference `references/hormozi-framework.md` and work through these sub-steps:

**A. Dream Outcome (the "So That" method)**
Chain the deliverable through 3-4 "so that" layers until you reach the real business outcome. The final layer becomes the proposal's headline promise.

Example: "We build an AI chatbot **so that** support tickets drop 60% **so that** your team handles 3x the volume **so that** you scale without hiring."

**B. Map Problems to Solutions**
For each deliverable area, identify friction across the four categories:
- **Time** — What takes too long? What's delayed?
- **Money** — What's being wasted? What's the cost of inaction?
- **Effort** — What's manual that should be automated?
- **Fear** — What could go wrong? What's their past bad experience?

Flip each friction point into a named solution. Use distinctive, branded names (not "website" but "Revenue-Optimized Conversion Platform").

**C. Build the Value Stack**
- List 4-6 deliverables with standalone market values
- Each gets: a branded name, one-line outcome description, value estimate
- Total value should be 5-10x the proposed price

**D. Trim & Stack**
- Core Offer: 2-4 high-value items solving the main problem
- Bonuses: 2-3 items that are low cost to deliver but high perceived value
- Each bonus needs: name, retail value, benefit, why it's free

### Step 3: Generate Proposal JSON

Build a JSON object matching this structure:

```json
{
  "client_name": "Client Name",
  "industry": "Industry",
  "date": "YYYY-MM-DD",
  "title": "The [MAGIC Name] -- Proposal for [Client]",
  "sections": [
    {"heading": "...", "level": 1, "body": "..."},
    {"heading": "...", "level": 2, "bullets": ["...", "..."]},
    {"heading": "...", "level": 1, "table": {"headers": [...], "rows": [...]}}
  ]
}
```

**Section types:**
- `heading` + `level` (1=H1, 2=H2, 3=H3) — Section title
- `body` — Paragraph text
- `bullets` — Array of bullet point strings
- `table` — Object with `headers` (string array) and `rows` (array of string arrays)

A section can combine heading + body + bullets + table. All are optional except at least one must be present.

**Required proposal sections (A through J):**

**A. Offer Name (H1)** — Use the MAGIC formula: Magnetic reason + Avatar + Goal + Interval + Container. Example: "The Q1 Revenue Acceleration 90-Day System for SaaS Founders"

**B. Problem Statement (H1)** — 2-3 paragraphs. Articulate their pain better than they can. Be specific and visceral. Reference their industry, not generic business problems.

**C. Dream Outcome (H1)** — 1-2 paragraphs painting the "after" picture. Include at least one hard metric and a timeframe.

**D. Solution Overview (H1) + Core Deliverables (H2)** — Brief intro paragraph, then bulleted list of core deliverables. Each bullet: "Name ($X,XXX value) -- one-line outcome description."

**E. Bonuses (H2)** — Bulleted list. Each: "Name ($X,XXX value) -- benefit. Yours free because [reason]."

**F. Deliverables & Timeline (H1)** — Table with columns: Phase, Deliverables, Timeline.

**G. Your Investment (H1) + Value Stack (H2)** — Table showing each deliverable and its value, with total at bottom.

**H. Pricing Options (H2)** — 2-3 tiers in a table (Essential, Growth, Scale) OR single price with ROI math in body text. Anchor with highest tier first.

**I. ROI Math (H2)** — Body text showing exactly how the investment pays for itself. Use specific numbers.

**J. Our Guarantee (H1)** — Stack two guarantees: unconditional (14-day refund) + conditional (performance metric by date). Name each guarantee.

**K. Why Now (H1)** — Capacity limit, bonus expiration, proposal validity window (7 days).

**L. Next Step (H1)** — Single, clear CTA. Low friction. Reinforce the dream outcome.

### Step 4: Create Google Doc

Pipe the JSON to the creation script:

```bash
echo '<proposal_json>' | python .claude/skills/proposal-generator/scripts/create_proposal_doc.py
```

The script:
1. Finds or creates the "NexusPoint Proposals" folder in Google Drive
2. Creates a blank Google Doc with the proposal title
3. Inserts all text content with proper heading styles, bullets, and formatting
4. Creates and populates tables (timeline, value stack, pricing)
5. Returns the doc URL

### Step 5: Present Result

Show the user:
1. The Google Doc URL
2. A brief summary of key proposal elements (offer name, total value, price point, guarantee)
3. Ask if they want to adjust any sections

## Writing Rules

- **Tone:** Confident, direct, outcome-focused. Never apologetic or hedging.
- **Language:** Specific to their industry. No generic business jargon.
- **No emojis.** No em dashes in proposal content (use commas or periods).
- **Position AI/automation as the premium differentiator** when relevant to the deliverables.
- **Never auto-send to the client.** Always present the doc for Aleem's review first.
- **Value estimates should be realistic** — based on market rates for similar services, not inflated.
- **Timeline should be achievable** — reference `context/team.md` for who's available and realistic delivery speeds.

## Pricing Guidelines

Reference `context/work.md` for NexusPoint's service pricing benchmarks:
- Web design & development: $3K-$25K depending on complexity
- AI automation & workflows: $2K-$15K
- Custom SaaS / web apps: $5K-$30K
- CMS builds: $1.5K-$8K

Price the proposal based on actual scope, not a formula. The value stack should be 5-10x the price to make it feel like a deal.

## Edge Cases

- **Vague scope brief:** Ask 2-3 specific questions before proceeding. Don't generate a generic proposal.
- **No budget mentioned:** Default to mid-range pricing for the service category. Include 2-3 tiers.
- **Multiple services needed:** Bundle into a single offer with a unified name, not separate proposals.
- **Existing client:** Skip the trust-building sections (guarantee, urgency). Focus on deliverables and timeline.
- **Script fails:** If the Google Doc creation fails, output the proposal JSON to the conversation so the user can still review the content. Suggest manual doc creation.
