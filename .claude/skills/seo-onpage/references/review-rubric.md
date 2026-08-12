# Review Mode

For when someone hands you existing on-page work - an audit from another agency, an
in-house checklist, a set of "optimized" pages - and asks whether it is any good.

Score, then decide whether to offer to redo it.

---

## The scorecard

Seven rows. Score each **Strong / Workable / Weak / Missing**.

| # | Dimension | Strong looks like | Weak looks like |
|---|---|---|---|
| 1 | **Intent match** | Each page's type matches what ranks for its query, and someone checked | Nobody looked at a SERP |
| 2 | **Prioritization** | Three ranked fixes with an expected effect | A list of every issue found, unordered |
| 3 | **Evidence** | Every claim points at a measurement, report or SERP | "Best practice suggests" |
| 4 | **Metadata written, not flagged** | Replacement titles and descriptions, paste-ready and within threshold | "Titles need improvement" |
| 5 | **Structure for retrieval** | One H1, no skipped levels, sections that stand alone, answer-first openings | Headings used as styling |
| 6 | **Internal linking** | Orphans named, opportunities listed, depth checked | Not mentioned at all |
| 7 | **Honesty about limits** | Says what could not be established and why | Presents inference as measurement |

Rows 2, 4 and 7 fail most often. Row 4 is the clearest tell of a tool export: a report that
lists which titles are too long without writing the replacements has done the countable
half and skipped the part being paid for.

Row 7 is the one worth checking hardest. A confident document with no stated limits was
usually produced without Search Console access by someone who did not say so.

---

## Reading order

1. Read the **summary or diagnosis first**. If it could be pasted onto another client's
   report unchanged, score row 2 Weak before reading further.
2. Count the findings. More than about ten and unranked means row 2 is Missing.
3. Pick three findings at random and try to trace each to evidence. That scores row 3.
4. Look for proposed replacements, not just flagged problems. Row 4.
5. Check whether internal linking appears at all. Row 6.
6. Search the document for "could not", "unknown", "without access to". Absence scores row
   7 Weak.
7. **Then spot-check two claims against the live pages.** An audit can be well-structured
   and wrong. `python scripts/onpage.py --url URL --primary-keyword "..."` takes a minute
   and settles it.

---

## Output

```markdown
## On-Page Review - <client or source>

**Verdict:** <one line - is this worth acting on, fixing, or replacing>

| Dimension | Score | Note |
|---|---|---|
| ... | Strong/Workable/Weak/Missing | ... |

### What it gets right
### What it gets wrong
<Separate factually wrong from merely thin. Those need different responses.>

### What it misses entirely
### What I would do instead
```

---

## The handoff rule

- **5 or more rows Weak or Missing** - say plainly that the underlying work needs redoing
  rather than patching, and offer build mode.
- **Rows 1 or 7 Weak** - the conclusions are not safe to act on even where the rest is
  competent. A well-executed audit of the wrong intent is still the wrong audit.
- **Mostly Strong with gaps** - patch the gaps. Do not redo work that is fine in order to
  put your own name on it.

## Pushback

Two things to say out loud when they apply, because a client usually will not.

**"The tool found 340 issues" is not a finding.** Screaming Frog and Semrush hand you
hundreds of items, most of them noise. Tools count things - broken links, redirect chains,
missing tags, page weight. They cannot tell you a page targets the wrong intent, that two
pages cannibalize, or that content is thin. An audit that is just a tool export has no
value, and the judgment is what was supposed to be bought.

**A previous audit being wrong is not automatically a reason to redo everything.** If rows
1 and 7 are Strong and the rest is thin, the diagnosis was sound and only the execution was
short. Say that. Selling a full rebuild on top of usable work is the thing that makes
clients stop trusting audits.
