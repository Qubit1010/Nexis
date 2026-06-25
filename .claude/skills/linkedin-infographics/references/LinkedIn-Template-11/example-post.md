# Test post — "How I Use Claude Code in My Daily Workflow" (one filled single-image prompt)

Fully filled example for testing the Gem. Build the Gem from `gem.md` first (attach both Knowledge
images). Then paste the single block below and wait for the one infographic image.

This produces ONE 1080x1350 infographic, not a carousel. Fix it with
`regenerate, same layout, change [X]`.

---

```
Generate ONE complete LinkedIn infographic as a single 1080x1350 image (4:5 portrait), matching the Knowledge reference exactly. Do NOT make a carousel, a slide deck, or multiple images. One image only.

TITLE (large bold display, left-aligned):
Full title: "How I Use Claude Code in My Daily Workflow"
Pill phrase: wrap "Claude Code" in an inline coral rounded pill (bg #F07560, white text). All other words bold black (#1A1A1A).
SUBTITLE (italic, grey, in parentheses): "(and why it's the tool I open before everything else)"

BRAND: place the NexusPoint logo (from Knowledge) ~80-100px tall at the top-right of the title block.

PAGE BACKGROUND: #FAF6F0 (warm off-white) throughout.

---

DEFINITION ROW (3 equal boxes, full canvas width, thin amber left-border #E8A020 on each):

BOX 1:
ICON: terminal/command prompt icon
LABEL: "Claude Code ="
DEFINITION: "A CLI tool that brings Claude into your terminal. It reads your files, writes and runs code, and executes commands on your machine."

BOX 2:
ICON: plug/connector icon
LABEL: "MCP Servers ="
DEFINITION: "Connected tools that extend Claude Code. Hook it into Gmail, Drive, GitHub, Sheets, and more — all from the terminal."

BOX 3:
ICON: bookmark/document icon
LABEL: "Skills ="
DEFINITION: "Custom instruction files that teach Claude Code your exact workflows. Build a skill once, reuse it forever with a slash command."

---

LEFT COLUMN (~65% width):

SECTION HEADER (dark navy #1C2B3A, white text): "5 Ways I Use Claude Code"

ITEM 1:
BADGE: "1" (orange circle #E85D1A, white)
TITLE: "Build & Ship Features"
DESCRIPTION: "Describe what you want in plain English. Claude Code writes, tests, and runs it — reading your existing files for context."
TAGLINE (italic, orange #E85D1A): "Plain English in. Working code out."
ILLUSTRATION: hand-drawn code editor window with flowing text lines and a terminal output panel below

ITEM 2:
BADGE: "2"
TITLE: "Automate Repetitive Scripts"
DESCRIPTION: "Python or JS scripts written in seconds. File operations, API calls, data transforms — described once, built and run immediately."
TAGLINE: "Manual work, automated."
ILLUSTRATION: hand-drawn script file icon with an arrow looping back to a checkmark (recurring automation)

ITEM 3:
BADGE: "3"
TITLE: "Debug Without Googling"
DESCRIPTION: "Paste any error. Claude Code reads the surrounding file for context, explains the root cause, and writes the fix."
TAGLINE: "Context-aware diagnosis, every time."
ILLUSTRATION: hand-drawn bug icon with a magnifying glass and an X through it, error message lines beside

ITEM 4:
BADGE: "4"
TITLE: "Manage Projects by Chat"
DESCRIPTION: "Create files, rename folders, update configs, run git commands — all by describing what you want in plain English."
TAGLINE: "Your terminal, but smarter."
ILLUSTRATION: hand-drawn terminal window with a chat bubble input and a file tree on the right

ITEM 5:
BADGE: "5"
TITLE: "Research & Implement Together"
DESCRIPTION: "Web search a topic, synthesize the findings, then implement — without losing context or switching tools."
TAGLINE: "Idea to working code, no context switch."
ILLUSTRATION: hand-drawn browser window with research notes, arrow pointing to a code file

---

RIGHT COLUMN (~35% width):

SIDEBAR HEADER (dark navy #1C2B3A, white text, gold star icon left): "Best Practices for Claude Code"

CARD 1:
ICON: document/file icon
TITLE: "Always Have a CLAUDE.md"
DESCRIPTION: "Set your project rules, preferred stack, and context once in CLAUDE.md. Claude Code reads it at the start of every session and applies it automatically."

CARD 2:
ICON: lightning bolt icon
TITLE: "Build Skills for Repeat Workflows"
DESCRIPTION: "Any task you do twice is a skill candidate. Write a SKILL.md once, and you can trigger the entire workflow with a single slash command."

CARD 3:
ICON: checklist icon
TITLE: "Ask for a Plan First"
DESCRIPTION: "Before any complex task, say 'plan this first.' Review the steps before saying 'proceed.' Fewer surprises, easier to course-correct."

CARD 4:
ICON: brain/network icon
TITLE: "Keep Context Files Fresh"
DESCRIPTION: "The more Claude Code knows about your project structure, goals, and decisions, the better every output gets. Update your context files regularly."

---

FOOTER BAR (full width, warm amber-beige #F5E8D0, rounded pill/banner shape):
QUOTE: "heart icon — Claude Code is a force multiplier. Once you wire it into your stack, you can't go back."
CTA: "Follow for more AI and automation strategies"

---

RULES: warm off-white page (#FAF6F0); two-column layout — left ~65%, right ~35%; definition row and footer bar span full width; section headers dark navy (#1C2B3A) with white text; orange badges (#E85D1A) with white numbers; italic taglines in orange (#E85D1A); sidebar icons in orange (#E85D1A); sketch illustrations hand-drawn outline style (thin dark lines, no fill); thin horizontal dividers between all items and cards; all text legible at 1080x1350; no emojis in body; no em dashes.
One image only.
```

---

Fix any issue with: `regenerate, same layout, change [X]` (re-renders the whole infographic).
