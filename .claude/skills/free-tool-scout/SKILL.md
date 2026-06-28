---
name: free-tool-scout
description: >
  Discovers, catalogs, and searches for free tools, APIs, and software across 7 business
  categories: Marketing, Business Operations, Market Research, Productivity, Content Creation
  & Editing, AI Tools, and Finance Management. Pre-built catalog for instant answers; live
  Exa AI search for specific or niche queries; refreshable catalog on demand.

  Always trigger this skill when the user asks about free tools for any business task —
  even if they don't explicitly say "tool scout". Trigger on: "find free tools for X",
  "what tools should I use for Y", "alternatives to [paid tool]", "any free [category] tools",
  "best free [marketing/CRM/AI/productivity] tools", "search for [tool name]",
  "what free tools exist for [task]", "refresh the catalog", "run the tool scout",
  "tool scout [query]", "free email marketing", "free CRM", "free invoicing",
  "free AI tools", "find me a tool that does X for free", "good free tools for startups".
  If the user describes a workflow and a free tool exists for it — surface it proactively.
argument-hint: "[category | tool query | 'refresh']"
---

# Free Tool Scout

Finds and surfaces free tools, APIs, and software for business use across 7 categories.
The catalog is pre-built (fast, no API cost) and live-searchable via Exa AI on demand.

## Categories

| Category | Covers |
|----------|--------|
| **Marketing** | Email tools, social scheduling, SEO, analytics, ads |
| **Business Operations** | CRM, project management, invoicing, HR |
| **Market Research** | Surveys, competitive intel, audience research |
| **Productivity** | Note-taking, time tracking, calendar, automation |
| **Content Creation** | Writing, video, image editing, design |
| **AI Tools** | Assistants, code gen, image gen, workflow AI |
| **Finance Management** | Budgeting, expense tracking, accounting, invoicing |

---

## Mode Detection

Pick the mode from the user's message:

| Signal | Mode |
|--------|------|
| "find free tools for X", "what tools for Y", "alternatives to Z", "any free [category] tools" | **Catalog** (fast) |
| "search for [tool]", "look up [tool]", "find [specific tool]", "any new tools for X" | **Live Search** (Exa) |
| "refresh", "update the catalog", "rebuild catalog", "run the fetch" | **Refresh** |

When unsure: check the catalog first. If it has 2+ relevant entries, answer from it. If the query is very specific (a tool name, a niche task), go Live Search.

---

## Catalog Mode

Read `catalog/tools.md` (path: `.claude/skills/free-tool-scout/catalog/tools.md` from repo root). Filter entries matching the user's category or task.

**Output format:**
```
**[Tool Name]** — [Category]
- URL: [url]
- About: [description]
- Free tier: [what's free — be specific, not "free tier available"]
```

Show up to 8 relevant tools. If fewer than 3 match the query, supplement with a Live Search automatically — tell the user "searching Exa for more options...".

If `catalog/tools.md` is missing or empty, tell the user:
> "Catalog not built yet. Say 'refresh the tool catalog' to run the initial Exa research — takes about 2 minutes."

---

## Live Search Mode

Run from the repo root:
```
python .claude/skills/free-tool-scout/scripts/search_tool.py --query "[user's query]"
```

With optional category context:
```
python .claude/skills/free-tool-scout/scripts/search_tool.py --query "[query]" --category "[category]"
```

Parse the script output and present results inline. After showing results, offer: "Want me to add any of these to the catalog?"

---

## Refresh Mode

Warn the user this takes 2-3 minutes (runs 14 Exa searches across 7 categories).

Run from the repo root:
```
python .claude/skills/free-tool-scout/scripts/fetch_tools.py
```

When done, confirm: "Catalog updated — [N] tools across 7 categories. Say 'find free tools for X' to browse."

---

## Output Style

Keep it scannable — no paragraphs. Tool entries like:

**Mailchimp** — Marketing
- URL: https://mailchimp.com
- About: Email marketing platform with drag-and-drop editor
- Free tier: Up to 500 contacts and 1,000 sends/month

Group by category when showing 5+ tools. For 10+ results, ask which categories matter most before dumping everything.
