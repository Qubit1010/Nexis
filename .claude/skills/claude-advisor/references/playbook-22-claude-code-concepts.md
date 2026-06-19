# Advanced - Section 22: Claude Code Concepts You Need to Know

*The mental model that makes everything in Claude Code make sense.*

**Bottom line:** Claude Code has a specific architecture: Workflows define the task, the Agent executes it, Tools do the actual work. Understanding this triangle, plus CLAUDE.md, context window management, and permissions, will save you hours of trial and error.

---

## The core mental model: Workflows, Agent, Tools

- **Workflows** are the high-level plans Claude Code makes before acting. They are the "here is what I am going to do" that Claude shows you before executing. In Plan Mode, you see and approve the workflow before anything happens.
- **The Agent** is Claude itself, running in the terminal, reading and writing files, calling tools, and iterating on results.
- **Tools** are what the Agent uses to actually do things: reading a file, writing a file, running a command, searching the codebase, calling an API. Claude Code has a set of built-in tools and can use external ones via MCP.

## CLAUDE.md: your standing instructions

CLAUDE.md is a file you put in your project folder. Every time Claude Code starts in that folder, it reads this file first. Think of it as the custom instructions from Projects, but for Claude Code. Use it to tell Claude Code:

- What the project is and what it does
- What stack, libraries, and conventions to use
- What it must not do (delete certain files, change certain settings)
- How you want code formatted, named, and organized
- Context about the team or business that helps it make better decisions

A good CLAUDE.md means you never re-explain the project. A missing one means Claude Code starts from scratch every time.

## The context window and context rot in Claude Code

Just like in chat, Claude Code operates within a context window. In very long sessions (large codebases, many file reads, extended iterating), the early context gets compressed and Claude Code can lose track of earlier decisions or file contents.

Signs: inconsistent changes, forgetting about a file it saw earlier, repeating a question it already asked.

Fixes: Start a new Claude Code session with a fresh summary of what has been done. Use CLAUDE.md to anchor the standing context so it does not have to re-derive it from the session.

## Permissions and autonomy

Claude Code asks for permission before taking actions that could be destructive or irreversible (deleting files, running commands that modify your system). You can configure how much autonomy it has:

- **Default (ask each time):** Claude Code stops before any significant action and asks you to approve. Best for new projects and sensitive codebases.
- **Elevated trust:** You can tell Claude Code to proceed with certain categories of action without asking each time. Use this only for well-understood, reversible operations.

Never give Claude Code blanket permission to do anything without understanding what that means in your specific project.

## Plan Mode: Shift+Tab

Pressing Shift+Tab in Claude Code activates Plan Mode. In Plan Mode, Claude Code builds the full workflow before taking any action, shows you exactly what it plans to do, and waits for your approval. This is the right mode for:

- Large tasks touching many files
- Anything involving irreversible changes
- Situations where you want to understand the approach before execution

Use Plan Mode by default until you are comfortable with how Claude Code works in your specific project.

## Essential commands

| Command | What it does |
|---------|-------------|
| `/init` | Read the project and generate a CLAUDE.md file automatically |
| `Shift+Tab` | Toggle Plan Mode (plan before act) |
| `/btw` | Add a note to the session context mid-task |
| Custom status line | Show current task and progress in the terminal |
| Screenshot loop | Claude Code can take screenshots of running apps and iterate on them |

## Key takeaways

- The mental model: Workflows (plans) + Agent (Claude) + Tools (file ops, commands, APIs).
- CLAUDE.md is your standing instructions file. Create it on every project with `/init` and keep it current.
- Context rot happens in long sessions. Start fresh when you see inconsistency.
- Permissions are granular. Start with ask-each-time and only loosen as you build trust.
- Plan Mode (Shift+Tab) is your safety net for large or risky tasks.
