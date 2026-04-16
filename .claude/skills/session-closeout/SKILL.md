---
name: session-closeout
description: >
  End-of-session wrap-up skill for Aleem's Nexis assistant. Summarizes what was done,
  extracts decisions worth logging, and updates context/current-priorities.md to reflect
  any shifts. Use this skill whenever the user says "close out", "wrap up", "end session",
  "session summary", "closeout", "wrap this up", "let's close", or anything indicating
  they're done for the session. Also trigger if the user says "what did we do today" or
  "summarize this session". This skill should always be used at session end — don't just
  summarize inline, run this skill so decisions get logged and priorities stay current.
---

# Session Closeout

Turns the raw work of a session into organized memory: a clean summary, logged decisions, and updated priorities. Run this at the end of every session so context files stay current and nothing meaningful gets lost.

---

## Step 1 — Gather What Changed

Before summarizing, ground yourself in actual changes made. Run the following:

```bash
git status
git diff --stat HEAD
```

This tells you what files were created or modified — use it as a concrete anchor for the summary. Don't rely on memory alone; the diff doesn't lie.

Also scan the conversation for:
- Files created or significantly changed
- Tools built, scripts written, features added
- Problems solved or bugs fixed
- Anything explicitly decided or rejected

---

## Step 2 — Write the Session Summary

Print a clean session summary directly in the conversation (don't save to a file unless the user asks). Use this structure:

```
## Session Summary — [Today's Date]

**Focus:** [1-line description of the session's main theme]

### What Got Done
- [Concrete item — be specific, not vague. "Built X" not "worked on stuff"]
- ...

### Open Items
- [Things started but not finished, or explicitly noted as next steps]
- ...
```

Keep it tight. If the session was focused, the summary should be 5-10 bullets max. If it was broad, group related items. The goal is a record someone (future Aleem) can scan in 30 seconds.

---

## Step 3 — Extract Decisions

Read back through the session and identify decisions that are worth logging. A decision is worth logging if:
- It represents a meaningful architectural, strategic, or workflow choice
- Something was explicitly chosen over an alternative
- A direction was set that will affect future work
- Something was decided *not* to do (and why matters)

Not worth logging:
- Trivial implementation details ("used a for-loop instead of map")
- Temporary workarounds with no lasting impact
- Things that are already obvious from the code

For each decision identified, format it as:
```
[YYYY-MM-DD] DECISION: [what was decided] | REASONING: [why] | CONTEXT: [session/feature/project it relates to]
```

Then ask the user: "I found [N] decision(s) worth logging — should I append them to decisions/log.md?"

If they say yes (or if they gave a blanket "yes" earlier), append to `decisions/log.md` using the Read + Edit tools. Never overwrite the file — always append after the last entry.

---

## Step 4 — Update Priorities

Look at `context/current-priorities.md` and ask: does what we did today change anything?

Good reasons to update:
- Something got built that was listed as "next to build" — move it to "What's Live"
- A bottleneck shifted — the constraint is now different
- The user explicitly said focus is moving somewhere new
- A new urgent item emerged that isn't captured yet

Bad reasons to update:
- Just because time passed
- Minor progress that doesn't change the strategic picture
- You want to be thorough — only update if something actually shifted

If an update is warranted, make the edit directly to `context/current-priorities.md`. Update the "Last updated" date to today. If nothing meaningful shifted, say so: "Priorities look current — no update needed."

---

## Step 5 — Offer Memory Updates

Scan the session for anything worth saving to persistent memory that isn't already captured:
- New preferences Aleem expressed
- Patterns in how he likes things done
- Project context that future conversations would benefit from knowing

If you find something, say: "One thing worth saving to memory: [what and why]." Then save it if he agrees.

---

## Output Format

End every closeout with a single clean block like this — no preamble, just the output:

```
Session closed.
Summary: [1-line]
Decisions logged: [N] (or "none")
Priorities updated: [yes / no — what changed] (or "no change")
Memory saved: [what, or "nothing new"]
```

Keep it crisp. The value is in the background work (logging, updating files), not in a long summary at the end.
