# SEO / AEO / GEO / AIO Checklist — the scoreboard (load by default)

The operational pass every blog runs through before it's done. Lead with the move, then why. Citations `[sN]` resolve via `_research/sources.json`; evidence is in `research-synthesis.md`. **[practitioner]** = industry heuristic, not peer-reviewed (see the synthesis honesty flags). Do NOT invent numbers not here.

## The one rule that reconciles everything
Google's official stance and the AI-engine evidence agree: **write helpful, people-first content with clean, extractable structure.** That single move satisfies traditional SEO, Google AI Overviews, and third-party AI engines at once [s34][s1]. Everything below is that rule made concrete. Never write a separate "for AI" version — Google calls that scaled-content-abuse spam [s34].

---

## 1. Intent & keyword (before writing)
- [ ] Pin the **dominant search intent** for the target query (informational / comparison / how-to / transactional). Intent alignment predicts AI citation better than rank [s27][s30]. **[peer-reviewed]**
- [ ] Set **one primary keyword/topic** + 3-6 supporting/semantic terms mapped to intent, not isolated head terms [s5][s16].
- [ ] Brainstorm the **5-10 query fan-out questions** Google's AI will expand into (alternatives, "vs", troubleshooting, "is X worth it", decision criteria). Plan to answer them in-page or across the cluster [s46][s37].

## 2. Structure for extraction (the biggest AEO/GEO lever)
- [ ] **Answer-first:** open the intro and each H2 with a short, self-contained, quotable answer before the elaboration. Explicit modular structure raises AI-citation likelihood over the same content in unstructured prose [s26]. **[peer-reviewed]**
- [ ] Keep each extractable answer **tight (~40-60 words)** — **[practitioner]** window; the principle (short + self-contained) is what's evidence-backed, the exact count is convention [s26].
- [ ] **Headings map to questions:** one H1, H2/H3 phrased the way people ask (matches fan-out queries) [s3][s37][s9].
- [ ] Use the **right block for the intent:** definition block (What is X), numbered steps (How to X), **comparison table** (X vs Y), pros/cons (evaluation), **FAQ** (related questions) [s37][s38]. Tables beat prose for comparisons; numbered lists beat paragraphs for process [s37].
- [ ] One clear idea per paragraph; scannable [s3][s7].

## 3. Authority & citability (GEO)
- [ ] **Cite real sources** with links, and include **specific statistics with dates and attribution.** Direction is safe and matches both the Princeton GEO study and E-E-A-T; exact per-method % are **[practitioner]** (Princeton KDD-2024 via `ai-seo`), so don't quote them as measured fact [s24].
- [ ] Demonstrate **first-hand experience / a real POV** (E-E-A-T) — also the strongest human tell [s1][s8][s73].
- [ ] Named **author + credentials**; visible **"last updated" date**; refresh competitive posts [s0][s4][s12].
- [ ] AI citations aren't limited to page 1 — a well-structured page 2-3 post can still be cited ("SEO floor") [s29]. Structure earns the cite; don't skip it because you're not #1.

## 4. On-page & technical
- [ ] **Title tag:** unique, descriptive, primary keyword near the front, ~50-60 chars **[practitioner]** [s3][s9].
- [ ] **Meta description:** unique, benefit + keyword, ~150-160 chars **[practitioner]** [s3][s9].
- [ ] **URL slug:** short, hyphenated, keyword-bearing [s3][s7].
- [ ] **Internal links:** 2-5 to related cluster/pillar posts with descriptive anchors [s0][s3][s7].
- [ ] **External links:** 1-3 to authoritative sources you cite [s24].
- [ ] **Image alt text:** descriptive, on every image [s3][s7].
- [ ] **Schema:** `Article`/`BlogPosting` (+ `FAQPage` if there's an FAQ). Understood-by-engines baseline; effect on AI citation specifically is still an open question [s3][s19][s76]. Full schema-type table: `ai-seo`.

## 5. AI-surface presence (site-level, note for the client — usually out of a single post's scope)
- [ ] `robots.txt` allows the AI crawlers you want citing you: GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot/anthropic-ai, Google-Extended, Bingbot [s43]. Blocking them = they literally can't cite you.
- [ ] Optional machine-readable files (`llms.txt`, `/pricing.md`, OKF) — see `ai-seo`. Not required by Google; help non-Google engines [s34].

## 6. Format choice (practitioner priors — labeled)
No peer-reviewed evidence that a named format ranks/cites better [s76][s77]; pick the format the **intent** demands. As a tie-breaker prior, `ai-seo`'s industry shares favor **comparison articles (~33%)** and **definitive guides (~15%)**, then original-research, listicle, how-to, opinion — **[practitioner]**, directional only, never quote as fact.

## 7. Measurement (hand to the client)
- [ ] Track Google AI Overviews/AI Mode via **GSC → Search Appearance → "AI Mode"** [s40][s41]; cross-platform citation via Otterly/Peec/ZipTie [s40]. No AI-specific GSC ranking report exists — standard Search metrics still apply [s34].

---

## The deliverable's SEO metadata block (always produced)
Every finished blog ships with:
`SEO title` (≤60) · `Meta description` (≤160) · `URL slug` · `Primary keyword` + `Supporting keywords` · `Answer-block callouts` (the extractable snippets under each H2) · `FAQ` (3-6 Q&A) + `FAQPage` JSON-LD · `Article/BlogPosting` JSON-LD stub · `Image alt texts` · `Internal-link suggestions` · `External sources cited` · `Last updated` date.
