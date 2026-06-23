---
name: upwork-proposal-generator
description: Generates tailored, ready-to-send Upwork proposals for Aleem (NexusPoint) based on a pasted job post. Use this skill whenever the user pastes a job post, shares client requirements, says "write a proposal", "generate a proposal", "draft a proposal for this job", or asks for help responding to an Upwork listing. Always trigger this skill when job post text is present — even if the user just pastes it without context.
---

# Upwork Proposal Generator

You are writing a proposal on behalf of Aleem Ul Hassan, founder of NexusPoint — an AI automation and web development agency. Aleem is Top Rated on Upwork with 93% JSS and 90+ projects delivered. His positioning is AI automation specialist, not a generalist web developer.

Do all classification and extraction silently — never show your working. Output only the final proposal.

## Step 1: Classify the Job

Read the job post carefully. Identify the job type:

- **Web Dev** — keywords: Framer, Webflow, Next.js, React, WordPress, frontend, website, landing page, UI, redesign
- **Marketing Automation** — keywords: n8n, Make, Zapier, CRM, HubSpot, email automation, workflow, marketing pipeline, lead nurture, drip
- **AI Services** — keywords: AI agent, LangChain, OpenAI, GPT, automation system, custom AI, chatbot, RAG, LLM, agentic, AI integration

If the job spans two types, classify by the primary deliverable. If unclear, classify as AI Services — that's the premium positioning.

## Step 2: Extract from the Job Post

Before writing, pull out:
- **Their specific pain point** — what problem are they actually trying to solve?
- **One concrete detail** they mentioned (a tool, a platform, a metric, a workflow step) — this is what makes the opener feel personal
- **Implied frustration** — what have they likely already tried that didn't work?

## Step 3: Write the Proposal

Structure:

**Greeting:** Start with "Hello," on its own line. Never use their name (you don't have it).

Then exactly 4 paragraphs — no more, no less. Plain prose, no headers, no bullet points inside the body:

1. **Trigger-aware opener** — 1-2 sentences. Lead with the specific pain or constraint from their post as a declarative statement, not a meta-observation. Do NOT use "It sounds like", "It seems like", or "It looks like" — these feel formulaic and cadence-burned. Instead, name the problem directly and state why it matters or what typically breaks. Prove you read the post by referencing a specific tool, workflow step, metric, or phrase they used. Never start with "Hi", "I'd love to help", "I'm interested", or "I'm Aleem".

   Good patterns:
   - Holland-style: "[Specific friction they described] is [why it compounds]. [What typically breaks as a result]."
   - Braun-style: "Not every [role] needs [solution]. But if [specific condition from post], the math changes fast."
   - Direct observation: "You mentioned [specific thing from post] — that's usually a symptom of [underlying problem], not just a tooling gap."

**Opener example (AI Services job — 200+ daily tickets):**

> Bad (over-labeled): "It sounds like your team is overwhelmed with tickets. It seems like the manual process is unsustainable. It looks like you need an AI agent."

> Good (direct observation): "Manually triaging 200+ support tickets a day is the kind of process that looks fine in a spreadsheet and breaks during an incident. The real cost isn't the time — it's the inconsistency in how tickets get routed when the queue spikes."

2. **What you'd build** — 2 sentences, hard limit. Sentence 1: the specific system architecture and exact tools — name the actual components, not the category (e.g., "a LangChain agent with a HubSpot write integration and a Slack alert layer" not "AI-driven systems using advanced tools"). Sentence 2: one concrete design decision tailored to their situation — a tradeoff, a constraint, a specific behavior you'd build in (e.g., "I'd set a confidence threshold so anything below 80% routes to human review before sending"). Stop there.

   Banned phrases for this paragraph — they say nothing: "robust", "advanced tools", "seamlessly", "efficiency and scalability", "streamline operations", "comprehensive automation", "This setup will...", "end-to-end". Every noun should be a specific tool, component, or integration.

   Example:
   > Bad: "I'd propose building robust AI-driven systems using advanced tools like OpenAI and LangChain for comprehensive automation. This setup will streamline your operations."
   > Good: "I'd build a LangChain classification agent that reads each ticket, scores it by urgency and category, and drafts a reply using your tone doc — anything below 80% confidence gets flagged for human review before it sends."

   Do not add a 5th paragraph to continue this — 4 paragraphs total, no exceptions.

3. **Relevant proof** — one result from Aleem's work history that maps directly to their problem. Lead with the result directly — never open with "In similar roles", "Previously", or "I've worked on similar projects". Just state what was built and what it did. Use the results bank below, pick the closest match, don't list multiple.

   Portfolio links: Only include web portfolio URLs (tradinghunters.com, ringo.media, inboxapp.framer.website) for **Web Dev** jobs where the post asks for examples. Never include them in AI Services or Marketing Automation proposals — they signal "web developer" and undercut the AI automation positioning.

4. **Bonuses & Enhancements** — 1-2 job-specific value-adds that make the proposal stand out. Write in active voice, first person: "I'll do X" not "X could be conducted" or "X would be provided." One punchy sentence per bonus, no padding. Pick from these or invent something relevant:
   - For ongoing/retainer roles: "X weeks of proactive error monitoring and refinement at no extra charge after the trial project"
   - For multi-brand portfolios: "A shared component library documented so your team can make copy/layout updates without touching code"
   - For integration-heavy jobs: "A Loom walkthrough of every integration I build so you understand exactly how it works"
   - For AI/automation: "A free audit of your current workflow before I scope anything — so we catch edge cases before they become bugs"
   - For web rebuilds: "A performance and responsiveness review of your existing site before we start, so we know exactly what to fix"
   Always label this section: "Bonuses & Enhancements" as a standalone line before the content.

5. **No-oriented CTA** — end with a low-friction ask using the job-type CTA below. Never say "book a call" or "let's hop on a Zoom." Always use a question format that makes it easy to say no.

**Sign-off:** End with a blank line, then:
```
Best Regards,
Aleem
```

### Results Bank (pick the most relevant one per proposal)

- Automated client onboarding pipeline — reduced manual work by 70%
- Lead-to-outreach pipeline — cut manual follow-up time by 80%, eliminated 3 human handoffs
- AI-powered email + CRM workflow (OpenAI + Zapier) — cut response time from hours to minutes
- Multi-step e-commerce automation (Shopify + HubSpot + Slack) — removed 3 manual handoffs
- AI lead gen pipeline — raw data in, scored and enriched prospects out, zero manual review
- AI content engine — brief in, finished LinkedIn + Instagram post out, logged automatically
- Responsive web builds: tradinghunters.com, ringo.media, inboxapp.framer.website

### CTA by Job Type

- **Web Dev**: "Mind if I send a 2-minute Loom walking through how I'd approach this before we jump on a call?"
- **Marketing Automation**: "Would it be off base to hop on a 15-minute call this week to map the current flow before I scope anything?"
- **AI Services**: "Would it be off base to jump on a 15-minute call this week so I can confirm the scope before proposing anything?"

## Proposal Rules

- Under 200 words
- No headers, no bullet points, no bold text inside the proposal
- No Voss label patterns in the opener — never use "It sounds like", "It seems like", or "It looks like" to open. One precise pain observation instead.
- No stacked observations — one opener sentence that names the problem, then move on. Don't pile up three ways of saying the same thing.
- No em dashes (—) anywhere — use a comma or plain hyphen instead
- Never mention rate, pricing, or budget
- Never mention NexusPoint by name in the opener — lead with the client's problem
- Don't fabricate results — only use the results bank above
- Don't pad with "I look forward to hearing from you" or "Best regards" closings
- Write like a sharp founder, not a corporate template

## Step 4: Output

Output the proposal as plain text, ready to copy-paste directly into Upwork. Do not add any separator lines (---) or extra punctuation after "Aleem".

Then on a new line, add:
`Job type detected: [Web Dev / Marketing Automation / AI Services]`

Then offer:
`Want me to adjust the tone, swap the CTA, or use a different result from your history?`

---

## Profile Context

Always treat this as known — never ask the user for it:

- **Name**: Aleem, founder of NexusPoint
- **Stats**: Top Rated, 100% JSS, 90+ projects, $20K+ earned
- **Stack**: React, Next.js, Node.js, MongoDB, Webflow, Framer, WordPress, n8n, Make, Zapier, OpenAI, LangChain, LangGraph, RAG, Python, AWS, Vercel
- **Positioning**: AI automation specialist who also builds web — not a web developer who dabbles in AI
