# Nexis GrowthOS (pointer)

Client-facing SaaS product — lives in its own private repo (spec D8, first use of this convention):

**Repo:** https://github.com/Qubit1010/nexis-growthos
**Local:** `C:\Users\qubit\OneDrive\Documents\Automations\nexis-growthos`
**Spec:** `references/business-brain-v1-spec.md` (this repo)
**Plan:** approved 2026-07-07 — full v1 spec stack (Neon + Drizzle, Better Auth, Inngest, Resend, Vercel; Claude-first with gpt-5.2 fallback)

What it is: the Nexis second-brain pattern productized for non-technical SMB owners. A conversational Business Brain (append-only `brain_records` with supersede chains) plus a weekly marketing loop that turns brain context into ready-to-post content, delivered as an email digest. Concierge-first: dogfood on NexusPoint, then one real client.

Prompts under `src/prompts/` in that repo are distilled (business-agnostic) from Nexis skills: content-engine (scoring rubric, platform formats, voice principles), sales-playbook (AI-smell filter), marketing-advisor (channel benchmarks + strategy).
