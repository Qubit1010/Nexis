# Intermediate - Section 14: Connecting Claude to Your Tools

*Claude plugged into your actual work stack.*

**Bottom line:** Claude becomes dramatically more useful when it can read from and write to the tools you already work in, Gmail, Calendar, Drive, Slack, Notion, and more. This section covers the three ways to connect: built-in integrations, Claude in Chrome, and the Model Context Protocol (MCP).

---

## Built-in connectors

Claude's paid plans include native integrations with some of the most common tools. These let Claude pull context from your actual work and push output back into the right place.

| Connector | What Claude can do |
|-----------|-------------------|
| Gmail | Read, draft, and send emails. Triage your inbox. Draft replies in your voice. |
| Google Calendar | See your schedule. Draft meeting agendas. Find free time slots. |
| Google Drive / Docs | Read documents and sheets. Update Docs. Save outputs directly. |
| Slack | Read channel history. Draft messages. Post updates. |
| Notion | Read databases and pages. Write summaries back. |

These connect through the Integrations panel in your Claude settings. Once connected, Claude can pull from these sources automatically when you ask for context.

## Claude in Chrome

The Chrome extension lets you bring Claude into any tab you are browsing, with the page content already loaded. Useful for:
- Summarizing an article you are reading without copying it
- Drafting a reply to an email in Gmail without switching windows
- Analyzing a report in Google Sheets without leaving it
- Getting quick answers about a page's content while staying in it

## MCP: the deeper connection

The Model Context Protocol (MCP) is the standard that lets Claude connect to virtually any tool, including ones Anthropic did not build. If the built-in connectors do not include a tool you use, there is likely an MCP server for it. Think of MCP like USB-C for AI tools: a common plug that any compatible tool can use.

MCP servers are available for dozens of professional tools. A few examples: GitHub, Jira, Asana, Salesforce, HubSpot, databases, custom internal APIs. If your team has a developer, they can build a custom MCP server for any internal tool in a few hours.

## What a connected week looks like

An example of how connectors change a working day:

- **Morning:** "Summarize the 10 most important emails from the last 24 hours and tell me what needs a response today." (Gmail connector)
- **Before a meeting:** "Read my calendar and draft a 3-point agenda for my 2pm client check-in based on the notes in the shared Drive doc." (Calendar + Drive)
- **Afternoon:** "Take the feedback from this morning's Slack thread and turn it into a structured brief I can use to brief the design team." (Slack)
- **End of day:** "Save today's decisions and action items to the project Notion page." (Notion)

None of this requires any manual copying, switching tools, or re-describing what you already told another app.

> **Start with one connector.** Pick the tool you use most, Gmail, Drive, or Slack, and connect it first. One integration that saves 20 minutes a day is worth more than five integrations set up and never used.

## Key takeaways

- Built-in connectors (Gmail, Calendar, Drive, Slack, Notion) let Claude work inside your actual tools, reading and writing directly.
- The Chrome extension brings Claude into any browser tab with the page loaded automatically.
- MCP extends connections to nearly any tool through a common standard. If the built-in list does not have it, look for an MCP server.
- Start with one connector and get value from it before adding more.
