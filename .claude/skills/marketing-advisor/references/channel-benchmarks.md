# Channel Benchmarks 2026 (The Scoreboard)

**Source basis:** Every number here is pulled from `references/research-synthesis.md` (a NotebookLM synthesis of 234 unique 2026 sources). Citations like `[s156]` map to the global source index in `_research/sources.json`. Use these as the scoreboard: targets to beat, not guarantees. Always measure NexusPoint's own numbers and beat the baseline.

**Honesty rule:** If a number isn't here or in the synthesis, don't invent one. Say "I don't have a 2026 benchmark for that."

---

## Email (cold + nurture)

| Metric | 2026 benchmark | Notes |
|--------|---------------|-------|
| Cold reply rate (avg) | **3.4%** | Top 10% (90th pct): **8-12%+** [s39, s61] |
| Cold open rate | **~27.7% true** (42-44% inflated by Apple MPP) | Stop using opens as a KPI [s39, s216] |
| Cold bounce rate | **5.1% avg**, top senders **<1.5%** | Purchased lists hit 18.5% bounce [s41] |
| Cold -> closed deal | **~0.215%** (≈1 deal per 464 sends) | Plan volume around this [s63] |
| Nurture open / click | **39.26% open / 6.21% click** | Permission email beats cold [s143] |
| Welcome email open | **~80%** (or 35.5% true baseline) | Multi-email welcome = +90% orders [s199] |
| Meeting-booked (SMB <$1k ACV) | **1.0-2.5%** | [s62] |
| Meeting-booked (mid $1k-25k ACV) | **0.5-1.5%** | [s62] |
| Meeting-booked (enterprise $100k+) | **0.3-0.8%** | [s62] |

**Reply rate by industry (cold):** Legal ~8-10%, Recruiting 5.8-7.2%, Healthcare 4-6%, Real Estate ~3.8%, Agency->SMB 4.2%, Financial 1.5-4%, **SaaS/Software 1-4% (lowest, inbox saturation)** [s62].

**Cold sequence shape:** 4-7 emails. **58% of replies come from email 1**, 35% from touches 2-4, 7% from 5-7 [s61]. First touch <80 words; body 50-125 words = 2.4x reply vs >200 words [s64]. Mostly plain text, max one link.

---

## LinkedIn (organic + outreach)

| Metric | 2026 benchmark | Notes |
|--------|---------------|-------|
| Algorithm | Interest Graph ("360Brew", 150B-param AI) | Reads semantic content, not network proximity [s185, s186] |
| Organic reach since shift | impressions **-63-66%**, views **-50%**, engagement **-25%** | Bar is higher now [s185] |
| "Golden Hour" test | post shown to **2-5% of network**; needs **5-10% ER** to advance | <2% ER kills it (87% of posts die here) [s186] |
| Dwell time (#1 signal) | 0-3s = **1.2% ER**; 61s+ = **15.6% ER** (13x) | Optimize for read time, not likes [s186] |
| Document/PDF carousel ER | **6.6-7.0%** (highest format) | 5-15 slides; +278% vs video [s146, s185] |
| Native vertical video ER | **4.7-5.6%** | 30-90s, hook in 1-2s, 9:16 = +71% impressions [s185] |
| Text post ER | **2.0-4.5%** (expert 6-8%) | Sweet spot 150-300 words / 800-1000 chars [s186] |
| Newsletter open rate | **40-60%** | Bypasses feed; triggers email+push [s154, s155] |
| External link in body | **-60-68% reach** | Put link in a comment? Also penalized now [s185] |
| Personal vs company page | personal = **8x engagement, 5.6x reach** | Founder-led wins [s85] |
| Cadence | **3-5 posts/week**; Tue-Thu; 7-10am, 12-1pm, 2-4pm local | [s146, s222] |
| Connection acceptance (avg) | **28.5-30%** | Personalized/pre-warmed: **55-70%**; generic mass: 12-18% [s156, s149] |
| Safe connection volume | **80-100/wk** (cloud automation 20-25/wk) | <20% acceptance = penalty box [s156, s38] |
| Connection-note reply | **2.2-3.0%** (down 37% YoY) | [s156] |
| Post-acceptance DM reply | **10.4% avg**; good 10-25%; elite multi-touch 30-50% | [s156, s157] |
| InMail (Message Ads) | **57.5% open, 10-25% reply, ~3.2% CTR** | [s148] |
| Omnichannel lift | LinkedIn+email+phone = **+287% purchase** vs email alone | [s150] |

---

## Instagram / Reels

| Metric | 2026 benchmark | Notes |
|--------|---------------|-------|
| Reels views from non-followers | **55%** | Best cold-acquisition tool on IG [s130, s135] |
| Reels avg reach rate | **30.81%** (2x+ static/carousel) | [s130] |
| Ranking signals (in order) | Watch time/completion > Sends-per-reach > Likes | Sends = **3-5x** weight of likes; Saves = **3x** [s119, s184] |
| Ideal length | **15-30s** sweet spot (up to 3 min for Explore) | Completion beats length: 15s@80% > 3min@20% [s126, s184] |
| 3-second drop-off | up to **50% scroll past in 3s** = 71% of total drop-off | Win the first 1.5-3s [s100, s184] |
| 3-sec hold-rate bench | <50% kills reach; **60%+ strong; 65-70%+ expands; 75%+ exceptional** | [s127] |
| Hook rate (3s plays / impressions) | **>25% good**, <15% degrades CPM | [s127] |
| Avg watch time | **8.4s** (top 25%: 18s+) | Aim >50% of duration [s120] |
| Completion rate | **42% avg** (top 25%: 68%) | [s120] |
| Shares-to-reach | **0.8% avg** (top 25%: 2.5%); >3% = viral | [s120] |
| Saves-to-reach | **1.2% avg** (top 25%: 3.8%) | [s120] |
| Cadence | **3-5 Reels/week** | 1->3-5/wk = +12% reach/post, 2x follower growth [s98] |
| Hashtags | **3-5 niche** (30 = spam penalty) | Caption semantics matter more [s119] |

**Watch-on-mute:** 60-85% of short-form is watched muted; captions/kinetic text = +25% retention [s175].

---

## Content / Short-form (cross-platform)

| Metric | 2026 benchmark | Notes |
|--------|---------------|-------|
| Short-form 3s drop-off | **50% in 3s** = 71% of drop-off; <45% retention if no hook by 15s | [s69] |
| Jump cuts | every **2-4s**; scene change every 3 sentences | [s69] |
| Script density | **~75 words / 30s** | [s175] |
| Repurposing flywheel | 1 pillar = **20-30 derivative pieces** (12-15 "knowledge atoms") | [s33] |
| Repurposing ROI | cost/piece $150-300 -> **$40-80**; 3.2x impression multiplier | [s33] |
| Personal brand ramp | **12-24 months** to compounding inbound | [s110] |
| Website conversion (median) | **2.35%** (top 10%: 11.45%) | [s71] |
| AI-search referral conversion | **3.49%** (+22% vs organic 2.86%) | ChatGPT/Perplexity traffic is pre-qualified [s71] |
| B2B lead-gen landing page | **4.1%** (SaaS free trial 7.2%) | [s142] |

**Revenue formats vs vanity (2026):** Reddit/forum help converts **3-4x** vs search; comparison pages **3.2x** vs feature pages; customer-voiced stories beat polished case studies **3:1**; behavior-triggered email **45%** open vs 18% blasts. Vanity: viral shorts convert **<0.1%** without a direct offer; generic thought-leadership and static infographics ≈ 0 conversion [s201].

---

## Paid Ads (B2B)

| Metric | Google Ads (B2B) | Meta Ads (B2B services) |
|--------|------------------|--------------------------|
| CTR | **1.30%** | **0.78%** |
| CPC | **$6.29** | **$2.52** |
| CVR | **0.31%** | **10.63%** |
| Cost/conversion | **$606** (CPL) | **$73.77** CPA (median) |

Sources [s43, s166, s167]. Recommended B2B SaaS split: **70% Google / 30% Meta** [s59]. Google Search beats PMax for B2B leads (**553% vs 436% ROAS**) [s43]. LinkedIn Ads cost-per-qualified-lead **$47 vs Google $65** (-28%) despite higher CPC [s148].

**Minimum viable test budgets:** Meta `(target CPA x 50) / 7 = min daily/ad set` (e.g. $40 CPA -> ~$300/day); manual test floor $300-600/mo, Advantage+ $1,000/mo. Google Search $500-1,000/mo over 2-4 wks; PMax $1,500/mo over 4-6 wks [s168].

---

## ICP, Attribution & Economics

- **68%** of B2B firms lack a clear ICP; those with one report **68% higher win rates**. Only **5-10%** of your ICP is in-market at any time; **79%** of marketing leads never convert [s112, s183].
- Lead scoring: split **fit** vs **intent**; behavioral intent must **decay 10-20% / 30 days**. Tier A (80+) = sales SLA <1hr (closes 2x); Tier B (60-79) = nurture; Tier C (<60) = automated hold [s44].
- Market validation: 30-50 discovery interviews (70%+ pain consistency); **Sean Ellis test ≥40% "very disappointed"**; landing page 3-5% signup; 10 paid pilots in 30 days [s193, s215].
- Pricing model usage ($150k+ operators): **value-based 62% / retainer 28% / hourly 8%**. Value-based median income $96k vs hourly $58k (**+66%**) [s87, s163].
- AI automation project tiers: Entry **$1.5-10k** + $0.5-1.5k/mo; Core **$10-35k** + $1.5-4k/mo; Premium **$35-100k+** + $4-10k+/mo [s32].
- Three-tier pricing close rate **75%** vs 55% (two options) vs 35% (single) [s27]. AI audit gateway ($2-5k) converts **40-60%** into core builds [s28].
- Dark funnel = **~38% of B2B pipeline** (51% PLG); use self-reported attribution ("How did you hear about us?") blended 70% digital / 30% survey [s162, s48].
- Track: SQL rate, pipeline/channel, CAC, CAC payback, LTV:CAC, CTOR + reply rate (not opens), POAS (not just ROAS). Ignore raw traffic, impressions, opens, follower counts [s206].

---

## How to use this file
- When asked "what's a good [metric]," quote the number **with its bracket** and name the lever to move it.
- Lead advice with the benchmark, then the tactic. ("Cold reply avg is 3.4%; to beat it, cut the list and personalize the first line - aim for 8%+.")
- Full context + every citation lives in `references/research-synthesis.md`. Resolve `[sN]` via `_research/sources.json`.
