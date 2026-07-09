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
| pillars | Pillars | Comma/newline-separated pillar labels |
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

Mode -> default pillars when the Pillars cell is blank (mirrors the dashboard):
news -> practical_stakes + content_specific · opinion -> strong_pov + taste_judgment ·
story -> lived_experience + identity_voice · tutorial -> practical_stakes + content_specific

## Pillars cell -> canonical keys

| Cell label | Key |
|---|---|
| Lived Exp / Lived Exp. / Lived Experience | lived_experience |
| Strong POV | strong_pov |
| Cross-domain | cross_domain |
| Taste & Judgment | taste_judgment |
| Identity | identity_voice |
| Practical Stakes | practical_stakes |
| Content Specific | content_specific |

Pillar definitions (what each enforces in the writing) live in
`.claude/skills/content-engine/references/voice-principles.md` — read that file at generation time.

## Design Template cell -> template folders

`schedule.py` parses out both numbers. Templates that exist on disk:

- **LinkedIn** {1, 2, 4, 9, 10, 11} -> `.claude/skills/linkedin-infographics/references/LinkedIn-Template-<N>/`
- **Instagram** {1, 2, 6, 10} -> `.claude/skills/carousel/references/Instagram-Template-<N>/`

Numbering is sparse. If a row names a missing number, `schedule.py` returns it in
`templates.errors` — stop and ask Aleem which template to use instead. Never substitute silently.

## Write-back

`python scripts/schedule.py write --row <N> --doc-url <URL> [--status Draft]`
writes the Doc URL into that row's Final Video/Post cell and sets Status.
