---
description: Connected tools and how to use them
globs:
---

# Tool Integrations

## Google Workspace CLI (gws)
- Authenticated as hassanaleem86@gmail.com
- Available: Gmail, Drive, Docs, Sheets, Calendar, Presentations, Tasks
- Use `gws gmail +triage` for email summaries
- Use `gws gmail +send` to send emails
- Use `gws drive files list` to search Drive
- Use `gws docs documents get --params '{"documentId": "ID"}'` to read docs

## MCP Servers
- Google Calendar / Gmail -- scheduling and email
- Google Drive -- file search and access
- GitHub -- repos and version control
- Firecrawl -- web scraping and crawling
- Stitch -- design
- NotebookLM -- research and knowledge management
- Canva -- design generation, brand templates, exports
- Upwork -- job posts, freelancer search, profile

## Skills, Plugins & Collections
- Skills live in `.claude/skills/` (one folder + `SKILL.md` each). In-house skills are catalogued in `CLAUDE.md`.
- Installed third-party skills + plugins (scientific-agent-skills, awesome-claude-skills, senior-* / code-reviewer / etc., and the global plugins) are also catalogued in `CLAUDE.md` under "Installed Skills, Collections & Plugins" -- prefer them over building from scratch when a task matches.
- Install more skills with `npx skills add <owner>/<repo> --agent claude-code`; install plugins with `claude plugin marketplace add <repo>` then `claude plugin install <name@marketplace>`.

## Development
- GitHub for version control
- VS Code as primary editor
- Claude Code as core execution engine
