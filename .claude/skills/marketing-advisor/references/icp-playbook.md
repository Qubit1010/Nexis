# ICP Playbook 2026 (Identify, Score, Target)

**Source basis:** Distilled from `references/research-synthesis.md` Q1 (NotebookLM synthesis of 2026 sources). Key citations map to `_research/sources.json`. Tailored to NexusPoint (AI-automation + web agency). Cross-reference NexusPoint's current ICP in `nexuspoint-positioning.md`.

**Why this matters:** 68% of B2B firms have no clear ICP; the ones that do report **68% higher win rates** [s112, s183]. Only **5-10%** of any ICP is in-market right now, and **79%** of marketing leads never convert because teams chase poor-fit accounts [s183]. A sharp ICP is the highest-leverage decision in the whole funnel.

---

## Step 1 - Build the ICP from closed-won data, in 5 layers

Don't invent an ICP from a wish list. Start from who actually paid, stayed, and referred. Define five layers [s112, s183]:

1. **Firmographic fit** - industry, employee count, revenue, geography, funding stage.
   - 50-200 employees avoids enterprise procurement hell while having budget.
   - Funding stage signals: **post-Series B** companies actively rebuild ops stacks; post-Series D optimize existing ones.
2. **Technographic fit** - the software stack reveals budget + integration readiness. A company on HubSpot + a real data layer signals it's ready for automation. Check via BuiltWith/Wappalyzer or job posts.
3. **Behavioral signals** - hiring patterns, funding events, tech migrations = near-term budget.
4. **Organizational readiness** - is there a decision-maker who owns this? No COO / Head of Ops / RevOps = automation deals stall in committee. Average B2B deal needs **6-10 stakeholders** to agree [s183].
5. **Negative indicators (Anti-ICP)** - disqualify: public layoffs, hiring freezes, high-churn traits, sub-$1k budgets, "just want a cheap website" buyers, student/free email domains.

**NexusPoint ICP starting point** (validate against closed-won): funded startups / profitable SMBs, 5-50 staff, $500K-$10M revenue, founder or Head of Ops who sees tech as a growth lever, bleeding time on manual ops or a website that doesn't convert. Anti-ICP and full profile: `nexuspoint-positioning.md`.

---

## Step 2 - Score fit and intent SEPARATELY

Never collapse "should we sell to them?" (fit) and "are they ready now?" (intent) into one number - it hides reality [s44]. Use a 100-point rubric across six families:

| Signal family | Weight | Examples |
|---------------|--------|----------|
| Firmographic fit | 35% | revenue, industry, size |
| Behavioral intent | 20% | repeat pricing-page visits, demo/form abandonment |
| Technographic fit | 15% | stack compatibility, competitor displacement |
| Persona/role fit | 15% | senior decision-maker present |
| Buying signals | 15% | job listings, funding |
| Negative signals | subtract | anti-ICP traits |

**Time decay rule:** intent is volatile. Decay behavioral scores **10-20% every 30 days** so you call accounts on current temperature, not old clicks [s44].

**Routing thresholds** [s44]:
- **Tier A (80+):** contact within 1 hour (these close at **2x** the normal rate).
- **Tier B (60-79):** nurture until intent spikes.
- **Tier C (<60):** low-touch automated hold. Keep sales away.

---

## Step 3 - Read buying-intent triggers (timing is everything)

Three rings of signal [s200]:
- **First-party (highest value):** "inbound multithreading" - e.g. an analyst downloads a resource and their ops director hits the pricing page within 48h. Form abandonment is prime.
- **Second-party:** spikes in relevant search ("custom n8n integration"), competitor research, negative G2/TrustRadius reviews of a competitor.
- **Third-party triggers (best for cold outreach):**
  - **New COO/Head of Ops** - incentivized to ship modern workflows in their first 90 days. Reach out fast.
  - **Funding round** - the **6-month window after funding** is peak buying intent.
  - **Hiring surges for manual roles** (data entry, SDRs, ops coordinators) - public proof of a bottleneck ripe for automation. This is NexusPoint's sharpest signal.

---

## Step 4 - Validate a new vertical before scaling into it (2-4 weeks)

Don't burn domain reputation scaling outbound into an unvalidated niche [s193, s215]:
1. **30-50 discovery interviews** with target decision-makers. Listen for **70%+ consistency** on the same pain.
2. **Sean Ellis test:** show a low-fi mockup, ask "how would you feel if this didn't exist?" If **≥40% say "very disappointed,"** you have problem-solution fit.
3. **Landing page test:** drive paid traffic; benchmark **3-5% email signup** or 1-2% pre-order.
4. **Paid pilots:** discounted pilot builds; target **10 paying pilots in 30 days** before going all-in.

---

## Step 5 - Find where decision-makers actually are

General feeds are saturated; ops/growth leaders retreated to private "watering holes" [s170, s53]. Go native there before/around outreach:
- **Ops & RevOps (Slack):** RevOps Co-op (15k+), Wizards of Ops (WizOps), Operations Nation (700+ COOs/VPs).
- **Growth & marketing:** Demand Curve, Superpath (15k+ content/SEO), Traffic Think Tank, Online Geniuses (53k+).
- Plus LinkedIn (founder-led content, see `linkedin-playbook.md`) and niche communities for the client's vertical.

---

## Step 6 - ABM for a small agency (the highest-ROI tactic)

Spray-and-pray gets <2.1% replies and burns domains. Restrict ABM to accounts with projected **ACV ≥ $10,000** to justify the effort [s37].

**The Personalized Loom Workflow Audit** (converts best, 2-minute format) [s44]:
- **0:00-0:30 Hook** - trigger-based context: "Saw [Company] is scaling outbound while hiring a RevOps lead."
- **0:30-1:30 Value** - screen-share a mock n8n/Make workflow: "incoming lead gets parsed by AI, scored, routed to Slack in 6 minutes, cutting manual entry ~60%."
- **1:30-2:00 CTA** - ask for a 15-min diagnostic. Embed the Loom as an animated GIF thumbnail in the email.

Build a narrow target list (intent data if available), engage decision-makers natively in their communities, then follow up by email with trigger-based insight. For the actual DM/email copy and the diagnostic-call script, hand off to the **sales-playbook** skill (clean split: marketing-advisor defines WHO + WHY + the campaign; sales-playbook writes the 1:1 message).

---

## Quick application
- "How do I find my ICP?" -> run Step 1 from closed-won, then validate (Step 4) if it's a new niche.
- "Who should I target this week?" -> filter for Tier A intent triggers (new COO, recent funding, manual-role hiring).
- "Is this lead worth pursuing?" -> score fit vs intent separately (Step 2); below 60 = automated hold, not a call.
