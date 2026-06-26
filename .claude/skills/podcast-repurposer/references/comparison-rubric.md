# Comparison Rubric

Used after all 4 templates run, to pick the winning method (or a hybrid). Score each
candidate set on the 5 dimensions below, 1-5. The point is **not** a leaderboard for its
own sake — it's to surface *which method's approach* Aleem should port into Min's production
system. A hybrid recommendation is allowed and often correct (e.g. "segments from #4,
captions from #3").

| Dimension | What a 5 looks like | What a 1 looks like |
|-----------|---------------------|---------------------|
| **Segment selection** | Every segment is self-contained, recruitment-relevant, and quotable. A good agent would screenshot it. | Mid-thought fragments, generic advice, or podcast housekeeping. |
| **Hook scroll-stop** | Hooks earn the first 3 seconds; specific, opinionated, varied across the 5. | Vague, samey, "Tips for agents," or buries the point. |
| **Voice / brand fidelity** | Sounds like Brenda (Mama Bear + Sage, grounded, candid). Zero absence-signal violations. | Em dashes, buzzwords, generic motivation, or off-archetype. |
| **Platform-nativeness** | IG / LinkedIn / FB genuinely differ; each reads native to its channel; self-contained. | One format pasted everywhere; leans on "listen to full episode." |
| **Effort-to-publish** | Red could ship with light edits. Clear, complete, correctly formatted. | Needs heavy rewriting; missing parts; off-spec. |

## Output of the comparison

After scoring, produce a short scorecard:

```
## Comparison — <episode>

| Template | Segments | Hooks | Voice | Platform | Effort | Total |
|----------|----------|-------|-------|----------|--------|-------|
| 01 social-media-skills | x | x | x | x | x | xx |
| 02 marketing-skills    | ...                                  |
| 03 client-content-creator | ...                               |
| 04 marketing-advisor   | ...                                  |

**Winner:** <template or hybrid>
**Why:** <2-4 sentences>
**Recommended hybrid (if any):** <which parts to take from which>
**For Min's production port:** <which method's prompt logic to encode in the OpenAI script>
```

Keep the judgment honest and specific. Cite an actual hook or caption from each set as
evidence, not just a number.
