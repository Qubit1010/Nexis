---
name: delegate
description: Use when someone asks to delegate a task, assign work to a team member, hand off a task, or send a task to someone on the team.
argument-hint: [task description]
---

# Team Task Delegation

## When to Trigger

Activate when the user says:
- "delegate [task]", "delegate [task] to [person]"
- "assign [task]", "assign [task] to [person]"
- "hand off [task]", "send this to [person]"
- "who should handle [task]?"

Also trigger proactively: when Aleem is about to do work that should be delegated (frontend, design, Webflow, ops tasks), suggest: "This looks like [category] work. Want me to draft a delegation message for [Person]?"

## Context

Before processing, read:
- `context/team.md` -- team roster, roles, availability
- `.claude/rules/agency-operations.md` -- delegation defaults and priority framework

## Steps

### Step 1: Parse the Request

Extract from $ARGUMENTS or conversation:
- **Task description** -- what needs to be done
- **Deadline** -- if mentioned (otherwise "None specified")
- **Specific person** -- if the user named someone
- **Additional context** -- project name, client, reference files, links

If the task is too vague to delegate, ask for clarification before proceeding.

### Step 2: Match Team Member

If the user named a specific person, use that person. Otherwise, auto-match:

| Task Type | Assign To |
|-----------|-----------|
| Frontend, UI, design, Framer, Webflow (simple) | Areeba Noor |
| Complex Webflow builds | Sohail Ahmed |
| Full-stack, backend, MERN, Next.js apps | Muzammil |
| Upwork bidding, operational tasks, misc ops | Moiz Hussain |
| Large UI/UX projects, design systems | Sher Nadir |
| 3D web, Three.js, Python automation | Ashhad |
| Executive, strategic, high-level decisions | Kaleem |

If the task does not clearly match one category, present options: "This could go to [Person A] or [Person B]. Who do you want?"

### Step 3: Generate Delegation Message

Write a WhatsApp/Discord-ready message. Rules:
- Max 6-8 lines. Shorter is better.
- No emojis. No em dashes. Natural, direct tone.
- Include enough context that the person can start without follow-up questions.
- Include reference files, links, or Figma URLs if provided.

Format:
```
Hey [Name],

[1-2 sentence task description -- what needs to be done and why]

[Scope/details as bullet points if needed]

[Deadline line if applicable]

Let me know if anything's unclear.
```

### Step 4: Present Output

Show in this format:

```
**Delegating to:** [Name] ([Role])
**Task:** [one-line summary]
**Deadline:** [deadline or "None specified"]
**Channel:** WhatsApp / Discord

---

**Ready-to-send message:**

[the message]

---

Copy and send. Want me to adjust anything or log this?
```

### Step 5: Log (Optional)

Only log if the user says "log this", "track this", or confirms logging.

Append to `logs/delegations.md`:

```markdown
### [YYYY-MM-DD] [Task summary]
- **Assigned to:** [Name]
- **Deadline:** [deadline]
- **Status:** Delegated
- **Notes:** [any context]
```

If the file does not exist, create it with this header first:

```markdown
# Delegation Log

Track of all delegated tasks.

---
```

## Rules

- Never auto-send messages. Always present for review first.
- Never guess scope on vague tasks. Ask for clarification.
- Keep messages natural. Write like a founder texting a teammate, not a corporate template.
- If Aleem overrides the auto-match, use his choice without pushback.
