# Design Standards — the anti-slop bar (Phase 2)

The whole point of this phase is that the finished product does not look AI-generated. "AI slop" is the generic default look: a purple-to-blue gradient hero, three equal feature cards with lucide icons, `Inter` everywhere, one accent color, uniform 8px-everything spacing, no real states, no point of view. This phase exists to prevent that.

## The three tools and what each is for

- **`ui-ux-pro-max`** — the design intelligence. Style selection, palette theory, font pairing, layout systems, accessibility rules, chart/component patterns. Use it to reason about what fits the product and to pull concrete, correct guidelines.
- **`taste-skill`** — the anti-slop enforcer and aesthetic engine. Reach for it whenever the product wants a distinct look, or when the default direction risks looking templated. It routes to the right sub-skill (brutalist, minimalist, luxury/brand-kit, high-end agency, motion-heavy/GSAP, image-first). Use it to commit to a real aesthetic with a point of view, not a safe average.
- **`ui-design-system`** — the token system for clean handoff. Use it to lock the color scale, spacing scale, radius, shadow, and motion tokens so Phase 3 builds against real design tokens, not ad-hoc values.

Order: use ui-ux-pro-max to decide the direction, taste-skill to sharpen the aesthetic, ui-design-system to lock the tokens. Write it all to `.builder/design-system.md`.

## Derive the direction from the product, not a default

Read the blueprint + architecture for: who uses this, the emotional register (a fintech dashboard is calm and precise; a sports-sponsorship marketplace is energetic and bold; a legal tool is trustworthy and restrained), the platform, and the density (data-heavy admin vs. airy marketing). The aesthetic is a decision derived from those, exactly like the stack is derived from the problem. Name the reason.

## The bar every UI must clear

**Visual identity (the anti-generic checks):**
- A real color system: a considered primary + secondary + accent with proper tints/shades and neutral scale, not one hue on gray. Meaningful, not decorative.
- Type with intent: a heading/body pairing chosen for personality and a real type scale (not every heading the same size). Avoid defaulting to `Inter` for everything unless it is a deliberate choice.
- Spacing rhythm: a consistent scale with genuine hierarchy and breathing room, not uniform padding everywhere.
- A signature: at least 1-2 memorable moments (a distinctive hero, a custom empty state, a considered data viz, a motion detail) that a template would not have.
- Depth done on purpose: shadows/borders/gradients used as a system, not sprinkled.

**Interaction & motion:**
- Purposeful motion: transitions that aid understanding (state changes, page transitions), tuned easing/duration, never gratuitous.
- Real states for everything async: loading (skeletons over spinners where it fits), empty (designed, not blank), error (helpful, near the problem), success.
- Hover/focus/active/disabled all styled. `cursor: pointer` on clickables.
- Respect `prefers-reduced-motion`.

**Accessibility (CRITICAL, from ui-ux-pro-max):**
- Contrast >= 4.5:1 for normal text, 3:1 for large.
- Visible focus rings on every interactive element; tab order matches visual order.
- Touch targets >= 44x44px.
- Labels tied to inputs; `aria-label` on icon-only buttons; alt text on meaningful images.
- Body text >= 16px on mobile.

**Responsive:**
- Mobile-first. Content fits the viewport, no horizontal scroll.
- Layouts reflow (not just shrink) at real breakpoints. Test the smallest and a mid width.
- A defined z-index scale.

## The checkpoint (mandatory unless `--auto`)

After writing `design-system.md`, present the direction to the user before building. Keep it tight:

1. **Aesthetic + why** — one line naming the chosen direction and why it fits this product's audience and register.
2. **Palette** — the primary/accent/neutral roles (with hex).
3. **Type** — the heading/body pairing and the register it sets.
4. **Motion/interaction feel** — one line on how it should feel.
5. **Signature moments** — the 1-2 things that make it memorable.

Then ask: go, or adjust? Do not start Phase 3 until it is approved. If the user wants a different feel, re-run with taste-skill toward that aesthetic and re-present. This gate is the difference between premium and generic; spend the one round here.
