# Closeout & Push Prompt

After completing any of the following actions, always end your response with the two questions below — in this exact order, on their own line:

**Trigger actions:**
- Created a new skill (new folder + SKILL.md in `.claude/skills/`)
- Installed a skill or plugin via `npx skills add` or `claude plugin install`
- Created a new project folder under `projects/`
- Created multiple new files as part of a feature, workflow, or system (not single-file edits)
- Made significant structural changes to the repo (gitignore, CLAUDE.md, skills-lock.json, etc.)

**Questions to ask (always both, always in this order):**

> Want me to run `/session-closeout` to log decisions and update priorities?
>
> Should I push these changes to GitHub?

**Rules:**
- Ask after the work is done, not before.
- Both questions on every trigger — never skip one.
- If the user already ran session-closeout this session, skip the first question and only ask about the push.
- If the user already pushed this session as part of the same task, skip the second question.
- Don't ask for trivial single-file edits (fixing a typo, updating a line in an existing file).
