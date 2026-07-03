# Test post — "The Core Architecture of Claude Code" (one detailed prompt per slide)

Fully filled set for testing the Gem. Build the Gem from `gem.md` first (attach the 4 Knowledge
images). Then paste the blocks below **one at a time**, in order, waiting for each image. Handle is
`@aleem_uh`. Optionally attach the architecture infographic before slide 2 to feature it in the
taped frame.

---

## STEP 0 — CONTEXT (paste first, no image)

```
We are building an 8-slide Instagram carousel in the template (match the Knowledge reference images). I will send ONE detailed prompt per slide; generate ONE 1080x1350 image per prompt. Do not generate anything yet, do not tile slides into one image, do not build a slide deck.

Topic: The core architecture of Claude Code, and why treating it like a chatbot burns your repo and context window. The 3-part mental model (Workflow, Agent, Tools) plus the loop, compaction, memory, subagents, and safety.
Source / notes (keep every slide consistent with this): Claude Code is an agentic harness around the model. Workflows are plans you approve; the Agent is the model reasoning; Tools read/write files, run shell, search code, call APIs. The agentic loop is a ReAct cycle: gather context, take action, verify, repeat. A five-layer compaction pipeline (Budget, Snip, Microcompact, Context Collapse, Auto-compact) fights context rot in a window up to 1M tokens. Extensibility by context cost: CLAUDE.md (auto-loaded), Hooks (zero), Skills (low), Plugins (medium), MCP servers (high). Subagents (Explore, Plan) run in isolated windows and return summaries. Safety is deny-first: checkpoints snapshot files before edits (double Escape or /rewind), permission modes (Plan, Default, acceptEdits, bypassPermissions). Production habit: externalize state into a DECISIONS.md so compaction cannot forget.
Identity: header always reads "ALEEM · NEXUSPOINT"; handle is "@aleem_uh".

Reply with a one-line confirmation and a numbered slide plan, then wait for my per-slide prompts.
```

## STEP 1 — COVER

```
Slide 1 of 8 — COVER. Generate ONE 1080x1350 image only.
Style: saturated blue vertical gradient background (deep blue). A photoreal dark stone monolith engraved with faint circuit-line patterns, bleeding off the top-right, holding a 3D terracotta star/spark object (the symbolic "spark" of the model).
Kicker (small uppercase, letter-spaced): "ARCHITECTURAL DEEP DIVE"
Headline (giant condensed heavy white sans, tight leading, soft drop shadow): "STOP TREATING CLAUDE CODE LIKE A CHATBOT."
Subtitle (italic serif, white): "The 3-part mental model for agentic development on production repos."
No header, no footer, no page number. No emojis, no em dashes. One image only.
```

## STEP 2 — BODY (Point 01)

```
Slide 02 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 02 / 08"
Pill (black ticket pill with notched ends, white uppercase): "POINT 01 / HARNESS"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "It's a harness, not a chat UI."
Body (cream, key phrases bold): "Make three things explicit before anything runs: the **Workflow** you approve, the **Agent** that reasons, the **Tools** that touch files, shell, and code."
Visual (taped polaroid frame: white border, two tape strips, slight rotation): render a clean diagram of three stacked labeled blocks, "Workflow", "Agent", "Tools".
Footer: "02 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 3 — BODY (Point 02)

```
Slide 03 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 03 / 08"
Pill (black ticket pill, white uppercase): "POINT 02 / THE LOOP"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "Gather. Act. Verify. Repeat."
Body (cream, key phrases bold): "The agentic loop is a **ReAct cycle**. Skip the **verify step** and you ship green-looking diffs that break at runtime."
Visual (taped polaroid frame): render a clean circular loop diagram, "Gather Context -> Take Action -> Verify Results", arrows forming a cycle.
Footer: "03 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 4 — BODY (Point 03)

```
Slide 04 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 04 / 08"
Pill (black ticket pill, white uppercase): "POINT 03 / COMPACTION"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "Five layers fight context rot."
Body (cream, key phrases bold): "Before every call: **Budget, Snip, Microcompact, Collapse, Auto-compact**. The window, up to 1M tokens, is the real constraint."
Visual (taped polaroid frame): render a clean vertical stack of five labeled layers (Budget, Snip, Microcompact, Context Collapse, Auto-compact).
Footer: "04 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 5 — BODY (Point 04)

```
Slide 05 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 05 / 08"
Pill (black ticket pill, white uppercase): "POINT 04 / MEMORY"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "CLAUDE.md is standing memory."
Body (cream, key phrases bold): "Extend Claude by **context cost**: Hooks (zero), Skills (low), Plugins (medium), MCP servers (high). CLAUDE.md auto-loads your conventions."
Visual (taped polaroid frame): render a clean horizontal cost arrow from "LOW" to "HIGH" with Hooks, Skills, Plugins, MCP Servers placed along it.
Footer: "05 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 6 — BODY (Point 05)

```
Slide 06 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 06 / 08"
Pill (black ticket pill, white uppercase): "POINT 05 / SUBAGENTS"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "Isolate work to protect context."
Body (cream, key phrases bold): "**Explore** and **Plan** subagents run in separate windows, sometimes separate git worktrees, and return only a summary. Main context stays clean."
Visual (taped polaroid frame): render a clean diagram, two subagents "Explore" and "Plan" feeding summaries into a single "Main Context" box.
Footer: "06 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 7 — BODY (Point 06)

```
Slide 07 of 8 — BODY. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background, subtle grain and vignette.
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 07 / 08"
Pill (black ticket pill, white uppercase): "POINT 06 / SAFETY"
Headline (heavy rounded sans, cream and ink words mixed, ends in a period): "Deny-first, with checkpoints."
Body (cream, key phrases bold): "Snapshots before every edit (**double Escape** or **/rewind** to undo). Scale autonomy with permission modes: Plan, Default, acceptEdits, bypassPermissions."
Visual (taped polaroid frame): render a clean shield-and-checkpoint icon with four small permission-mode chips (Plan, Default, acceptEdits, bypassPermissions).
Footer: "07 / 08" left, "SWIPE ->" right.
No emojis, no em dashes. One image only.
```

## STEP 8 — CTA

```
Slide 08 of 8 — CTA. Generate ONE 1080x1350 image only.
Style: terracotta paper-texture background (same as body slides).
Header (monospace, uppercase, letter-spaced): "JUN ©2026 · ALEEM · NEXUSPOINT · 08 / 08"
Pill (black ticket pill, white uppercase): "BUILD YOUR NEXT PROJECT"
Stacked statement (huge, ONE word per line, alternating cream/ink, each word ends with a period): "plan." "verify." "externalize."
Summary line (cream): "Write a DECISIONS.md so compaction never forgets the truth. Follow @aleem_uh for more AI engineering breakdowns."
Footer: "08 / 08" left.
No emojis, no em dashes. One image only.
```

---

Fix any slide with: `regenerate slide N, same style, change <X>`.
