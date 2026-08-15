# Review Rubric — auditing an existing visual identity

Audit mode. The client has a brand book, a style guide, a website, or a folder of logo files.
The job is to say what is specified, what is merely asserted, and what is missing, then fix the
pieces worth fixing.

**This rubric is ours.** No validated visual-identity audit instrument exists in the corpus.
Present it as a structured judgment, not a published scoring model.

---

## The lens

Two questions run through every row:

1. **Could a designer who has never met this client execute it without asking a question?**
2. **Could a developer build it?**

Most brand books fail the second while passing the first, because they were made for a
presentation rather than for production. That gap is the most common finding in this audit and
it is a documented cause of non-adoption: print-first documents that lack actionable digital
guidance get ignored by product teams `[P]` [s181] [s190].

**Measure, do not impress.** A row scores on whether it specifies, not on how good it looks.

---

## The scorecard

Seven rows. Each is **Strong / Workable / Weak / Missing**. Lead the deliverable with the
table, then justify every row.

| # | Dimension | Strong means |
|---|---|---|
| 1 | **Direction** | Each visual decision traces to a personality trait or a position. Not style adjectives |
| 2 | **Logo** | A system: variants, clear space, minimum sizes, misuse. Not one file |
| 3 | **Colour** | Roles with usage rules, not a swatch row. Neutrals specified, not an afterthought |
| 4 | **Typography** | Pairing plus scale, weights, line heights, fallbacks, and licence status |
| 5 | **Space and layout** | Spacing scale, grid, breakpoints, radii, elevation |
| 6 | **Accessibility** | Computed contrast ratios for real pairs, against AA as the floor |
| 7 | **Implementability** | Tokens or values a developer can use directly, consistent with rows 3-5 |

**Scoring discipline.** Weak means present but unusable. Missing means absent. Do not soften.

**Calibration.** Rows 5, 6 and 7 fail most often, and row 6 fails almost universally: very few
brand books contain a single computed contrast ratio. Row 2 is frequently Weak rather than
Missing, because clients own a logo but not a logo system.

---

## Reading order

1. **Sample the live site, do not read the brand book.** Pull the actual hex values and the
   actually-loaded fonts. Divergence between the document and production is itself the finding,
   and it is common.
2. **Ask for vector logo files.** Raster-only is a hard constraint on everything downstream and
   clients frequently do not know which they have.
3. **Compute contrast for every real pair.** Body text on background, text on primary, text on
   CTA, placeholder text, disabled states, links. Use the formula in `method.md` Phase 8. Report
   numbers. Expect failures on the brand colour specifically.
4. **Check colour roles, not colour count.** Five colours with no usage rules is worse than
   three with them. Look for whether neutrals are specified at all.
5. **Check the type scale exists.** Two font names is not typography. Look for sizes, line
   heights, weights actually used, and fallbacks.
6. **Check licensing.** Web, desktop and app are licensed separately. A client can be
   non-compliant without knowing. Verify per typeface; never assume.
7. **Look for the invisible layer.** Spacing, grid, radii. Its absence explains most
   "consistent in the deck, inconsistent in production" complaints.
8. **Test one surface end to end.** Take their social avatar or an invoice and try to produce it
   from the document alone. Where you guess, the document has a hole.

---

## Then fix what is worth fixing

Rank by leverage:

- **Accessibility failures first.** They are objective, unarguable, and carry legal exposure in
  some markets. Fixing them also produces an immediate visible win.
- **Then implementability**, because a system nobody can build is not in use regardless of its
  other qualities.
- **Then the gaps** in colour roles and type scale, which cause the daily friction.
- **Logo replacement last, and only if diagnosed.** Redesign discards accumulated recognition,
  the most loyal customers react worst `[C]` [s29], and backlash risk is documented `[C]` [s11].
  Most "we need a new logo" requests are actually rows 3-7 failures wearing a logo complaint.

Supply corrected values, not descriptions of what corrected values would look like. An
accessible variant of the brand colour with its computed ratio is worth more than a paragraph
explaining that contrast matters.

**If it is a mood board rather than a specification**, say so. Mood boards are useful and
different. Offer to build the spec.

**If the system is fine and nobody follows it**, that is a governance finding, not a design
one. Employee response is the hinge for identity adoption `[C]` [s45] [s50]. A more beautiful
document will not fix it, and saying so is more useful than redesigning.
