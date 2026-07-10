# Design System Template

> Written in Phase 2 (ui-ux-pro-max + taste-skill + ui-design-system). This is what keeps the UI from looking generic. Every choice is derived from the product, and named. Read `references/design-standards.md` first.

---

```yaml
---
project: {{PROJECT_NAME}}
aesthetic: {{e.g., "warm editorial minimalism" | "high-energy sports marketplace" | "precise fintech"}}
platform: {{web | mobile | both}}
created: {{ISO_TIMESTAMP}}
---
```

## 1. Direction (the why)

{{One short paragraph: the product's audience and emotional register, the aesthetic chosen, and why it fits. This is the anti-slop thesis — it should be impossible to swap onto a different product without it feeling wrong.}}

- **Aesthetic:** {{named direction}}
- **Register / mood:** {{e.g., trustworthy and calm / bold and kinetic / premium and restrained}}
- **Reference points:** {{2-3 touchstones, if used}}
- **taste-skill sub-skill used:** {{e.g., minimalist-ui / high-end-visual-design / industrial-brutalist-ui / none}}

## 2. Color System

| Role | Token | Value | Notes |
|------|-------|-------|-------|
| Primary | `--color-primary` | {{hex}} | {{when to use}} |
| Primary tints/shades | `--color-primary-{50..900}` | {{scale}} | |
| Secondary | `--color-secondary` | {{hex}} | |
| Accent | `--color-accent` | {{hex}} | {{sparingly, for emphasis}} |
| Neutral scale | `--color-neutral-{50..900}` | {{scale}} | text, surfaces, borders |
| Semantic | success / warning / error / info | {{hex each}} | states |

- **Dark mode:** {{yes/no; how the scale maps}}
- **Contrast:** all text/background pairs meet >= 4.5:1 (3:1 large).

## 3. Typography

| Role | Font | Weight | Size / scale |
|------|------|--------|--------------|
| Display / H1 | {{font}} | {{weight}} | {{size}} |
| Headings | {{font}} | {{weight}} | {{scale}} |
| Body | {{font}} | {{weight}} | {{size / line-height}} |
| Mono / data | {{font, if any}} | | |

- **Pairing rationale:** {{why these fonts carry the register}}
- **Type scale:** {{the ratio/steps — real hierarchy, not one size}}

## 4. Tokens (ui-design-system)

- **Spacing scale:** {{e.g., 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64}}
- **Radius:** {{scale}}
- **Shadow / elevation:** {{scale, used as a system}}
- **Border:** {{weights / colors}}
- **Z-index scale:** {{e.g., 10 / 20 / 30 / 50}}
- **Breakpoints:** {{sm / md / lg / xl}}

## 5. Motion

- **Language:** {{how motion should feel — snappy / smooth / minimal}}
- **Durations / easing:** {{tokens}}
- **Signature transitions:** {{page/state transitions worth specifying}}
- **Reduced motion:** honored.

## 6. Component Treatments

{{For the key components, the specific treatment — not just "a button". Buttons (variants/states), inputs, cards, nav/sidebar, tables, modals, data viz. Note anything that departs from the framework default toward the chosen aesthetic.}}

## 7. Signature Moments

{{The 1-2 memorable things a template would not have: a distinctive hero, a custom empty state, a considered chart, a motion detail. Describe each concretely enough to build.}}

## 8. States Checklist

Every async surface must ship: loading (skeleton where it fits), empty (designed, not blank), error (helpful, near the problem), success. Every interactive element: hover / focus / active / disabled. List the ones that need custom design here.

---

## Checkpoint summary (present this to the user)

- **Aesthetic + why:** {{one line}}
- **Palette:** {{primary / accent / neutral, hex}}
- **Type:** {{heading + body pairing, register}}
- **Motion/feel:** {{one line}}
- **Signature moments:** {{the 1-2}}

Ask: go, or adjust? Do not build Phase 3 until approved (unless `--auto`).
