# Agentic coding & AI-assisted engineering

_25 curated sources via Exa_

## 1. Context Engineering for AI Coding Agents: 9 Fixes (2026) — funDesk
<https://www.fundesk.io/context-engineering-techniques-ai-coding-agents-2026>
*2026-04-23*

> This is not a model problem. It is a context problem. And in 2026, fixing it has its own name: context engineering. Anthropic's Applied AI team formalized the term in September 2025, calling it "the set of strategies for curating and maintaining the optimal set of tokens during LLM inference." The shift matters because agents — unlike chat — cannot be re-prompted at every step of a 15-step refactor. They need a persistent, carefully curated information environment. ... - Context engineering = cu

## 2. Effective context engineering for AI agents \ Anthropic
<https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
*2025-09-29*

> We recommend organizing prompts into distinct sections (like`<background_information>`,` `,`## Tool guidance`,`## Output description`, etc) and using techniques like XML tagging or Markdown headers to delineate these sections, although the exact formatting of prompts is likely becoming less important as models become more capable. ... Tools allow agents to operate with their environment and pull in new, additional context as they work. Because tools define the contract between agents and their i

## 3. Context Engineering for AI Coding Agents: The Complete Guide (2026) — amux
<https://amux.io/guides/context-engineering/>
*2026-04-09*

> The complete guide to structuring what your AI agents see — CLAUDE.md, hooks, skills, subagents, memory, and specs — so they produce reliable output, especially when you run many of them in parallel. ... Context engineering is the practice of curating everything an AI coding agent sees — system prompts, project rules, reference docs, tool outputs, conversation history, memory — so that it produces reliable, correct output. ... This is not prompt engineering. Prompt engineering optimizes a single

## 4. Claude Code Context Engineering: 6 Pillars Framework
<https://claudefa.st/blog/guide/mechanics/context-engineering>
*2026-07-03*

> # Context Engineering: The Six Pillars That Make Claude Code Reliable ... Master context engineering in Claude Code. The six pillars framework transforms inconsistent AI into a reliable, predictable coding partner. ... Problem: Claude Code gives you inconsistent results. Sometimes brilliant, sometimes frustrating. You can't predict when it will nail your request or miss the mark entirely. ... Quick Win: Stop stuffing everything into your prompt. Load context strategically: ... The difference: pr

## 5. Context Engineering for Claude Code: Why Prompt Structure Beats Prompt Wording | Code With Seb
<https://www.codewithseb.com/blog/context-engineering-claude-code-guide>
*2026-04-20 | Sebastian Sleczka*

> In 2026, model quality improved enough that how you structure context matters more than how you phrase prompts. Here's the context engineering playbook: CLAUDE.md architecture, skill decomposition, MCP as context providers, and the patterns that consistently produce better output. ... Context engineering is the practice of structuring everything Claude receives — before, during, and after a task — so that the model has exactly the information it needs, no more, no less, at the moment it needs it

## 6. Context Engineering Best Practices for AI-Powered Dev Teams (2026)
<https://packmind.com/context-engineering-ai-coding/context-engineering-best-practices/>
*2026-04-03*

> 026) ... Context engineering — the discipline of structuring, maintaining, and governing the information that shapes how AI coding assistants behave — has become the foundational skill that separates teams seeing sustained ROI from those still stuck managing AI rework. This guide compiles 30+ actionable best practices across the full spectrum : from writing your first effective context file to building the ContextOps infrastructure that makes AI-assisted development governable at scale. Each cha

## 7. Context Engineering for Claude Code (2026) | Claude Code Guides
<https://claudecodeguides.com/context-engineering-claude-code-complete-guide-2026/>
*2026-04-22 | Michael Lip*

> Context engineering is the discipline of controlling exactly what information an AI agent sees, when it sees it, and how much of it enters the context window. In Claude Code, poor context engineering is the single largest source of token waste. A session with unmanaged context easily consumes 200K tokens, while the same task with proper context engineering completes in 60K-80K tokens – a 60-70% reduction that saves $6-$15 per session at Opus 4.6 rates ($15/$75 per MTok input/output). ... 1. Audi

## 8. Set up a context engineering flow in VS Code
<https://code.visualstudio.com/docs/agents/guides/context-engineering-guide>
*2025-09-29*

> This guide shows you how to set up a context engineering workflow in VS Code using custom instructions, custom agents, and prompt files. ... Context engineering is a systematic approach to providing AI agents with targeted project information to improve the quality and accuracy of generated code. By curating essential project context through custom instructions, implementation plans, and coding guidelines, you enable AI to make better decisions, improve accuracy, and maintain persistent knowledg

## 9. Spec-Driven Development with AI Coding Agents: The Complete Guide (2026) — amux
<https://amux.io/guides/spec-driven-development/>
*2026-04-10*

> Write the spec first. Let agents implement in parallel. Review against acceptance criteria, not vibes. The workflow that makes AI coding predictable. ... Spec-driven development (SDD) is a workflow where you write a structured specification before any code is written — by you or by an AI agent. The spec defines the goal, requirements, constraints, and acceptance criteria. The agent implements against the spec. You review against the spec. No vibes, no guessing, no prompt-and-pray. ... | Dimensio

## 10. The Complete Guide to Spec Driven Development (SDD) | Planu — SDD for AI Agents
<https://planu.dev/en/blog/spec-driven-development-guide>
*2026-03-03 | Planu*

> Spec Driven Development (SDD) is a methodology that addresses this. It provides the missing layer of structure that makes AI-assisted development reliable at scale. ... SDD is a software development methodology where structured specifications are created and maintained as first-class artifacts — before coding begins, not as an afterthought. ... - Defines what "done" looks like in terms of specific, testable acceptance criteria - Captures key constraints and architectural decisions - Tracks imple

## 11. Best practices for Claude Code
<https://code.claude.com/docs/en/best-practices.md>

> - By a second opinion: a ... subagent or a dynamic workflow that checks its own findings has a fresh model try to refute the result, so the agent doing the work isn't the one grading it. ... ## Explore first, then plan, then code ... planning from implementation ... Letting Claude jump straight to coding can produce code that solves the wrong problem. Use plan mode to separate exploration from execution. ... The recommended workflow has four phases: ... Ask Claude to create a detailed implementa

## 12. Claude Code Guide 2026: Context Engineering & Planning | Generative, Inc.
<https://www.generative.inc/the-complete-claude-code-guide-2026-planning-context-engineering-and-high-leverage-development>
*2026-03-19 | Stan Sedberry*

> Claude Code is not a faster editor, it's a system for orchestrating work through context, plans, and execution loops. This guide distills what actually matters: environment setup, context structuring, plan mode workflows, cost optimization, and scaling beyond a single session. ... This guide distills what actually matters when using Claude Code at a high level: how to set up your environment, structure context, plan work, execute reliably, manage costs, and scale beyond a single session. ... If 

## 13. Claude Code Workflows: A Practical Pattern Guide
<https://www.sitepoint.com/claude-code-workflows-a-practical-pattern-guide/>
*2026-06-24*

> # Claude Code Workflows: A Practical Pattern Guide Published: 2026-06-24T20:38:39.405000+00:00 Source: sitepoint.com (sitepoint.com) Language: en ## Story Claude Code Workflows: A Practical Pattern Guide [SitePoint](https://www.sitepoint.com/) ![avatar](https://s3.sitepoint.com/images/avatars/default-50x50.jpg) [Premium](https://www.sitepoint.com/premium/pricing/?ref_source=sitepoint&ref_med

## 14. The Complete Guide to Claude Code Best Practices for Enterprise Projects | TheProductionLine
<https://www.theproductionline.ai/blog/claude-code-best-practices-complete-guide>
*2026-03-03 | TheProductionLine, Inc.*

> Optimal CLAUDE.md size ... Specialized sub-agents ... Frontend (sonnet), content (opus), QA (haiku), DB (sonnet). ... check, deploy, review, feature, new-blog-post, new-tool, scaffold. ... With best practices: Claude loads your project context in under 3 seconds from CLAUDE.md files. It follows your conventions from the first line of code, runs pre-approved commands without interruption, and delegates specialized tasks to purpose-built sub-agents. Sessions start productive and stay productive. .

## 15. 9 Parallel AI Agents That Review My Code (Claude Code Setup) - HAMY
<https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents>
*2026-02-20*

> The subagents all handle a category of problems I frequently see in code I review from AI. It also covers cases where I think I could use ...

## 16. The Claude Code Masterclass — Every Trick, Setting, and Workflow You Need | Steele O'Brien Consulting
<https://steeleobrienconsulting.com/blog/claude-code-masterclass-every-trick-and-workflow/>
*2026-03-12 | Jon Steele*

> ## Getting started: the explore-plan-code-commit loop ... Before diving into features, it helps to understand the fundamental workflow that produces the best results with Claude Code. Think of it as a loop with four phases: ... 1. Explore — Ask Claude to read and understand the relevant parts of your codebase. Let it use subagents to search broadly without polluting your main conversation context. 2. Plan — Switch to Plan Mode (press`Shift+Tab` or use`/plan`). Have Claude propose its approach, i

## 17. Claude Code Operator’s Guide: Agentic Workflows & Best Practices
<https://adambernard.com/kb/ai/models/specific-models/claude/ai-models-specific-models-claude-claude-code-operators-guide/>
*2026-02-16 | Adam*

> Operational best practices for Claude Code, Anthropic's agentic CLI. Details how to establish 'Project Memory' via CLAUDE.md, configure safety permissions, implement a 'Plan-First' architecture, and utilize specialized sub-agents (Planner, Implementer, Reviewer) for robust software development. Treats agentic development as orchestration: the developer sets context and gates, the agents plan and execute. ... Operational best practices for Claude Code, Anthropic's agentic CLI. Details how to esta

## 18. Claude Code Setup Guide: Skills, Subagents, and Measuring What Actually Works | Keon Armin
<https://keonarmin.com/blog/claude-code-configs>
*2025-11-30 | Keon Armin*

> Claude Code has emerged as the most configurable AI coding assistant on the market, offering a hierarchical file-based system that balances simplicity with enterprise-grade customization. The`.claude/` directory enables teams to share coding conventions via version control while individuals maintain local overrides—a pattern that other tools are now beginning to emulate. No standardized measurement framework exists for evaluating configuration effectiveness, representing a significant gap and op

## 19. Claude Code workflow best practices: 6 tips
<https://www.youtube.com/watch?v=CnfJKGY6rko>
*2026-05-23 | Sai Santosh Kumar (SSK)*

## 20. Claude Code best practices | Code w/ Claude - YouTube
<https://www.youtube.com/watch?v=gv0WHhKelSE>
*2025-11-05 | Anthropic*

## 21. Claude Code Workflow Cheatsheet — All 12 Sections Explained (CLAUDE.md, Skills, Hooks & Agents 2026)
<https://www.youtube.com/watch?v=VJjAQYNGzwU>
*2026-04-09 | Vamaze Tech*

## 22. Best practices for Claude Code - Claude Code Docs
<https://www.anthropic.com/engineering/claude-code-best-practices>

> # Best practices for Claude Code ... > Tips and patterns for getting the most out of Claude Code, from configuring your environment to scaling across parallel sessions. ... Claude Code is an agentic coding environment. Unlike a chatbot that answers questions and waits, Claude Code can read your files, run commands, make changes, and autonomously work through problems while you watch, redirect, or step away entirely. ... This changes how you work. Instead of writing code yourself and asking Claud

## 23. Overview - Claude Code Docs
<https://docs.anthropic.com/en/docs/claude-code/overview>

> > Claude Code is an agentic coding tool that reads your codebase, edits files, runs commands, and integrates with your development tools. Available in your terminal, IDE, desktop app, and browser. ... Claude Code is an AI-powered coding assistant that helps you build features, fix bugs, and automate development tasks. It understands your entire codebase and can work across multiple files and tools to get things done. ... `CLAUDE.md` is a markdown file you add to your project root that Claude Cod

## 24. Claude Code Advanced Patterns: Subagents, MCP, and Scaling to Real Codebases
<https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf>

> 1. Control Claude’s behavior with CLAUDE.md and Hooks 2. Parallelize Claude for major productivity gains 3. Embed Claude Code across your SDLC, from feature research to CI/CD 4. Form a mental model on when tool creation is worth the cycles 5. Imagine what an advanced Claude Code implementation could look like for your organization ##### Learning Outcomes ... ##### CLAUDE.md Similar to a README, but for Claude Forced README file to give Claude instructions on project structure, common commands, p

## 25. Claude Code: Foundations | Webinars \ Anthropic
<https://www.anthropic.com/webinars/claude-code-foundations>

> Join Anthropic's Claude Code specialist team for a hands-on introduction to Claude Code—the agentic coding tool that lives in your terminal and your repo. In one hour, we'll go from a cold install to a fixed bug, teach Claude the rules of your codebase, and show how teams scale a single agent into a fleet. Live demos throughout, run against a real service. ... - What Claude Code is and how to hand it your first task: installing the CLI, pointing it at a real repo, running the agentic loop (read,
