# On-Page & Content - Section 12: Headings and Content Structure

*Structure is now a retrieval mechanism, not a formatting preference.*

**Bottom line:** Headings do three jobs: they let readers scan, they let Google understand
hierarchy, and they let AI engines lift a section out of your page and cite it. That third
job is new and it changes how you write. Sections that stand alone get retrieved. Sections
that depend on the paragraph above them do not.

---

## The hierarchy rules

**Exactly one H1**, containing the primary query, close to the title but not identical. Two
H1s is not a penalty, it is just confused signalling. `[practitioner]`

**H2 for each major sub-topic, H3 for divisions inside it.** Never skip levels for styling
reasons. If an H3 looks better, fix the CSS, do not change the tag.

**Headings describe content, they do not decorate it.** "Introduction" and "Overview" tell
nobody anything. "How crawl budget actually works" does.

## Phrase headings as questions

The highest-leverage change in this section.

Phrasing H2s and H3s as **direct user questions** improves the odds of being pulled into a
featured snippet or cited in an AI Overview, because it matches how queries are phrased.
`[practitioner]`

Compare:

- "Crawl Budget Considerations" describes a category
- "How much crawl budget does my site actually get?" matches a real query

You do not need every heading as a question. A useful mix is roughly a third, concentrated on
the sub-questions you found in People Also Ask during Section 6.

## Self-contained sections

This is the structural change 2026 demands.

AI engines retrieve at **passage level**, not page level. A section gets lifted out of your
page and evaluated on its own. If it opens with "As mentioned above, this means..." it is
useless out of context and will not be used.

The working spec:

- **Roughly 134 to 167 words per answer unit.** Long enough to answer, short enough to
  extract cleanly. `[practitioner]`
- **Define the entity in the first 40 to 60 words** of the section. Name the thing rather
  than referring to "it". `[practitioner]`
- **Bottom line up front.** Conclusion first, support after.
- **No backward dependencies.** Avoid "as we saw earlier", "this", "the above" as the opening
  move of a section.

Read any section of your page in isolation. If it makes sense alone, it can be retrieved. If
it cannot, it will not be.

## Formatting that earns its place

**Tables** for genuinely comparative data. They extract cleanly and are heavily favoured for
featured snippets. Do not use them for layout.

**Numbered lists** for sequences where order matters. **Bulleted lists** where it does not.
A list of three items that are really one idea should be a sentence.

**Bold** for the load-bearing phrase in a paragraph, not for emphasis generally. A paragraph
with six bold phrases has none.

**Short paragraphs.** Two to four sentences. Not because attention spans are short, but
because a wall of text hides the answer and both readers and extraction systems lose it.

## Scannability is not dumbing down

A well-structured page serves two readers at once: the person scanning for the one thing they
came for, and the person reading properly. Headings and formatting serve the first without
costing the second anything.

The test: read only your H2s in order. Do they tell the story of the page? If yes, a scanner
gets value in fifteen seconds. If they read as a list of vague nouns, the page has no spine.

## What not to do

- **Do not keyword-stuff headings.** "SEO Audit: The Best SEO Audit for SEO Audits" is a 2012
  tactic that now reads as spam to both readers and systems.
- **Do not use headings for visual size.** That is CSS.
- **Do not write a heading you do not answer** immediately underneath it.
- **Do not open sections with backward references** if you want them retrieved.

> **Why this matters:** structure used to be a readability nicety. Now it determines whether
> a passage can be lifted and cited at all. The same discipline serves both: say what the
> section is about, answer it directly, and make it stand alone.

## Do this now

1. **Take the page you optimized in Section 9.** Read only its H2s in order. Do they tell the
   story?
2. **Rewrite any heading that describes a category rather than answering something.**
3. **Convert roughly a third of your H2s into direct questions**, using the People Also Ask
   phrasing from Section 6.
4. **Check every section for backward dependencies.** Rewrite openings that start with "this",
   "as mentioned", or "the above".
5. **Check section length.** Split anything much over 200 words into two sections with their
   own headings.
6. **Confirm exactly one H1** and no skipped levels. Browser dev tools or any SEO extension
   will show you the outline.
7. **Repeat on two more important pages.**

## Capstone step

Three of your most important pages now have a heading structure that reads as a spine, a
third of headings phrased as real questions, and sections that survive being lifted out of
context.

## Key takeaways

- One H1, no skipped levels, headings that describe content rather than decorate it.
- Phrase roughly a third of headings as direct user questions to match how queries are
  actually worded.
- Write self-contained sections of about 134 to 167 words that define their subject in the
  first 40 to 60 words. Passage-level retrieval cannot use a section that depends on the one
  above it.
- Reading only your H2s should tell the story of the page. If it does not, the page has no
  spine.
