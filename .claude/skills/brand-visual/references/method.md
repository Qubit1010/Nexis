# Method — building a visual identity

The pipeline. Load this first in build mode.

Output: `client-projects/<slug>/15-brand-visual-identity.md`, structured per
`report-structure.md`. When the client wants the single manual, also
`16-brand-guidelines.md` (assembly rules at the end of `report-structure.md`).

**This document is the written spec, not the artwork.** Hex values, type scales, measured
contrast ratios, licence status. Imagery generation hands off to `taste-skill:brandkit`.

---

## Phase 0 — Resolve the input

Same dispatch as the sibling skills. All run **UNSANDBOXED**.

| What they gave | Resolve with |
|---|---|
| Google Doc URL or ID | `python .claude/skills/client-onboarding-workflow/scripts/extract_proposal.py "<url_or_id>"` |
| PDF / DOCX brand book | `python .claude/skills/to-markdown/scripts/convert.py "<path>"` then `Read` the `.md` |
| Website URL | `python .claude/skills/web-scraper/scripts/scrape.py --url "<url>" --depth crawl --pages 12 --extract raw` |
| Name only | `python .claude/skills/research/scripts/research.py --query "<name> <industry>" --depth medium --mode entity` then crawl |

---

## Phase 1 — Record the current state as fact, not impression

Most identity engagements begin by discovering the client does not own what they think they
own. Establish, by measurement:

- **Actual hex values** sampled from the live site, not the values in the old brand PDF. They
  diverge more often than not.
- **Fonts actually loaded** by the site, versus the fonts the brand book names.
- **Logo files they possess**, and in what formats. "Do you have vector?" has a surprising
  failure rate, and a raster-only logo constrains everything downstream.
- **Where the identity already breaks**: social avatars, email signatures, proposals,
  invoices, packaging. The surfaces nobody audits.

Put all of this in section 0 as facts with confidence levels. This phase alone frequently
justifies the engagement.

---

## Phase 2 — Read upstream

| File | Take |
|---|---|
| `13-brand-strategy.md` | Personality traits and positioning. **Every visual decision traces back to one of them.** A colour chosen because it looks good is a preference; a colour chosen because the brand is positioned against a category of loud competitors is a decision |
| `14-brand-voice.md` | The register. A visual system and a voice that disagree is the most common incoherence in an identity |
| `13`'s category research | What the category looks like, so conformity and deviation each have a known cost |

If `13` does not exist, you are designing a system with nothing to express. Offer
`brand-strategy` first. If declined, derive working direction here and label it an assumption.

---

## Phase 3 — Set the direction

One paragraph, per `report-structure.md` §1. Name which personality trait and which position
each visual decision will serve. Everything downstream refers back to it.

**Category conformity is a real variable, not a failure.** Category colour norms exist and
atypical packaging colour has measured consequences `[C]` [s112]. Deviating is a legitimate
choice with a cost; conforming is a legitimate choice with a different cost. Say which one is
being made and why.

---

## Phase 4 — Logo direction

Per `report-structure.md` §2. The evidence:

- **Henderson & Cote** is the foundational work on selecting or modifying logos `[C]` [s123].
- **Descriptiveness has been tested directly** `[C]` [s124]. A widely circulated HBR summary
  claims descriptive marks improve evaluations and performance but supplies no numbers `[P]`.
- **Complexity moderates response** `[C]` [s125], and visual complexity is separable from
  conceptual complexity `[C]` [s127].
- **Shape carries meaning.** Rounding angular logos shifts brand attitude `[C]` [s126];
  asymmetry interacts with brand personality `[C]` [s129]; shape affects consumer inference
  `[C]` [s11]. Orientation and implied motion affect perceived reliability and innovativeness
  `[C]` [s15].
- **Logos relate to firm performance** `[C]` [s130] and logo change to brand attitude `[C]`
  [s131].

**Keep, refine or replace.** This decision is the section's real output and it must be
defended, not assumed. Replacement discards accumulated recognition. The mechanism is
evidenced: the most loyal customers react worst to identity change `[C]` [s29], and redesign
carries documented backlash risk `[C]` [s11].

**No ROI figure exists.** If asked what a new logo is worth in revenue, say no traceable
primary study supports any such number.

Hand imagery to `taste-skill:brandkit`. State the handoff.

---

## Phase 5 — Colour

Per `report-structure.md` §3. Roles first, values second.

Get candidates rather than inventing from scratch:

```
python .claude/skills/ui-ux-pro-max/scripts/search.py "<direction keywords>" --domain color -n 5
```

Returns palettes with roles already assigned (primary, secondary, CTA, background, text,
border). Treat as candidates, then justify the choice against Phase 3.

**The evidence:**

- **Hue maps to brand personality**: red to excitement, blue to competence `[C]` [s107].
- **Appropriateness beats hue.** Fit to brand and product is more consequential than the hue
  itself, and saturation and value matter alongside it `[C]` [s104] [s110].
- **Category norms exist** `[C]` [s112]; **trust is colour-sensitive** `[C]` [s113]; **context
  moderates everything** `[C]` [s111].
- **No effect sizes are available.** State direction only.

**Refuse the 80% claim.** "Colour increases brand recognition by 80%" has no traceable primary
source and two independent traces call it a myth `[P]` [s144] [s147]. It will come up.

**Compute contrast in this phase, not at the end.** See Phase 8.

---

## Phase 6 — Typography

Per `report-structure.md` §4.

```
python .claude/skills/ui-ux-pro-max/scripts/search.py "<mood keywords>" --domain typography -n 5
```

Returns pairings with mood keywords, Google Fonts URLs, CSS imports and Tailwind config.

**The evidence:**

- **Typefaces carry semantic associations that transfer to the message** `[C]` [s114] [s118],
  and typeface design is usable for impression management `[C]` [s115].
- Typographic factors affect advertising persuasion `[C]` [s117].
- **Legibility is genuinely contested.** Serif-versus-sans has been studied `[C]` [s116] with a
  broader legibility literature `[C]` [s119] [s120] [s121] [s122], and practitioner reviews
  conclude no universal rule holds `[P]` [s199] [s207]. **Never assert a legibility rule.**
- Two circulating numbers are secondhand vendor claims and must not be cited: the Monotype 13%
  figure `[P]` [s160] and the Baskerville-versus-Comic-Sans believability study `[P]` [s189].

**Licensing is a live commercial risk and the corpus is silent on it.** Web, desktop and app
use are licensed separately. Check the specific foundry terms and state what was and was not
verified. **Never quote a licensing cost from memory.**

---

## Phase 7 — Space, imagery, applications

Per `report-structure.md` §5-7. Spacing scale, grid, breakpoints, radii, elevation, then art
direction, then the surfaces they actually use.

§5 is the most-skipped section and the most common reason an identity looks coherent in the
deck and incoherent in production.

---

## Phase 8 — Accessibility, computed

Per `report-structure.md` §8. **Compute every contrast ratio. Do not estimate.**

WCAG AA is the floor: 4.5:1 for body text, 3:1 for large text and UI components. Report the
computed number, not just pass or fail.

Contrast ratio is a defined formula on relative luminance, so it is arithmetic rather than
judgment:

```python
def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def contrast(hex1, hex2):
    def lum(h):
        h = h.lstrip('#')
        r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
        return 0.2126*_lin(r) + 0.7152*_lin(g) + 0.0722*_lin(b)
    a, b = sorted((lum(hex1), lum(hex2)), reverse=True)
    return (a + 0.05) / (b + 0.05)
```

**When a brand colour fails**, supply an accessible variant for text use and keep the original
for large display use. Do not quietly drop the brand colour, and do not ship an inaccessible
one. Record both and say which goes where.

Accessibility is **not** in the research corpus, WCAG is a standard, not a finding. Cite the
standard, not an `[sN]`.

---

## Phase 9 — Tokens

Per `report-structure.md` §9.

```
python .claude/skills/ui-design-system/scripts/design_token_generator.py "<primary-hex>" modern json
```

Also `css` and `scss`. **Never `summary`**: it prints emoji, violating the house style rule.

It derives tints and shades algorithmically from a single hex, so the output is a **starting
scale, not the answer**. Check every generated step against the roles from Phase 5, override
what fights the palette, and record what was overridden and why. Shipping generated tokens
unchecked is how a system ends up with eleven blues and no rule about which to use.

---

## Phase 10 — Kill list, then deliver

Run against `.claude/skills/branding-advisor/references/what-not-to-do.md`. This skill has no
kill list of its own; one copy cannot drift.

1. Write `client-projects/<slug>/15-brand-visual-identity.md`.
2. If asked for the manual, assemble `16-brand-guidelines.md` per the rules at the end of
   `report-structure.md`. **Pull finished sections, do not re-derive.** If `13`, `14` and `15`
   disagree, fix the source rather than reconciling silently in the assembly.
3. Summarise: the direction in one line, the palette roles, the type pairing, any contrast
   failures found and how they were resolved.

Doc and PDF are not built by default. Offer via `content-engine/scripts/save_content.py` and
`seo-advisor/scripts/seo_pdf.py`.

---

## A note on consistency

The client will assume consistency is self-evidently good and the deliverable is what produces
it. Neither is quite true, and the corpus is clear enough to be worth repeating:

- **Consistency is a questioned dogma**, not a proven law `[C]` [s46].
- **Whether guidelines improve consistency is only anecdotally evidenced** `[P]` [s178] [s248].
- **Adoption is an organizational problem.** Employee response is the hinge `[C]` [s45] [s50],
  and print-first documents that ignore digital are a documented cause of non-adoption `[P]`
  [s181] [s190].

The practical consequence for this skill: write for the people who will use it. A guidelines
document optimised to look impressive in a presentation and awkward to consult while building a
page is the failure mode, and it is the normal one.
