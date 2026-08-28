# AI agent vs skill: I built 104 skills and zero agents

By Aleem Ul Hassan, AI automation engineer and full-stack developer.

A skill is a set of instructions loaded on demand. An agent is a process that runs a loop, decides what to do next, and keeps going until it stops itself. The difference that matters commercially is not capability, it is blast radius. A skill fails visibly on one task. An agent fails quietly across many, and the failure compounds before anyone notices.

I have 104 skills in a single working directory and no autonomous agents running unattended. That was not a philosophical decision. It is what happened after I shipped both and watched which one I could actually trust on a Friday afternoon.

## What is the actual difference between an agent and a skill?

A skill is closer to a checklist than to a colleague. It sits on disk, gets loaded when the task matches, tells the model how to do one thing properly, and then goes away. Its scope is a single invocation. When it is wrong, it is wrong in front of you, on one task, and you can read the instructions and see why.

An agent owns the loop. It calls tools across many turns, changes state as it goes, and adapts based on what came back. Anthropic's engineering team frames the tradeoff directly: "The capabilities that make agents useful also make them difficult to evaluate." Autonomy, intelligence and flexibility are the same properties in both columns. They are what you are buying and what makes the thing hard to check.

| | Skill | Agent |
|---|---|---|
| Scope | One task, one invocation | Many turns, until it decides to stop |
| State | Stateless | Modifies state as it runs |
| Failure | Visible, on one task | Propagates and compounds |
| Debugging | Read the instructions | Replay the trajectory |
| Right when | The procedure is known | The path is genuinely unknown |

## Why did 104 skills beat the agents?

Because almost every problem I actually had was a procedure I already knew, written down badly or not at all.

The keyword research process, the SERP read, the lead enrichment pipeline, the proposal structure. None of those needed a system that reasons about what to do next. They needed the correct steps, in order, applied consistently. That is a skill. Handing them to an agent adds a decision layer on top of a problem that had no decisions left in it, and the decision layer is exactly where the compounding failure lives.

The honest test I now use: **write the procedure down first.** If you can write it, you do not need an agent, you need the written procedure loaded at the right moment. If you genuinely cannot write it, because the path depends on what the last step returned, that is the case for a loop.

Most of what gets sold as agentic work fails that test. It is a procedure someone did not want to write.

## What does the failure actually look like?

Two examples from my own work, both of which cost real time.

A lead enrichment pipeline I built resolved company founders by searching for them. It worked, in the sense that it returned a person for almost every row. It also attached the wrong person repeatedly. One agency got matched to an unrelated notary who shared a first name. Another got the art director instead of the co-founder. The system was confident every time. I only found it because a human read the spreadsheet and recognised a name that was obviously wrong.

The fix was not a better agent. The fix was inverting the order: scrape the company's own website first, take the founder from their own About page, and only fall back to search when the site names nobody. Provenance became a field. Anything sourced from search stopped being written automatically and went to a review queue instead.

That is the pattern. The agent version optimised for always returning an answer. The skill version optimised for knowing when it did not have one.

## How do you evaluate either one?

Evaluation is where I lost the most time, and the lesson generalises past AI entirely.

I built an eval harness to score whether skills triggered correctly. It reported roughly 50% for months. I assumed the descriptions were badly written and rewrote several of them, which changed nothing. The harness was launching a command-line binary that no longer existed. Every invocation failed, and the harness scored each failure as "the skill did not trigger."

**A broken measurement and a real result are indistinguishable unless the harness can tell you which one it produced.** A score near 50% on a binary test is the tell, because that is what noise looks like.

Anthropic's own guidance describes the same class of problem from the other side, noting that a frontier model solved a benchmark task about booking a flight "by discovering a loophole in the policy. It 'failed' the evaluation as written, but actually came up with a better solution for the user." The eval was wrong, not the model. In my case the eval was wrong, not the skills. Both directions are live, and neither is visible from the score alone.

## When is an agent genuinely the right call?

Three conditions, and I want all three before I reach for one.

The path is unknown at the start, so the next step depends on what the last one returned. The cost of a wrong step is recoverable, meaning nothing irreversible happens without a human. And there is a way to check the work that does not rely on the same system that did it.

Client work has met that bar. An automated proposal pipeline built in n8n for a client genuinely needed a loop, because the input documents varied so much that no fixed sequence covered them. A document analysis system using retrieval over a client's own corpus needed one too, since the question determined the path.

What none of them needed was autonomy without a checkpoint.

## What should an agency owner ask a partner about this?

One question does most of the work: ask them to write the procedure down. If they can write it, ask why it needs to be an agent at all. If they cannot write it, ask how they will know when it is wrong, and treat "the model handles it" as a no rather than an answer.

The practitioner communities are ahead of the vendor marketing here. The [r/ClaudeAI thread on agents versus skills](https://www.reddit.com/r/ClaudeAI/comments/1s5bo5v/help_me_understand_agents_vs_skills/) is a reasonable snapshot of where opinion actually sits, and it is considerably less settled than any product page suggests.

I ship skills by default and agents by exception. After 104 of the first and a handful of the second, that ratio has not moved.

## Frequently asked questions

### Is an AI skill the same as an agent?

No. A skill is instructions loaded for one task and it is stateless. An agent runs a loop across many turns, modifies state, and decides when to stop. A skill can be used by an agent, but the two are not interchangeable.

### What is the difference between ChatGPT agents and skills?

The vocabulary differs by vendor and the underlying split does not. Anything that loads context for a single task behaves like a skill. Anything that keeps calling tools until it satisfies a goal behaves like an agent, whatever the product name.

### Can you use skills and agents together?

Yes, and this is the common production shape. The loop belongs to the agent and the individual procedures belong to skills, which keeps each step readable and testable on its own.

### How do I know if I need an agent?

Write the procedure down. If you can write it, you need the procedure, not the agent. If the next step genuinely depends on what the last step returned, you have a real case for a loop.

---

## SEO Metadata

- **Primary keyword:** ai agent vs skill
- **Secondary:** ai agent vs mcp, ai agent vs automation, agents vs skills
- **Title tag:** AI Agent vs Skill: I Built 104 Skills and Zero Agents
- **Meta description:** A skill is instructions for one task. An agent owns the loop. After building 104 skills and shipping few agents, here is when each one actually wins.
- **Slug:** /blog/ai-agent-vs-skill
- **Cluster:** 42 · **Winnability:** 5.0 · **UGC on page 1:** yes · **Median result age:** 120 days
- **Outbound citations:** anthropic.com/engineering/demystifying-evals-for-ai-agents, reddit.com/r/ClaudeAI/comments/1s5bo5v
- **Expert quote:** Anthropic engineering team, attributed inline
- **POV source:** 104 skills in `.claude/skills/`; the lead-enrichment founder-resolution failure; the eval harness scoring a dead binary as "not triggered"
- **Internal links:** /services, /work, /work/nexis-scaling-operations-with-an-agentic-ai-ecosystem
