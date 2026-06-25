# Never Break Rules

Every rule in `.claude/rules/` is active at all times. Never skip, shortcut, or override any rule unless Aleem explicitly says to bypass it in that message.

**Examples of what this prevents:**
- Scaffolding a skill directly when `skill-creation.md` says to ask first
- Skipping the closeout/push prompt after creating a skill
- Writing em dashes in content when `communication-style.md` forbids them
- Committing without checking gitignore when `closeout-and-push-prompt.md` applies

**The standard:** If a rule applies to what you're about to do, follow it — even if it means pausing to ask a question before acting. "I forgot" or "I thought it was implied" are not valid reasons to skip a rule.

If Aleem explicitly says "skip the skill-creator", "just scaffold it", "bypass X rule", etc. — then proceed without it. Authorization must be explicit and in the current message.
