# Email Marketing Playbook 2026 (Strategy + Deliverability)

**Source basis:** Distilled from `references/research-synthesis.md` Q4 (234-source NotebookLM synthesis). Citations map to `_research/sources.json`. This covers strategy, benchmarks, deliverability, and sequence ARCHITECTURE. For the actual email copy (subject lines, body, openers, breakup lines), hand off to the **sales-playbook** skill (clean split). Execution tooling (Apify/Gmail/Sheets pipeline) lives in the **cold-outreach** skill.

---

## What changed in 2026 (read this first)

The inbox is now AI-mediated and strictly regulated. Three shifts to internalize [s39, s88, s92]:
1. **Apple MPP and Gmail Gemini sit between you and the reader.** Open rates are inflated and meaningless (~42-44% reported vs ~27.7% true). Gemini summarizes threads and quietly hides up to **40%** of technically-delivered emails that lack "value density."
2. **Deliverability is a hard baseline, not an edge.** Google/Yahoo/Microsoft enforce auth + complaint + unsubscribe rules for bulk senders.
3. **Generic AI templates are filtered.** Homogeneous "AI speak" gets deprioritized; "just bumping this" follow-ups get exposed by the AI summary.

---

## Benchmarks (set expectations, pace volume)

- Cold reply avg **3.4%**; top 10% hit **8-12%+** [s39, s61].
- True open ~27.7% (ignore opens as a KPI) [s39].
- Cold -> closed deal **~0.215%** (≈1 per 464 sends) - this sets the volume math [s63].
- Meeting-booked: SMB <$1k ACV **1-2.5%**, mid $1k-25k **0.5-1.5%**, enterprise $100k+ **0.3-0.8%** [s62].
- Reply by industry: Legal ~8-10%, Recruiting 5.8-7.2%, Healthcare 4-6%, Agency->SMB 4.2%, Financial 1.5-4%, **SaaS/Software 1-4% (most saturated)** [s62].
- Nurture (permission) avg **39.26% open / 6.21% click** - much better than cold [s143].
- Welcome emails ~80% open; multi-email welcome series = +90% orders [s199].

Full table: `channel-benchmarks.md`.

---

## Deliverability checklist (non-negotiable in 2026)

For anyone sending bulk (>5,000/day, but follow it regardless) [s88, s92, s91]:
- **SPF** under the 10-DNS-lookup limit (else silent PermError).
- **DKIM** 2048-bit minimum, rotate every 6 months.
- **DMARC** must be **`p=quarantine` or `p=reject`** - `p=none` is now treated as no DMARC and triggers rejection (Microsoft).
- **One-click unsubscribe** (RFC 8058 `List-Unsubscribe-Post`), honored within 2 days.
- **Spam complaint rate < 0.1%** (Postmaster/SNDS). 0.3% = hard block.
- **FCrDNS/PTR** on sending IPs; **TLS 1.2+** on all SMTP.

**Warmup + volume** [s56, s80]:
- Warm new domains **3-6 weeks** (up to 8 for brand-new).
- Ramp: 3-5 (or 10-20) emails/day week 1, +5-10/week.
- Cap **30-50 emails/inbox/day**; 50+ on Microsoft 365 trips junk routing.
- 3-5 min gaps between sends; **3-4 inboxes per domain** max.

---

## Sequence architecture (copy -> sales-playbook)

- **Length: 4-7 emails.** Reply distribution: **58% from email 1**, 35% from touches 2-4, 7% from 5-7. Don't over-invest in touch 6+ [s61].
- **Word count:** first touch **<80 words**; body 50-125 words (3-5 sentences) = 2.4x reply vs >200 words [s64].
- **Format:** mostly plain text, **max one link**, no heavy HTML/images (spam triggers) [s67].
- **Cadence:** Email 1 -> wait 2-3 business days -> Email 3 +3-4 days -> Email 4 +5-7 days -> 7-14 days for later touches. Tue-Thu 8-11am local [s67].

**The 5-step skeleton** (AI-automation wedge example) [s67]:
1. **Day 1 - Problem opener:** one specific ops bottleneck + one CTA.
2. **Day 4 - Value add:** a data point/trend/teardown. Never "just checking in."
3. **Day 8 - Social proof:** a quantified peer result (pull from sales-playbook `proof-bank`).
4. **Day 13 - New angle:** different pain or competitive threat.
5. **Day 18-20 - Breakup:** respectful low-pressure close ("Is this not a priority right now?").

Write the actual copy with the **sales-playbook** opener archetypes + the Voss/Hormozi framing it carries. This file decides the *shape*; sales-playbook writes the *words*.

---

## What NO LONGER works (kill list)

- **Spray-and-pray** to 1,000+ unpersonalized = 2.1% reply; purchased lists = 18.5% bounce + permanent domain damage [s41].
- **Open rate as a KPI** (MPP inflates it). Track CTOR, reply rate, meetings [s39].
- **Generic AI templates** - Gemini filters homogeneous copy; up to 40% quietly hidden [s88].
- **"Just bumping this"** follow-ups - the AI thread summary exposes them as spam [s95].
- **DMARC `p=none`**, multiple links, heavy HTML [s92].

Full cross-channel kill list: `what-not-to-do.md`.
