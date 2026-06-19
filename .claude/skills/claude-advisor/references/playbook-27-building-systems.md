# Advanced - Section 27: Building Systems That Run Themselves

*From one-off tasks to production automations.*

**Bottom line:** The skills from the previous sections let you build things. This section is about making those things run, on a schedule, reliably, without you watching. Three deployment paths, one golden rule.

---

## Three ways to deploy an automation

| Method | Where it runs | Best for |
|--------|-------------|----------|
| Local loop / cron | Your own computer, on a schedule | Tasks that need your local files, your apps, or your credentials |
| Cloud Routine | Anthropic's servers (Claude subscription) | Tasks that are purely digital and do not need your machine |
| External cloud + Agent SDK | Your own cloud server or hosting (AWS, GCP, Render, etc.) | Production systems, custom tools, client-facing products |

## The local loop (cron)

The simplest automation: a script that runs on a schedule using your computer's task scheduler (cron on Mac/Linux, Task Scheduler on Windows) or the Claude Code `/schedule` command. The script calls Claude Code, which executes the task and saves the output.

Good for: morning briefs, weekly report generation, overnight processing of local files.

Requires: your computer to be on and awake when the task runs.

## Cloud Routines

Covered in Section 16. These run on Anthropic's infrastructure, not your machine. The task is defined in Claude Code and scheduled via the Routines panel. You log in and review the outputs; the execution happened in the cloud.

Good for: tasks that do not need your local machine (web research, email drafts, content pipelines using external APIs).

## The Agent SDK: production-grade systems

The Anthropic Agent SDK is the path for building systems that run at scale, serve users, or power client-facing products. It is an API-based interface that lets developers embed Claude Code's intelligence into their own applications, with:

- Custom tools the agent can call
- Custom permissions defining what it is allowed to do
- Full orchestration: spawning subagents, routing tasks, handling errors
- Production-grade reliability: retries, logging, monitoring

**Managed Agents:** Anthropic's hosted path for teams that do not want to manage their own server infrastructure. You define the agent behavior, Anthropic handles the hosting.

## Guardrails: keeping automations safe

Any automation that runs without you watching needs guardrails:

- **Hooks:** Pre- and post-action scripts that validate what Claude Code is about to do before it does it. A hook can reject an action that falls outside defined parameters.
- **Permissions:** Define exactly what the automation is allowed to access, write, send, or change. Keep this as narrow as possible.
- **Secrets management:** Never hard-code API keys, passwords, or credentials into your automation scripts. Use environment variables or a secrets manager.
- **Logging:** Every production automation should log what it did, when, and the result. You want a record you can audit.

## The golden rule

**Automation built on the API runs reliably and at scale. Automation built on a subscription surface (Claude.ai, Claude Desktop) is for personal use and does not have production SLAs.**

If you are building something for clients, for other users, or that needs to run 24/7 without intervention: use the API and the Agent SDK. If it is for your own workflow and you are comfortable with the occasional hiccup: subscription + local/cloud routines is fine.

## Key takeaways

- Three deployment paths: local cron (your machine), Cloud Routines (Anthropic's servers), Agent SDK (your own cloud or Managed Agents).
- Local is simplest but requires your machine to be on. Cloud Routines are hands-off but limited to digital tasks. Agent SDK is the production path.
- Every production automation needs guardrails: hooks, narrow permissions, proper secrets management, and logging.
- The golden rule: client-facing or always-on systems belong on the API, not on a subscription surface.
