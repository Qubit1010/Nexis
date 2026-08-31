# Design Review: the critic pass and the adversarial audit

Two review gates that bracket the build. The critic runs on the *design*, before any file is
written. The audit runs on the *finished skill*, in a context that has never seen the design.

Both are prose protocol. Neither needs a script, a subagent framework, or a directory.

---

## 1. Critic pass (before building)

Once the design is settled and before writing SKILL.md, stop and attack it. Do not defend the
previous reasoning. The goal is to find reasons not to build this, or to build something else.

Work through these, in this order, because the first one kills more designs than the rest combined:

**Overlap with an existing skill.** Check the skill list and `references/skills-catalog.md`
before assuming this capability is missing. Ask whether an existing skill already covers 80
percent of it and needs a handoff rather than a sibling. This matters more here than the
generic advice suggests: a new skill that under-triggers in evals usually means an older
overlapping skill is absorbing its prompts, and the fix is to repair the *older* skill's
handoff, not to reword the new one.

**Unnecessary complexity.** Which parts of this design are load-bearing, and which are there
because they look thorough? A phase that never changes an outcome is a phase to cut.

**Over-specification.** Is this written as "step 1 through step 14," or as task, guardrails
and exit criteria? Long numbered procedures encode how *today's* model needs to be handled and
degrade as models improve. Prefer the higher-altitude version unless the sequence is genuinely
load-bearing (an API that must be called in order, a destructive step that needs a gate).

**Scripts that should be prose, and prose that should be a script.** Deterministic, repeatable
work belongs in `scripts/`. Judgment belongs in the SKILL.md body. Getting this backwards
produces either a brittle script that hardcodes a judgment call or a prose instruction that
asks the model to do arithmetic by hand.

**Verification.** How does this skill know it succeeded? If the answer is "the user will
notice," it has no verification and cannot be trusted to run unattended. A check that cannot
distinguish "did not run" from "ran and returned nothing" is worse than no check, because it
reports success either way.

**Failure modes.** What does this do with bad input, a dead API, an empty result set, or a
missing credential? Returning `unknown` honestly is a correct outcome. Fabricating a plausible
answer is not.

Write the findings down and resolve them before building. If the critic pass produces nothing,
it was not run seriously.

---

## 2. Adversarial audit (after building)

Run the finished skill against real cases in a fresh context. The auditor must not see the
design discussion, the critic pass, or any of the reasoning that produced the skill. Given that
history it will grade the intent instead of the artifact.

Frame it explicitly:

> You are an independent evaluator. Audit this skill as if deciding whether it can be used on
> paying client work. Try to make it fail. Document every failure. Do not optimize for making
> the skill look good, optimize for finding problems.

**Use real cases, not synthetic ones.** A skill that handles a tidy invented example and breaks
on a real client's messy input has not been tested. Pull actual material: a real transcript, a
real job post, a real URL, a real client folder.

**Include cases designed to break it:**

- Input that is wrong, contradictory, or missing the field the skill assumes is present.
- A request just outside the skill's scope, to see whether it declines or improvises.
- The same input twice, to see whether the output is stable enough to trust.

**Judge the output, never the SKILL.md.** An impressive-looking skill file is not evidence.
The only evidence is what came out when it ran.

**Then run the trigger evals** (`scripts/run_eval.py`). Note the two known harness traps:
use `--num-workers 2`, and treat a score near 50 percent as a signal that the harness itself
is broken rather than that the description is bad.
