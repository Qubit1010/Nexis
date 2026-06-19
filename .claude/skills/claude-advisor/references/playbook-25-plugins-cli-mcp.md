# Advanced - Section 25: Plugins, CLIs, and MCP Servers

*The ecosystem that extends Claude far beyond its defaults.*

**Bottom line:** Claude Code's capabilities extend through three types of additions: Plugins (from the Anthropic marketplace), CLIs (command-line tools Claude Code can call), and MCP Servers (connections to external systems). This is how Claude Code accesses GitHub, browses real websites, controls a browser, or connects to your internal tools.

---

## Three extension types

| Type | What it is | How it works |
|------|-----------|-------------|
| Plugin | A packaged extension from the Claude Code or Claude.ai marketplace | Install once, Claude uses it when relevant |
| CLI | A command-line tool Claude Code can call like any terminal command | Install the tool, Claude calls it as needed |
| MCP Server | A server that exposes a tool or data source via the Model Context Protocol | Run the server, Claude connects and uses it |

## Plugins worth knowing

| Plugin | What it adds |
|--------|-------------|
| Superpowers | Expanded capabilities pack for common tasks |
| Code-Simplifier | Automatically suggests ways to reduce code complexity |
| Security Guidance | Flags security issues in code as it is written |
| Graphify | Creates visual diagrams from code or data descriptions |
| Codex | Access to a library of code patterns and templates |

Plugins are installed through the Claude Code settings or the Claude.ai extension panel. They load when relevant to the current task.

## CLIs that pair well with Claude Code

| CLI | What it enables |
|-----|----------------|
| GitHub CLI (`gh`) | Read and write GitHub repos, PRs, issues, and actions directly from Claude Code |
| Playwright CLI | Browser automation: Claude Code can navigate, fill forms, scrape, and test web pages |
| Firecrawl CLI | Advanced web scraping and crawling with structured output |
| Google Workspace CLI (`gws`) | Read and write Gmail, Drive, Docs, Sheets, and Calendar from Claude Code |
| NotebookLM CLI | Programmatic access to Google NotebookLM for research and knowledge management |

These are installed via npm or pip as you would any command-line tool, and Claude Code calls them as terminal commands when you ask it to work with those systems.

## MCP Servers: the deep connectors

MCP (Model Context Protocol) servers expose tools and data through a standard interface Claude Code can use natively. Notable examples:

- **Context7:** Provides up-to-date library documentation so Claude Code does not rely on outdated training data when writing code
- **Composio:** A hub connecting to hundreds of SaaS apps (Salesforce, HubSpot, Jira, Asana, and more) through a single MCP server

Installing an MCP server adds it to Claude Code's available tools. You can run multiple MCP servers simultaneously; Claude Code selects the right one based on the task.

## Where to find them

- **Official Claude Code extensions:** Listed in Claude Code documentation and the Desktop app's extension settings
- **MCP server registry:** The Anthropic GitHub organization and community repositories list available servers
- **npm and pip packages:** Many CLIs are packaged as standard tools with Claude Code integration

## The golden rule: discover widely, install sparingly

Every extension you install adds to the context Claude Code loads at startup. Too many extensions slow things down and can cause conflicts. The practical approach:

1. Know what is available in the ecosystem (the survey above covers the most useful)
2. Install only what you use regularly
3. Add a new extension when you have a specific task it solves, not speculatively

## Key takeaways

- Three extension types: Plugins (packaged marketplace tools), CLIs (terminal tools Claude Code calls), MCP Servers (protocol-based connectors to external systems).
- The most useful CLIs: GitHub, Playwright, Firecrawl, Google Workspace, NotebookLM.
- MCP extends Claude Code to hundreds of SaaS tools via Context7, Composio, and custom servers.
- Discover widely, install sparingly. Each extension adds startup overhead; keep only what you use.
