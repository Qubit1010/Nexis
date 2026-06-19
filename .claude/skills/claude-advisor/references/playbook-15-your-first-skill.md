# Intermediate - Section 15: Your First Skill: Making Claude Truly Yours

*Stop re-explaining yourself. Build once, reuse forever.*

**Bottom line:** A Skill is a saved set of instructions, context, and behavior that Claude loads for a specific task. It is how you stop repeating yourself and start running repeatable workflows in seconds. Build your first one and the upgrade is immediate.

---

## What a Skill actually is

A Skill is a piece of structured context that tells Claude who to be, what to know, and how to behave for a specific, repeatable task. It is not an app or a plugin, it is closer to a detailed onboarding document for a specialist assistant.

When you invoke a Skill, Claude loads everything in that document before responding, so you never have to re-explain your preferences, your audience, your format, or your constraints again.

## The three-times rule

Build a Skill when you have done the same type of task three or more times and written similar instructions each time. If you have asked Claude to "write a client update in my voice, keep it under 150 words, reference the project status" more than twice, that is a Skill.

## How to build one

**Method 1: Describe it.** Tell Claude: "I want to build a Skill for [task]. It should always do [behavior], know about [context], and produce [format]. Help me write it." Claude will draft the Skill document for you.

**Method 2: Interview method.** Tell Claude: "I need a repeatable workflow for [task]. Interview me to understand what always has to be true, what context matters, and what good output looks like. Then write the Skill based on my answers." More thorough, produces better Skills for complex tasks.

## What a good Skill contains

- **Who Claude is in this context** (the role it plays)
- **The standing context** (background knowledge that never changes: your brand, your process, your clients)
- **The repeatable task** (exactly what it does each time)
- **The output format** (structure, length, tone, what to avoid)
- **At least one example** of ideal output (the fastest way to lock in your taste)

## Chaining Skills

Skills can reference other Skills, letting you build a library of modular, composable pieces. "Use the Brand Voice skill and the Client Summary format from the Client Update skill to draft this status report." This is how you turn Claude from a general assistant into something that genuinely knows your operation.

## Worked example: Weekly Client Update skill

**Context loaded:** You are an assistant for a digital agency. Always keep updates under 150 words. Write in a confident, friendly tone. Avoid jargon. Reference what was done, what is next, and if there are any blockers.

**Task:** When given a project name and a set of notes, produce a client update ready to send.

**Format:** 3 short paragraphs. No subject line needed.

**Example output:** [A real past update that landed well.]

Once this Skill exists, the workflow is: "Client update, Project X, notes: [paste raw notes]." The output is ready to send in under a minute.

## Keep Skills alive

A Skill that does not reflect your current process is worse than no Skill, because it produces confidently wrong output. Treat them like living documents: when your format changes or you find a better example, update the Skill. A quarterly review of your active Skills takes 20 minutes and keeps everything sharp.

## Key takeaways

- A Skill is structured context that Claude loads for a specific repeatable task. It is not code or a plugin.
- Build one when you have done the same setup work three or more times.
- Good Skills contain: role, standing context, the repeatable task, the format, and at least one example.
- Chain Skills to build modular, composable workflows across your operation.
- Keep them current: an outdated Skill is worse than no Skill.
