# SM Schedule — column map & vocab

The Weekly Posting Schedule sheet: `13RiOJpxWly5BztZdpLhGK5kT_Unna8Lnc-8GboApJ74`, tab **SM Schedule**.
`scripts/schedule.py` resolves all columns **by header name** (aliases below), never by position —
the sheet has hidden columns and gets reorganized.

## Fields the skill uses

| Field | Header aliases | Used for |
|---|---|---|
| topic | Topic / Idea, Topic | The post subject; goes to research + generation |
| description | Post Description | Angle/framing; goes to research + generation |
| reference | Reference | Optional URL; seeds research when present |
| platform | Platform | `All` = LinkedIn + Instagram; else just the named one |
| post_type | Post Type | `Reel` rows are skipped (reel-creator's job) |
| format | Format | Text Post / Carousel / Article / Newsletter |
| content_mode | Content Mode | News/Analysis, Opinion/POV, Personal Story, Tutorial/How-to |
| pillars | Pillars | Comma/newline-separated. Parsed across BOTH axes below |
| design_template | Design Template | Names BOTH image templates, e.g. `LinkedIn Infographic — Template 9,\nInstagram-Template-6` |
| final_post | Final Video/Post | OUTPUT: the generated Google Doc URL goes here |
| status | Status | Set to `Draft` after the Doc link is written |

Ignored per Aleem: Media Type, Content Theme, Column 1-3, and the misc trailing columns.

## Content Mode -> canonical key
(keys match the content-engine dashboard's MODE_INSTRUCTIONS)

| Cell value | Key |
|---|---|
| News/Analysis | news |
| Opinion/POV | opinion |
| Personal Story | story |
| Tutorial/How-to | tutorial |

Mode -> default **ingredients** when the Pillars cell names none (mirrors the dashboard):
news -> practical_stakes + content_specific · opinion -> strong_pov + taste_judgment ·
story -> lived_experience + identity_voice · tutorial -> practical_stakes + content_specific

These are ingredient defaults, not topical-pillar defaults. There is no sensible default
for what a post is *about*; step 1b decides that from the topic.

## Pillars cell -> canonical keys (two axes)

`schedule.py` parses the one cell against both maps and returns them separately as
`ingredients` and `topical_pillars`, with anything matching neither in
`pillars_unrecognized`. A typo surfaces instead of silently becoming an empty list.

### Axis 1 - the 7 Unswappable ingredients (`INGREDIENT_KEYS`)

Qualities every piece must contain, defined in `agency/personal-brand-voice.md`. A
per-piece craft check: every post needs at least two, so there is no mix to balance.

| Cell label | Key |
|---|---|
| Lived Exp / Lived Exp. / Lived Experience | lived_experience |
| Strong POV | strong_pov |
| Cross-domain | cross_domain |
| Taste & Judgment | taste_judgment |
| Identity | identity_voice |
| Practical Stakes | practical_stakes |
| Content Specific | content_specific |

### Axis 2 - the 4 topical pillars (`TOPICAL_PILLAR_KEYS`)

What a piece is *about*, defined in `agency/personal-brand-pillars.md`. **This is the
axis the target mix in `agency/personal-brand-content-engine.md` section 5 is measured
in, and it is what the Pillars column should hold going forward.**

| Cell label | Key | Target share |
|---|---|---|
| AI & Automation / AI and Automation | ai_automation | 40% |
| Founder Journey | founder_journey | 30% |
| Tech Insights | tech_insights | 20% |
| Young Builder / Learning in Public | young_builder | 10% |

The two Conversion-intent pillars, Founder Journey and Young Builder, sit at roughly zero
across all 199 rows. That gap is the reason the column exists.

The seven keys above are the Unswappable **ingredients** (qualities every piece must contain),
defined in `agency/personal-brand-voice.md`. They are **not** the 4 topical pillars in
`agency/personal-brand-pillars.md`, which are what a piece is *about* and what the engine's
target mix is measured in. Two axes, one column name. See the note at the end of this file.

## Design Template cell -> template folders

`schedule.py` parses out both numbers and validates them against the folders actually
on disk (globbed at import, not a hardcoded list — templates get onboarded often):

- **LinkedIn** -> `.claude/skills/linkedin-infographics/references/LinkedIn-Template-<N>/`
- **Instagram** -> `.claude/skills/carousel/references/Instagram-Template-<N>/`

Numbering is sparse. If a row names a number with no folder, `schedule.py` returns it in
`templates.errors` — stop and ask Aleem which template to use instead. Never substitute silently.

## Write-back

```
python scripts/schedule.py write --row <N> --doc-url <URL> [--status Draft] \
    [--pillars "Founder Journey"] [--content-mode "Personal Story"]
```

Writes the Doc URL into Final Video/Post, sets Status, and optionally fills Pillars and
Content Mode. Both optional values are normalized and validated **before** any cell is
touched, so an unrecognized label fails the whole write rather than leaving a row with a
Doc URL and a rejected classification.

`--pillars` takes the topical axis and accepts keys or labels (`founder journey`,
`Founder Journey`, `AI and Automation`). Passing an **ingredient** label there is a hard
error with an explanation, not a silent write: a cell filled with the wrong axis looks
filled while leaving the mix unmeasurable, which is the failure mode this whole split
exists to prevent.

## History — the `Pillars` column used to encode only one axis

Until 2026-08-28, `PILLAR_KEYS` in `schedule.py` mapped the `Pillars` cell to the 7
ingredients only, while `agency/personal-brand-content-engine.md` section 5 expressed its
target mix in the 4 topical pillars. One column name, two axes, no way to tell them apart.

Nothing was broken in practice, because the column was empty on all 199 rows. But filling
it with ingredient labels would have left the mix unmeasurable in the terms the engine
uses, and step 1b now asks for that column to be filled.

**Resolved** by splitting the map in two (`INGREDIENT_KEYS` + `TOPICAL_PILLAR_KEYS`),
returning `ingredients` and `topical_pillars` separately on read, and making `--pillars`
on write accept only the topical axis. The change is additive: a cell already carrying
ingredient labels still parses, it just lands in `ingredients` where it belongs.
