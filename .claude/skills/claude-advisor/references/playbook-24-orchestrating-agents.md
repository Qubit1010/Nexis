# Advanced - Section 24: Orchestrating Multiple Agents

*When one Claude is not enough.*

**Bottom line:** Some tasks are too large, too parallel, or too complex for a single Claude Code session. Orchestration is the practice of coordinating multiple Claude Code agents, each working on part of the problem, under the direction of a primary orchestrator. This is where Claude Code starts to feel like a team rather than an assistant.

---

## One agent to many

A single Claude Code session has a context window limit. Very large projects (a full codebase refactor, a research synthesis across dozens of sources, a multi-part content pipeline) can exceed what one session can hold. Orchestration solves this by splitting the work across multiple agents, each holding a piece of the project in its context.

The primary Agent (the orchestrator) holds the overall plan and coordinates. The worker Agents (subagents or parallel sessions) execute specific pieces and report back.

## Dynamic Workflows and Ultra Code

Two advanced Claude Code features support orchestration:

- **`/workflows`:** Lets you define a multi-step pipeline that Claude Code follows, with each step potentially spawning subagents or handoff points. Think of it as a flowchart Claude Code executes.
- **`/ultracode`:** A high-autonomy mode where Claude Code takes a complex task description and handles the full breakdown, subagent spawning, and synthesis on its own. Best for experienced users who trust Claude Code's judgment on large tasks.

## Worktrees for parallel sessions

A worktree is an isolated copy of your codebase that Claude Code can work in without affecting the main branch. Multiple Claude Code sessions can each have their own worktree, allowing genuinely parallel development:

- Session A works on the authentication refactor in its worktree
- Session B fixes the data import bug in its worktree
- Session C writes tests for the existing feature in its worktree

All three run at the same time. When done, you review and merge the ones that worked.

## Monitoring agents: the dashboard

When running multiple agents, use the Claude Code agent dashboard (accessible via `claude agents` in the terminal) to see the status of all running sessions, what each one is doing, whether any are waiting for input, and their output so far.

## When to use orchestration vs keep it simple

| Use orchestration when... | Keep it simple when... |
|--------------------------|----------------------|
| The task genuinely cannot fit in one context window | The task is straightforward and sequential |
| Different parts of the task are truly independent | You are still learning how Claude Code works |
| You want parallel processing to save time | The coordination overhead would exceed the time saved |
| You are building a system that needs to scale | The task is a one-off that will not repeat |

## The cost warning

Running multiple Claude Code sessions simultaneously multiplies your token usage. Each agent has its own context window. If you are running five agents in parallel on a large codebase, your usage is five times a single session. Check your plan limits before running large orchestrated pipelines.

## Key takeaways

- Orchestration coordinates multiple Claude Code agents on different parts of a large task.
- The primary orchestrator holds the plan; worker subagents execute the pieces.
- `/workflows` defines multi-step pipelines; `/ultracode` lets Claude Code handle the breakdown autonomously.
- Worktrees enable genuine parallelism: isolated copies of your codebase, one per session.
- Monitor running agents via `claude agents`. Watch for usage multiplication at scale.
