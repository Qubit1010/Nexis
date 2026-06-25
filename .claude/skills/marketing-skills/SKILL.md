---
name: marketing-skills
description: >
  Router for 45 marketing skills from coreyhaines31/marketingskills. Use when the user
  wants help with any marketing task: SEO, paid ads, cold email, copywriting, content
  strategy, conversion optimization, pricing, offers, landing pages, lead magnets, social
  media, product launches, referral programs, retention, churn, onboarding, competitor
  research, sales enablement, community, PR, analytics, or marketing planning.
  Also trigger on: "marketing help", "how do I get more [traffic/leads/clients]",
  "write [copy/email/ad]", "improve my [funnel/landing page/conversion rate]",
  "should I run ads", "what marketing should I do", "help me launch [X]",
  "marketing ideas for [X]".
  Do NOT use for NexusPoint-specific outreach or content (use marketing-advisor,
  content-engine, sales-playbook, or leads-to-crm instead).
---

# Marketing Skills Router

45 marketing skills covering every channel and tactic. When a request matches:

1. Identify the best skill (or chain) from the catalog below
2. Read its SKILL.md: `.claude/skills/marketing-skills/<name>/SKILL.md`
3. Follow those instructions exactly
4. If multiple skills apply, tell the user the recommended chain and start with the first

---

## How to pick

| When you need to... | Skill |
|---------------------|-------|
| Get more organic traffic | `seo-audit`, `programmatic-seo`, `site-architecture`, `ai-seo` |
| Convert visitors into leads | `cro`, `popups`, `signup`, `lead-magnets`, `free-tools`, `offers` |
| Nurture and close | `emails`, `cold-email`, `sms`, `onboarding`, `sales-enablement` |
| Write copy or content | `copywriting`, `copy-editing`, `content-strategy`, `video`, `image` |
| Run paid ads | `ads`, `ad-creative`, `analytics`, `ab-testing` |
| Launch something | `launch`, `co-marketing`, `public-relations`, `referrals`, `community-marketing` |
| Set pricing or offers | `pricing`, `offers`, `product-marketing`, `marketing-psychology` |
| Build a pipeline | `cold-email`, `competitor-profiling`, `prospecting`, `revops`, `customer-research` |
| Retain and grow | `churn-prevention`, `paywalls`, `onboarding`, `emails`, `referrals` |
| Social media | `social`, `aso`, `video`, `image` |
| Strategy and planning | `marketing-plan`, `marketing-ideas`, `content-strategy`, `customer-research` |
| SEO and discovery | `seo-audit`, `ai-seo`, `programmatic-seo`, `schema`, `directory-submissions`, `competitors` |

---

## Full catalog

### Traffic & Discovery
| Skill | What it does |
|-------|-------------|
| `seo-audit` | Technical + on-page SEO audit with fixes |
| `ai-seo` | Optimize for LLM/AI search (ChatGPT, Perplexity, Gemini) |
| `programmatic-seo` | Landing pages at scale, templates, SEO automation |
| `site-architecture` | URL structure, navigation, internal linking |
| `schema` | JSON-LD structured data for rich results |
| `directory-submissions` | Business directory and citation submissions |
| `competitors` | Competitor SEO, keywords, and ranking gap analysis |

### Conversion & Lead Gen
| Skill | What it does |
|-------|-------------|
| `cro` | Conversion rate optimization — tests, funnels, heatmaps |
| `popups` | Popup and overlay strategies (exit intent, timed, scroll) |
| `signup` | Optimize signup flows, reduce registration friction |
| `lead-magnets` | eBooks, checklists, templates as lead capture |
| `free-tools` | Build free interactive tools for lead gen |
| `offers` | Craft and position offers (Hormozi-aligned) |
| `ab-testing` | Plan and analyze A/B tests across any channel |

### Outreach & Sales
| Skill | What it does |
|-------|-------------|
| `cold-email` | Cold email sequences, subject lines, follow-ups |
| `emails` | Email marketing — nurture sequences, newsletters, automations |
| `sms` | SMS marketing — opt-ins, promos, reminders |
| `prospecting` | Find and qualify leads, build target lists |
| `sales-enablement` | Sales collateral, battle cards, pitch decks |
| `competitor-profiling` | Deep competitor analysis — positioning, gaps, weaknesses |

### Content & Creative
| Skill | What it does |
|-------|-------------|
| `copywriting` | Marketing copy — landing pages, ads, emails, social |
| `copy-editing` | Edit and polish existing copy |
| `content-strategy` | Content calendar, topic clusters, content funnel |
| `video` | Video marketing strategy across platforms |
| `image` | Visual content strategy — graphics, brand visuals |

### Paid Ads
| Skill | What it does |
|-------|-------------|
| `ads` | Campaign strategy — Google, Meta, LinkedIn, Twitter |
| `ad-creative` | Ad copy variations at scale (headlines, descriptions, body) |
| `analytics` | GA4, conversion tracking, UTM params, attribution |

### Launch & Growth
| Skill | What it does |
|-------|-------------|
| `launch` | Product launch — pre-launch, launch day, post-launch |
| `co-marketing` | Joint marketing partnerships |
| `public-relations` | Press releases, media outreach, brand mentions |
| `referrals` | Referral and affiliate programs |
| `community-marketing` | Build and nurture a brand community |
| `social` | Social media strategy — platform selection, content mix |

### Retention & Monetization
| Skill | What it does |
|-------|-------------|
| `churn-prevention` | Cancel flows, save offers, dunning, win-backs |
| `paywalls` | In-app and website paywalls and upgrade gates |
| `onboarding` | First-run experience, activation, time-to-value |
| `pricing` | Pricing strategy — tiers, anchoring, psychology |
| `product-marketing` | GTM messaging, positioning, features-to-benefits |

### Strategy & Research
| Skill | What it does |
|-------|-------------|
| `marketing-plan` | Full marketing plan — channels, budget, milestones |
| `marketing-ideas` | Brainstorm tactics, channels, campaigns |
| `marketing-psychology` | Scarcity, social proof, reciprocity, persuasion |
| `customer-research` | Surveys, interviews, persona building |
| `revops` | CRM hygiene, pipeline tracking, revenue ops |
| `aso` | App Store Optimization — keywords, screenshots, ratings |

---

## Common chains

| Goal | Chain |
|------|-------|
| Win a new client | `competitor-profiling` → `cold-email` → `sales-enablement` |
| Launch a product | `offers` → `pricing` → `copywriting` → `launch` → `co-marketing` + `public-relations` |
| Fix a leaky funnel | `analytics` → `cro` + `signup` → `onboarding` → `churn-prevention` |
| Grow organic traffic | `seo-audit` → `site-architecture` → `content-strategy` → `programmatic-seo` |
| Build a content engine | `customer-research` → `marketing-psychology` → `content-strategy` → `copywriting` → `social` |
| Run paid media | `ad-creative` → `ads` → `analytics` → `ab-testing` |
| Monetize existing users | `pricing` → `paywalls` → `offers` → `emails` → `referrals` |
