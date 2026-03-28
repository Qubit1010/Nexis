---
name: assignment-research
description: "Research university assignment topics, find academic sources, synthesize findings, and create structured research notes + outlines saved to Google Docs. Use this skill whenever the user mentions university assignments, homework, coursework, academic research, finding sources, literature reviews, or needs help structuring an assignment response. Triggers on: 'research assignment', 'assignment on [topic]', 'help with my assignment', 'find sources for [topic]', 'university assignment', 'research [topic] for class', 'help me write about [topic] for university', 'I have an assignment on...', 'need sources for my [course] paper'."
argument-hint: "[assignment topic or requirements]"
---

# Assignment Research Assistant

Research university assignment topics, find quality academic sources, synthesize findings into structured notes, and create outlines -- all saved to Google Docs. Built for a 6th semester BSAI student who needs thorough research done fast.

## When to Trigger

Activate when the user:
- Asks to research a topic for a university assignment or course
- Needs academic sources, papers, or references on a topic
- Wants help structuring or outlining an assignment response
- Says "assignment on [topic]", "research [topic] for my class", "find sources for..."
- Mentions homework, coursework, lab reports, or semester projects
- Needs a literature review or technical survey on an academic topic

## Context Loading

Before starting, read `context/me.md` for university details (BSAI, 6th semester, Iqra University). This helps calibrate the depth and complexity of research to an undergraduate AI student level.

## Workflow

### Step 1: Parse Assignment Requirements

Extract from the user's input (from `$ARGUMENTS` or conversation):

- **Topic** (required) -- the subject to research
- **Assignment type** (required, auto-detect if not stated):
  - `theory-paper` -- literature reviews, surveys, concept analysis
  - `programming-project` -- implementation-focused assignments
  - `written-report` -- essays, case studies, analytical reports
  - `math-stats` -- proofs, derivations, problem sets, statistical analysis
- **Specific questions** -- exact prompts from the assignment brief
- **Course name** (optional) -- helps tailor depth and focus area
- **Word count / page count** (optional)
- **Deadline** (optional)

**Auto-detection heuristics:** "implement", "build", "code", "develop" = `programming-project`. "analyze", "discuss", "compare", "evaluate", "essay" = `written-report`. "prove", "derive", "calculate", "solve" = `math-stats`. "survey", "review", "literature", "state of the art" = `theory-paper`.

If the type is genuinely ambiguous, ask: "Is this more of a written report or a programming project?" Don't ask if the context makes it obvious.

If the topic is vague (e.g., "machine learning"), ask: "What specifically does the assignment ask you to do? Can you share the assignment prompt?"

### Step 2: Research Phase

Use WebSearch with targeted queries to find academic-quality sources. Run 3-5 searches in parallel:

1. **Academic papers:** `site:arxiv.org [topic] [key terms]` or `[topic] research paper filetype:pdf`
2. **Scholar results:** `[topic] [specific aspect] site:scholar.google.com` or `[topic] survey 2024 2025`
3. **Course materials:** `[topic] course notes site:edu` or `[topic] lecture notes [university]`
4. **Documentation** (for programming topics): `[topic] documentation` or `[library/framework] official guide`
5. **Topic-specific:** Adapt to the field -- `site:ieee.org` for engineering, `site:neurips.cc` or `site:openreview.net` for ML/AI, `site:mathworld.wolfram.com` for math

For each promising result, use WebFetch to pull the page content. Extract:
- Title and authors (if paper)
- Key claims, findings, or techniques
- URL and publication date
- Relevance to the specific assignment questions

**Source quality hierarchy** (prioritize top, use bottom only as fallback):
1. Peer-reviewed papers (arxiv, IEEE, ACM, NeurIPS, ICML)
2. University course notes and textbooks
3. Official documentation and technical specifications
4. Established technical blogs (Distill.pub, Papers With Code, official framework blogs)
5. General tutorials and blog posts (only if nothing better exists -- flag these as non-academic)

**Cap at 8-12 sources.** Quality over quantity. If a topic is niche and sources are scarce, note this explicitly.

### Step 3: Synthesis Phase

From the fetched sources, synthesize:

- **5-8 key concepts** with concise explanations -- these form the backbone of the assignment
- **Main arguments or approaches** in the literature -- where do researchers agree/disagree?
- **Contradictions or open debates** -- valuable for demonstrating critical thinking
- **3-5 direct quotes** worth citing, with full attribution (author, year, page if available)
- **For programming projects:** recommended libraries, architectures, algorithms with trade-offs
- **For math/stats:** key theorems, formulas, and their intuitive explanations

Organize findings thematically, not by source. Group related ideas together.

### Step 4: Structure Phase

Build an outline using the appropriate template below. Fill in the outline with specific content from the research -- concrete findings, actual paper names, real data points. No generic placeholder text.

---

#### Template A: Theory Paper / Literature Review (`theory-paper`)

```
# [Topic] -- Research Notes

## Overview
- Problem definition / research question
- Why this matters (1-2 sentences of context)
- Scope of this review

## Key Concepts
- Concept 1: explanation + [Source]
- Concept 2: explanation + [Source]
- (5-8 concepts)

## Literature Review
### [Theme/Approach 1]
- Summary of papers taking this approach
- Key findings and contributions
### [Theme/Approach 2]
- Summary of papers taking this approach
- Key findings and contributions
(Group by theme, not by paper)

## Comparative Analysis
| Paper/Approach | Method | Key Finding | Limitation |
|---|---|---|---|
| ... | ... | ... | ... |

## Discussion Points
- Open questions in the field
- Gaps in the literature
- Potential future directions

## Suggested Assignment Structure
- How to organize the final paper based on this research

## Sources
- [1] Author (Year). Title. Venue. URL
- [2] ...
```

#### Template B: Programming Project (`programming-project`)

```
# [Project Title] -- Technical Research

## Problem Statement
- What needs to be built and why
- Input/output specifications
- Constraints and requirements

## Technical Approach
### Architecture Overview
- High-level system design
- Component breakdown
### Key Algorithms / Techniques
- Algorithm 1: how it works, time/space complexity, when to use
- Algorithm 2: ...
### Libraries & Tools
| Library | Purpose | Why This One |
|---|---|---|
| ... | ... | ... |

## Implementation Plan
1. Step 1: what to build first and why
2. Step 2: ...
(Ordered by dependency -- what must exist before what)

## Potential Challenges
- Known pitfalls and edge cases
- Common mistakes to avoid
- Performance considerations

## Code References
- Links to documentation, example implementations, tutorials
- Relevant GitHub repos or code samples

## Sources
- [1] ...
```

#### Template C: Written Report / Essay (`written-report`)

```
# [Topic] -- Research Notes & Outline

## Thesis / Central Argument
- 1-2 sentence thesis statement based on research findings

## Background & Context
- Key background the reader needs to understand the topic
- Historical context or foundational concepts

## Key Arguments
### Argument 1: [Claim]
- Supporting evidence + [Source]
- Counter-argument (if any) + [Source]
### Argument 2: [Claim]
- Supporting evidence + [Source]
- Counter-argument (if any) + [Source]

## Evidence Summary
| Claim | Evidence | Source |
|---|---|---|
| ... | ... | ... |

## Suggested Assignment Structure
- Introduction: hook, context, thesis
- Body section 1: [topic]
- Body section 2: [topic]
- Body section 3: [topic]
- Conclusion: restate thesis, implications, call to action or future outlook

## Key Quotes
- "[Quote]" -- Author (Year)
- "[Quote]" -- Author (Year)
(3-5 quotable passages with full citations)

## Sources
- [1] ...
```

#### Template D: Math / Stats (`math-stats`)

```
# [Topic] -- Concept Notes & Solution Approach

## Concept Overview
- What this topic is about
- Where it fits in the curriculum (prerequisites, what it leads to)

## Key Definitions & Theorems
- **Definition 1:** Formal statement + plain English explanation
- **Theorem 1:** Statement + intuition for why it holds
- (Cover all definitions/theorems relevant to the assignment)

## Worked Examples
### Example 1: [Description]
- Step-by-step solution with explanation of each step
### Example 2: [Description]
- Step-by-step solution (different technique or edge case)

## Solution Approach for Assignment
- Step-by-step strategy for the specific problems
- Which theorems/techniques apply to which parts
- How to verify your answers

## Common Mistakes to Avoid
- Typical errors students make on this topic
- Edge cases that trip people up

## Practice Resources
- Links to problem sets, video explanations, textbook chapters
- Similar solved problems for reference

## Sources
- [1] ...
```

---

### Step 5: Output Phase

1. **Present the research notes + outline** in the conversation for the user to review
2. **Ask:** "Save to Google Docs?" (default: yes)
3. If yes, build JSON matching the document schema (see `references/research-schema.json`) and pipe to the creation script:

```bash
echo '<json_content>' | python ".claude/skills/assignment-research/scripts/create_research_doc.py"
```

4. **Return the Google Doc URL** to the user
5. **Offer follow-ups:** "Want me to expand any section, find more sources on a specific point, or adjust the outline?"

**If Google Doc creation fails:** Output the full research as markdown in the conversation. Mention the error briefly and suggest copy-pasting into a doc manually.

## Important Boundaries

- **Math/stats assignments:** Explain concepts, show worked examples of *similar* problems, and outline the approach. Don't solve the actual assignment problems -- that defeats the purpose. Help Aleem understand, not bypass.
- **Programming projects:** Provide architecture, algorithm choices, library recommendations, and pseudocode. Don't write the actual implementation code -- the assignment requires him to code it.
- **Written reports:** Provide research, evidence, quotes, and a strong outline. Don't write the full essay -- the assignment requires his own analysis and writing.
- **Always cite sources.** Every claim should trace back to a source. Academic integrity matters.

## Edge Cases

- **No good academic sources found:** Fall back to quality technical content (official docs, established blogs). Explicitly flag: "Note: I couldn't find peer-reviewed sources for this specific angle. The sources below are from [documentation/technical blogs] rather than academic papers."
- **Topic outside BSAI curriculum:** Still research it, but note the scope may be broader than expected. Ask if narrowing is needed.
- **Multiple assignment questions:** Structure the outline to address each question as a section, with shared research at the top.
- **Group project:** Ask which part the user is responsible for and focus research on that section only.
