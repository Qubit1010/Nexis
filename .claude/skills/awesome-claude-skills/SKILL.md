---
name: awesome-claude-skills
description: >
  Router for 26 practical productivity and development skills from ComposioHQ/awesome-claude-skills.
  Use when the user wants to: create HTML artifacts or UI components, apply brand styling, design visuals
  (canvas-design), generate changelogs from git, extract competitor ads, connect Claude to external apps
  (Gmail, Slack, GitHub, Notion via Composio), write or research content, analyze developer growth,
  brainstorm domain names, organize files or invoices, enhance images, write internal comms, debug
  LangChain/LangSmith traces, research leads, build MCP servers, analyze meeting transcripts,
  pick raffle winners, share skills on Slack, create Slack GIFs, generate tailored resumes, apply
  themes to artifacts, optimize tweets/X posts, download YouTube videos, or test web apps with Playwright.
---

# Awesome Claude Skills Router

26 practical productivity and development skills from ComposioHQ. When a user request matches one:

1. Identify the best skill from the catalog below
2. Read its SKILL.md: `.claude/skills/awesome-claude-skills/<name>/SKILL.md`
3. Follow those instructions exactly

---

## Skill Catalog

### Development & Code
- **artifacts-builder** — Create elaborate multi-component HTML artifacts using React, Tailwind, modern frontend tech
- **changelog-generator** — Auto-generate user-facing changelogs from git commit history, categorized and formatted
- **developer-growth-analysis** — Analyze Claude Code chat history to identify coding patterns and development gaps
- **langsmith-fetch** — Debug LangChain/LangGraph agents by fetching execution traces from LangSmith Studio
- **mcp-builder** — Guide for creating high-quality MCP servers that enable LLMs to interact with external services
- **webapp-testing** — Test local web apps with Playwright: verify frontend functionality, debug UI

### Design & Visual
- **canvas-design** — Create visual art in PNG and PDF using design philosophy and AI image tools
- **image-enhancer** — Improve image quality, resolution, sharpness — especially for screenshots
- **theme-factory** — Apply professional font/color themes to slides, docs, reports, HTML landing pages
- **brand-guidelines** — Apply Anthropic's official brand colors and typography to artifacts for brand consistency

### Content & Writing
- **content-research-writer** — Research and write high-quality content with citations, improved hooks, iterated outlines
- **internal-comms** — Write internal communications: 3P updates, newsletters, FAQs, status reports
- **meeting-insights-analyzer** — Analyze meeting transcripts/recordings for behavioral patterns and actionable feedback

### Business & Marketing
- **competitive-ads-extractor** — Extract and analyze competitors' ads from Facebook/LinkedIn ad libraries
- **lead-research-assistant** — Identify and qualify high-quality leads by analyzing your business and target companies
- **domain-name-brainstormer** — Generate domain name ideas and check availability across .com, .io, .dev, .ai
- **twitter-algorithm-optimizer** — Optimize tweets for maximum reach using Twitter's open-source algorithm insights

### Integrations & Automation (requires Composio API key)
- **connect** — Connect Claude to any app: Gmail, Slack, GitHub, Notion — take real actions, not just text
- **connect-apps** — Composio integration router for 500+ apps: email, calendar, CRM, dev tools, storage

### Productivity & Organization
- **file-organizer** — Intelligently organize files and folders: understand context, find duplicates, suggest structure
- **invoice-organizer** — Organize invoices/receipts for tax prep: extract info, rename files, export summaries
- **tailored-resume-generator** — Generate tailored resumes from job descriptions matching relevant experience
- **raffle-winner-picker** — Pick random winners from lists, spreadsheets, or Google Sheets for giveaways
- **skill-share** — Create new Claude skills and share them automatically on Slack via Rube

### Media
- **slack-gif-creator** — Create animated GIFs optimized for Slack with size constraints and animation primitives
- **youtube-downloader** — Download YouTube videos with customizable quality and format options

---

## Notes on Composio Skills

The `connect` and `connect-apps` skills require:
1. A free [Composio](https://composio.dev) API key
2. OAuth authorization for each connected service (Gmail, Slack, GitHub, etc.)

Once set up, Claude can actually send emails, create GitHub issues, post Slack messages — not just draft them.

---

## How to Route

Read `.claude/skills/awesome-claude-skills/<skill-name>/SKILL.md` for the matched skill and follow its instructions.
