# AI agent evaluation framework: my harness scored 50% for months and was broken

By Aleem Ul Hassan, AI automation engineer and full-stack developer.

An agent evaluation framework gives an agent a task, lets it run, and grades the result against defined success criteria. The hard part is not the grading logic. It is that a broken harness and a genuinely failing agent produce the same number, and nothing in the score tells you which one you are looking at.

I learned that expensively. My own harness reported roughly 50% for months. I rewrote descriptions, adjusted thresholds, and assumed the work was bad. The harness was launching a binary that no longer existed, every invocation failed, and each failure was recorded as "did not trigger."

## What is an AI agent evaluation actually testing?

Not output quality. Trajectory.

A single-turn evaluation is simple: a prompt, a response, and grading logic. Agents break that model because they run over many turns, call tools, change state, and adapt as they go. Anthropic's engineering team puts the tension plainly: "The capabilities that make agents useful also make them difficult to evaluate." The autonomy you are paying for is the same property that makes the result hard to check.

The practical consequence is that grading the final answer is insufficient. An agent can reach a correct output through a path that was expensive, unsafe, or accidentally correct, and a final-answer grader will call all three a pass. You have to look at what it did, not only what it produced.

## Why does a score near 50% mean nothing?

Because on a binary test, that is what noise looks like.

This is the single most useful heuristic I took from the whole episode. If your evaluation is pass or fail per task, a random result lands near 50%. So does a harness that fails to invoke anything. So does one where the grader itself is broken. All three are indistinguishable from a genuinely mediocre agent when you only read the number.

The fix is not a better score. The fix is making the harness able to report a third state. A run that could not execute must be recorded as "did not run," never folded into "failed." Those are different facts and collapsing them is how a measurement system lies to its owner without anyone acting in bad faith.

## How do you tell a broken eval from a failing agent?

Three checks, cheapest first.

Run the harness against a case you know passes. If a known-good input fails, the harness is broken, not the agent. Then run it against a case you know fails. If a known-bad input passes, the grader is broken. Only when both controls behave correctly does the middle of the distribution mean anything.

Then check the invocation layer separately from the grading layer. In my case the failure was neither the agent nor the grader. It was the process launcher, which sat below both and was invisible to both. A harness that reports only scores cannot surface that, which is why the harness needs to log what it actually executed, not just what it concluded.

## Can the evaluation itself be wrong about a good result?

Yes, and this direction is less discussed than it should be.

Anthropic describes a case where a frontier model solved a benchmark task about booking a flight "by discovering a loophole in the policy. It 'failed' the evaluation as written, but actually came up with a better solution for the user." The system did something better than the test anticipated and the test scored it down.

That is not an edge case, it is a structural property of static tests applied to systems that can find paths you did not enumerate. It means a falling score is genuinely ambiguous: the agent may have got worse, or it may have got creative in a way the rubric did not allow for. Reading the failures rather than the aggregate is the only way to tell.

## What should a practical eval setup include?

Four things, and none of them require a vendor platform to start.

A small set of tasks with genuinely known answers, including at least one known-good and one known-bad control. Grading that inspects the path and not only the final output. Explicit separation of "did not run" from "ran and failed." And version pinning, so that when a score moves you know whether the agent changed or the environment did.

Anthropic's own writeup on [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) is the most useful starting point I have read, particularly on why multi-turn grading has to differ from single-turn. It also makes the case that evals compound in value over an agent's lifecycle, which matches what I saw: the harness became useful only after it could tell me why something failed.

## What this costs if you skip it

The failure is not dramatic. That is the problem.

Without a working evaluation you do not get a crash, you get a slow drift where things mostly work and occasionally do not, and nobody can say whether last month was better. Anthropic frames the alternative as getting "stuck in reactive loops," catching issues only in production where fixing one creates another. That matches my experience precisely.

I lost months to a broken measurement rather than to a broken system, and the broken measurement was more expensive, because it sent me to fix things that were never wrong.

## Frequently asked questions

### How do you evaluate an AI agent?

Give it tasks with known success criteria, grade the path it took rather than only the final output, and include known-good and known-bad control cases so you can tell a broken harness from a failing agent.

### What is the best evaluation framework for AI agents?

There is no single best one, and the choice matters less than the setup around it. A simple harness that distinguishes "did not run" from "ran and failed" beats a sophisticated one that collapses them.

### Why is my agent eval score around 50%?

Treat that as a warning rather than a result. On a binary test, random output, a broken harness and a broken grader all land near 50%. Run a known-good input before concluding anything about the agent.

### Can an evaluation be wrong about a correct answer?

Yes. A capable system can solve a task in a way the rubric did not anticipate and be scored as a failure. Read the individual failures rather than the aggregate before acting on a drop.

---

## SEO Metadata

- **Primary keyword:** ai agent evaluation framework
- **Secondary:** how to evaluate an ai agent, ai agent evaluation, agent evals
- **Title tag:** AI Agent Evaluation Framework: Why 50% Means Nothing
- **Meta description:** My agent eval harness reported 50% for months while being completely broken. How to tell a failing agent from a failing measurement, and why it matters.
- **Slug:** /blog/ai-agent-evaluation-framework
- **Cluster:** 30 · **Winnability:** 5.0 · **UGC on page 1:** yes · **Median result age:** 201 days
- **Outbound citations:** anthropic.com/engineering/demystifying-evals-for-ai-agents
- **Expert quote:** Anthropic engineering team, two attributed quotes inline
- **POV source:** the eval harness that launched a dead binary and scored every failure as "not triggered"; the 50%-is-noise heuristic
- **Internal links:** /services, /work, /blog/ai-agent-vs-skill
- **Difficulty note:** page one carries anthropic.com, aws.amazon.com, ibm.com and databricks.com. Winnability scores 5.0 on diversity and UGC, but the brand weight here is real. The differentiated angle is the practitioner failure story, which none of those publish.
