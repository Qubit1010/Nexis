# Advanced - Section 26: Integration Power-Ups: Claude + Your Stack

*What happens when you combine Claude Code with the right external tools.*

**Bottom line:** Each integration listed in Section 25 is useful on its own. The real leverage comes when you combine them: Claude Code plus Firecrawl for scraping pipelines, plus NotebookLM for knowledge bases, plus Playwright for browser automation, plus Graphify and Obsidian for a second brain. The pattern is always Claude as the intelligent layer on top of purpose-built tools.

---

## Combo 1: Claude Code + Firecrawl = scraping at scale

**What it unlocks:** Claude Code can crawl a website, extract structured data, and process the results automatically, without writing brittle scraper code.

**How it works:** Claude Code calls the Firecrawl CLI, which handles the actual web crawling and returns clean, structured output. Claude Code then processes that output: filtering, categorizing, writing to a spreadsheet, generating summaries.

**Real use case:** Point it at 50 competitor websites. Ask it to extract the services page, pricing page, and about page from each. Get a structured comparison table with no manual browsing.

---

## Combo 2: Claude Code + NotebookLM = near-infinite memory

**What it unlocks:** Claude Code's context window has limits. NotebookLM can hold a much larger body of knowledge and answer questions from it with citations. Claude Code + NotebookLM means Claude Code can query a vast knowledge base, get a cited answer, and use that in its current task without loading everything into context.

**How it works:** Claude Code calls the NotebookLM CLI to query a notebook. The answer comes back with citations. Claude Code uses that answer in the current task.

**Real use case:** Build a research-backed report. Claude Code queries the NotebookLM notebook for relevant findings, gets cited answers, and synthesizes them into a structured document without the full research archive in context.

---

## Combo 3: Claude Code + Playwright = browser automation

**What it unlocks:** Claude Code can control a real web browser, navigating pages, filling forms, clicking buttons, extracting content, and taking screenshots, then making decisions based on what it sees.

**How it works:** Claude Code calls Playwright through the CLI. Playwright launches a browser (headless or visible), performs the actions Claude Code instructs, and returns the results.

**Real use case:** Build an automated competitive intelligence loop. Every Monday, Claude Code browses 10 competitor sites via Playwright, captures any pricing or feature changes, and emails you a diff report.

---

## Combo 4: Graphify + Obsidian = second brain

**What it unlocks:** Turn Claude Code's outputs (diagrams, notes, research summaries, decision logs) into a permanent, visual, linked knowledge base in Obsidian.

**How it works:** Claude Code uses Graphify to generate visual diagrams from code structures or complex ideas. Those outputs, plus notes and summaries from Claude Code sessions, get saved to an Obsidian vault. Over time, the vault becomes a linked graph of everything the system has built and learned.

**Real use case:** Every Claude Code session that produces a significant decision or design gets saved to the Obsidian vault with Graphify diagrams for the architecture decisions. The vault becomes an always-current technical knowledge base for the project.

---

## The pattern behind the combos

Claude is the intelligence layer. External tools (Firecrawl, Playwright, NotebookLM, Obsidian) are the specialists. Claude Code decides when to call which tool, interprets the results, and synthesizes them into the output you need.

The pattern is: **Claude reasons and decides, external tools execute the specialized work, Claude synthesizes the results.**

This pattern scales to any tool with a CLI or an MCP server. The question is always: "what specialized tool handles this step better than Claude alone, and can Claude call it?"

## Key takeaways

- Four high-value combos: Firecrawl for scraping pipelines, NotebookLM for large knowledge bases, Playwright for browser automation, Graphify + Obsidian for a second brain.
- The pattern is always Claude as the intelligent layer calling specialized tools for the specialized work.
- Any tool with a CLI or MCP server can participate in this pattern.
- The real leverage comes from combinations, not individual tools.
