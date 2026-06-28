# Learn-Anything Playbook (Tutor Engine)

This is the **generative** half of student-advisor. It does not depend on the NotebookLM corpus,
because the set of possible topics is infinite. Instead it gives you reliable **structures** to turn
any topic the user names into a clear learning path. Use your own knowledge to fill them, and when
the user needs *current* sources or papers, hand off (see "Handoffs" at the bottom) rather than
guessing at links.

The point of these templates is not to fill in a form mechanically. It is to give the learner the
thing a good tutor gives: a sense of the terrain, a route through it, and momentum. Lead with the
single most useful thing first, keep it concrete, and always end with a first action they can take
today.

## Pick the output by what they asked

| They asked for | Build this |
|---|---|
| "roadmap for X", "how do I learn X", "where do I start", "teach me X" | **Roadmap** (+ Resource map) |
| "best way to learn X", "what resources", "how should I study X" | **Resource map** (+ a short roadmap skeleton) |
| "history of X", "where did X come from" | **Background / history** |
| "what is X used for", "applications of X", "why does X matter" | **Applications** |
| "how does X relate to Y", "connect X to my field", "what should I explore next" | **Cross-field synthesis** |
| "give me an outline for X", "structure for learning X" | **Learning outline** |

Most real requests want two of these stitched together (usually a Roadmap + Resource map). Combine
freely. Keep the whole thing skimmable.

---

## Template: Roadmap (beginner to advanced)

The job here is to break a big, intimidating topic into ordered stages with a clear "you are done
with this stage when..." signal, so the learner always knows where they are and what is next.

```
# Learning Roadmap: [Topic]

**Goal:** [what "I know this" looks like for them — tie to why they're learning it]
**Prerequisites:** [what they should already know; "none" is a valid answer]
**Rough time:** [honest range, e.g. "8-12 weeks at ~5 hrs/week" — flag that it varies]

## Stage 1 — Foundations (Beginner)
- Core concepts: [3-6 must-know ideas, named]
- What to be able to do: [concrete skill / output]
- Checkpoint: you're ready to move on when you can [specific, testable thing]

## Stage 2 — Working Knowledge (Intermediate)
- Concepts: [...]
- Build something: [a small project / problem set that forces application]
- Checkpoint: [...]

## Stage 3 — Depth (Advanced)
- Concepts: [...]
- Real application: [a substantive project, paper reproduction, or open problem]
- Checkpoint: [...]

## Common traps
- [where learners stall or waste time on this specific topic]

## Start today
- [one concrete first action — a specific video, chapter, or 30-minute exercise]
```

Rules of thumb that make roadmaps good:
- **Three to five stages, never more.** More than that and it stops being a map and starts being a
  syllabus nobody finishes.
- **Every stage ends in a checkpoint they can self-test** (this is retrieval practice baked into the
  plan — see `learning-science.md`).
- **Put a build-something step in by the intermediate stage.** Passive consumption is where most
  self-learners plateau; producing something is what moves them.
- **Be honest about time.** Don't promise "learn X in a weekend" if it isn't true.

---

## Template: Resource map (best ways to learn + what to use)

Different resource *types* do different jobs. The mistake learners make is collecting ten tutorials
of the same type. Map the topic across the modalities instead, and tell them how to actually use
each one (watching a course is not the same as learning from it).

```
# How to Learn [Topic]

**Best primary path for this topic:** [course / book / project / docs — pick ONE to anchor on,
and say why this topic rewards that path]

| Resource type | Use it for | What to pick |
|---|---|---|
| Structured course | the backbone, ordered coverage | [type of course to look for] |
| Book / long-form | depth, reference, the "why" | [...] |
| Video / lectures | intuition, seeing it done | [...] |
| Docs / primary source | accuracy, the real API/spec/theorem | [...] |
| Practice / problems | actually learning it (not optional) | [...] |
| Community | unblocking, staying motivated | [where this topic's people gather] |

**How to use them well:**
- Anchor on one primary resource. Treat the rest as support, not parallel tracks.
- Alternate input and output: never more than ~20-30 min of consuming before you do/recall something.
- [topic-specific tip]
```

If they want *named, current, specific* resources (exact course names, the best 2026 book, live
links), that is a research task — hand off to **deep-research** (see Handoffs). Give them the
*shape* and the selection criteria here; let the research skill fetch the live picks.

---

## Template: Background / history (concise)

A little history makes a topic make sense — it shows why the ideas exist and what problem each one
solved. Keep it short. The learner asked for orientation, not a documentary.

```
# A Short History of [Topic]

**The problem it was born to solve:** [1-2 sentences]

## Key milestones
- [year/era] — [what happened, who, why it mattered] 
- [year/era] — [...]
- [year/era] — [...]
(4-7 milestones, each one line)

## How thinking shifted
- [the 1-2 big conceptual turning points — what people believed before vs after]

## Why this history helps you learn it
- [the through-line: how knowing the origin makes the modern version easier to grasp]
```

Keep claims you're confident about. If the user needs exact dates, attributions, or is writing
something that will be graded or published, flag that and hand off to **assignment-research** /
**deep-research** for sourced facts rather than stating dates you're unsure of.

---

## Template: Applications

Learners stay motivated when they can see where a topic actually lands. Show range — the obvious
uses and at least one they wouldn't expect.

```
# Where [Topic] Is Used

## In practice
- [domain]: [how it's used, concretely]
- [domain]: [...]
(spread across different fields — don't list five flavors of the same use)

## The non-obvious one
- [a surprising or cross-disciplinary application]

## What this means for you
- [tie at least one application to the learner's stated field/goal if known]
```

---

## Template: Cross-field synthesis ("what should I explore next")

This is the highest-leverage template for a curious student, and it's what turns a list of subjects
into actual understanding. Show how the topic connects outward, then point at the most valuable next
thing to learn given where they are.

```
# [Topic], Connected

## Adjacent fields and the bridge concept
- [Field A] — connects via [the shared idea/tool]
- [Field B] — connects via [...]

## The transferable core
- [the underlying principle in this topic that shows up everywhere — name it plainly]

## What to explore next (ranked)
1. [next topic] — because [it builds directly on what they now know / opens the most doors]
2. [next topic] — because [...]
3. [a wildcard worth their curiosity]
```

When recommending "what to explore next," weigh it against the learner's actual goal and current
level — the best next topic for a beginner is rarely the most advanced one. If they have a career
goal, cross-reference `career-paths-playbook.md` so "what to explore next" points somewhere useful.

---

## Template: Learning outline

When they just want a clean structure to organize their own study (or notes), give the skeleton:

```
# [Topic] — Study Outline

1. [Major area]
   - [sub-topic]
   - [sub-topic]
2. [Major area]
   - [...]
(Ordered so each section depends only on earlier ones)

Suggested study order: [if different from the outline order, say so and why]
```

---

## Handoffs (don't reinvent search)

The tutor engine gives **structure and judgment**, not a live web crawl. When the request needs
current, specific, or citable material, route it:

- **`deep-research` skill** — for current, named resources, courses, tools, or a deep dive on a
  topic with live web search. Use when the user says "find me the best resources/courses on X,"
  "what's the latest on X," or wants real links.
- **`assignment-research` skill** — for academic/university work: peer-reviewed sources, literature
  reviews, citations, and assignment-shaped outlines saved to Google Docs. Use when the topic is
  for a course, paper, or anything that will be graded.

State the handoff plainly ("For the actual current course links, I'll hand this to deep-research —
want me to?") rather than fabricating specific URLs, dates, or resource names you can't verify.

## Offer the export

For a substantial roadmap or learning plan, offer to save it to Google Docs (see the SKILL.md
"Google Docs Output" section) so the learner has a durable plan to work against.
