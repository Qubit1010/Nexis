# Claude Cowork - The Agentic Desktop Product (2026)

**Source basis:** `research-synthesis.md` Q4 (237-source NotebookLM synthesis). `[sN]` -> `_research/sources.json`. **Honesty rule:** Cowork is new and evolving fast - confirm dates/limits via the live notebook before quoting to a client.

**What it is:** An **autonomous desktop agent for non-technical knowledge workers**. Same agentic engine as Claude Code, but a graphical desktop interface instead of a terminal. You give it a goal and step away while it works [s64, s195].

**Timeline:** research preview **Jan 12, 2026**; **GA across all paid plans (Pro/Max/Team/Enterprise) on April 9, 2026**. Built internally by Boris Cherny in ~10 days using Claude Code [s50, s64, s195].

---

## How it works

- **Plan-to-action loop:** analyzes the workspace, drafts a structured plan, splits into subtasks, executes - can coordinate parallel sub-agents [s194, s195].
- **Sandboxed local VM:** once you grant access to specific folders, it runs shell/code inside a secure local Linux VM (Apple `VZVirtualMachine` on macOS), reading/creating/editing files on your filesystem [s145, s194].
- **Computer use:** can simulate screen interactions to open files, navigate SaaS dashboards, click buttons, fill forms on your host screen [s194].
- **Safety modes:** **"Ask before acting"** (pauses for approval) vs **"Act without asking"** (continuous). Either way, an un-bypassable desktop prompt gates permanent file deletion [s145, s194].

---

## Best uses + tactics

- **File/data automation:** sort a messy Downloads folder into categories, batch rename (`YYYY-MM-DD_filename`), detect dataset outliers, turn a folder of receipt images into a formatted expense report [s145, s194].
- **Polished deliverables:** build real-formula Excel models; compile competitor research into a PowerPoint that respects brand fonts/masters/colors (not raw CSV/text) [s145, s194].
- **Scheduled work:** `/schedule` a recurring task once (e.g. weekly report, Monday competitor-pricing check) and it runs hands-free [s145, s194].
- **Mobile Dispatch (Mar 2026):** text a command from the Claude app; your phone wakes the desktop, runs the task locally, and pushes you the result [s113, s187].
- **Small Business (May 2026):** native connectors to QuickBooks, PayPal, Canva, HubSpot - reconcile ledgers, draft promos, generate Canva assets, prep a month-end close packet [s161].

---

## Limits + risks (say these plainly)

- **Desktop dependency:** your computer must stay awake, online, with the app open - sleep pauses active + scheduled tasks [s145, s146].
- **Token burn:** agentic multi-step work drains usage limits much faster than chatting [s145].
- **Audit gap:** Cowork activity streams via OpenTelemetry but is **not yet in the Claude Compliance API** - a blocker for strictly regulated enterprises; no cross-session memory unless inside a Project [s145, s199].
- **Prompt injection:** "Act without asking" + web access (or the Claude in Chrome extension) risks a malicious page/document hijacking the agent before you can intervene [s195, s199].

---

## Cowork vs Code vs Chat (the clean distinction)

- **Chat** = think/draft, human in the loop every turn, no filesystem/terminal access [s111].
- **Claude Code** = for developers, terminal/IDE, outputs committed software (tests, branches, PRs) [s111, s194].
- **Cowork** = for non-technical operators, GUI, outputs business deliverables (spreadsheets, decks, cleaned directories) without ever touching a terminal [s111, s194].

When a client asks "can my ops team run this themselves without a developer?" and it's desktop knowledge-work, Cowork is usually the answer. When it must run unattended/server-side or embed in their product, it's the API instead (see `surface-comparison.md`).
