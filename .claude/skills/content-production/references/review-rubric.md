# Review rubric — auditing a piece of content

Load this in audit mode, alongside the format's entry in
`content-advisor/references/format-specs/`.

**Calibration: most real client content scores Weak on rows 2, 4 and 6.** Specificity, proof
and a single clear action are the three that get lost between the brief and the draft. A piece
scoring Strong across the board is rare enough that you should re-read before believing it.

---

| # | Row | Strong | Workable | Weak | Missing |
|---|---|---|---|---|---|
| 1 | **Job** | The piece has one job and every section serves it | The job is inferable | It summarises a topic | It is a collection of things about a subject |
| 2 | **Specificity** | Claims are concrete, named and checkable | Some concrete detail, some generality | Category-generic — it would read the same for a competitor | Nothing in it is specific to this business |
| 3 | **Opening** | Earns the next line by the format's own test | Adequate but slow | Warm-up throat-clearing before the point | Starts with context nobody asked for |
| 4 | **Proof** | Every load-bearing claim traces to something real | Claims are supported but thinly | "Studies show", unattributed numbers | Invented statistics, quotes or results |
| 5 | **Voice** | Indistinguishable from the client's own best writing | Broadly on-voice | Generic marketing register | Sounds like an agency, or like AI |
| 6 | **The one action** | One clear action, positioned where the reader is ready | One action, awkwardly placed | Several competing actions | No action, or "learn more" |
| 7 | **Format fit** | Matches the spec's structure, length and platform mechanics | Minor deviations | Written as generic content and poured into the format | Wrong format for the message |

---

## The gates

Run these first. A failure here is the headline finding, ahead of any row score.

**The swap test.** Replace the client's name with a competitor's. If the piece still reads as
true, it is category content and row 2 is Weak regardless of how well it is written. This is
the single most common failure in client content and the one clients are least able to see.

**The read-aloud test.** Read the opening and one middle paragraph out loud. Anything you would
not say to a person fails. Machine-written cadence survives silent reading and does not survive
this.

**The proof test.** Take the three biggest claims and ask where each number came from. If the
answer is "it is a well-known figure", it is folklore — check it against
`content-advisor/references/what-not-to-do.md` before it ships.

---

## What to hand back

**Do not list everything that could be better.** Fourteen findings is not an audit.

1. **The score table**, all seven rows.
2. **The three highest-leverage rewrites**, done rather than described — the actual opening,
   the actual claim rewritten around real proof, the actual single action. A rewritten
   paragraph is worth more than a paragraph explaining what is wrong with it.
3. **One thing to cut.** Nearly every piece has a section that exists because someone thought
   it should. Naming it is usually the most useful line in the audit.

If the piece is in a format another skill owns, **route the rewrite** rather than doing it
here: articles to `blog-writer`, conversion pages to `copy-conversion`, carousels to `carousel`.
