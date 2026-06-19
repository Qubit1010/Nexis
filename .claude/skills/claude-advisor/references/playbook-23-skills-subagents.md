# Advanced - Section 23: Skills and Subagents in Claude Code

*Encode your workflows once. Delegate the execution.*

**Bottom line:** In Claude Code, Skills are structured markdown files that define repeatable behaviors, and subagents are separate Claude Code instances spawned to handle parts of a larger task in parallel. Together, they let you build a system where Claude Code runs complex, multi-part work without constant supervision.

---

## Skills in Claude Code

Skills in Claude Code work on the same principle as the Intermediate-level Skills from Section 15, but they live as markdown files inside the Claude Code environment and are loaded by the Agent when invoked. Instead of copy-pasting a prompt each time, the Agent reads the Skill file and executes the behavior defined inside.

A good Skill in Claude Code contains:

- **Role and capability:** Who Claude Code is acting as for this task (a code reviewer, a data analyst, a documentation writer)
- **The task definition:** What it should do when invoked, with enough specificity that the output is consistent
- **The output format:** What the result looks like (a file, a formatted report, a changed codebase)
- **Constraints:** What it must not do, what to ask before doing
- **An example:** The single most useful thing you can add

Two categories of Skills:
- **Capability skills:** Define what Claude Code can do ("when asked to review code, always check for these five things and output a structured report")
- **Preference skills:** Define how Claude Code should behave ("always use TypeScript, never use any, prefer explicit error handling over try-catch")

## Progressive disclosure

Claude Code loads Skills only when they are relevant, not all at once. This keeps the context window from filling with Skills you do not need right now. Design your Skills to be specific enough that Claude Code can identify when to use them without ambiguity.

## Subagents: delegated workers

A subagent is a separate Claude Code instance that runs alongside the primary session, handling a delegated piece of work. The primary Agent spawns subagents for:

- **Parallel work:** Researching multiple things at the same time
- **Isolated tasks:** Work that should not contaminate the main session context
- **Specialization:** A subagent focused only on writing tests while the primary Agent focuses on implementation

A subagent gets its own context window, its own set of tools, and its own instructions from the primary Agent. When it is done, it reports back.

## Skill vs subagent: the distinction

| Skill | Subagent |
|-------|----------|
| A set of instructions for how to behave | A separate Claude Code instance that executes |
| Loaded as context, no separate process | Runs in its own session, in parallel |
| Defines the what and how | Does the actual work |
| Reusable across many sessions | Spawned for a specific task, then done |

They combine: a subagent can have Skills of its own, defining how it behaves while it works on its delegated piece.

## Worked example: research-and-write pipeline

A primary Agent is tasked with producing a competitive analysis report.

1. It reads the Research Skill (defines how to gather information) and the Report Writing Skill (defines the output format and depth).
2. It spawns three subagents: one researches Competitor A, one researches Competitor B, one researches Competitor C. All three run in parallel.
3. Each subagent returns a structured summary to the primary Agent.
4. The primary Agent synthesizes the summaries and writes the final report using the Report Writing Skill as its guide.

What would take a person several hours of research, synthesis, and writing, the primary Agent + three subagents completes as a coordinated pipeline.

## Key takeaways

- Skills in Claude Code are markdown files that define repeatable behaviors. Two types: capability (what to do) and preference (how to behave).
- Progressive disclosure means Skills load when needed, keeping the context window efficient.
- Subagents are separate Claude Code instances delegated to run parallel or isolated work.
- Skills + subagents together enable complex, multi-part workflows with minimal supervision.
