# Bold Variant — Playful

Friendly, energetic, expressive. Think Linear's marketing pages, Vercel's brand moments, Stripe's illustrated sections, modern indie SaaS. Warm but never childish.

## Aesthetic principles
- Soft pastel surfaces with one or two saturated accent colors
- Rounded geometry — chunky pill buttons, `rounded-3xl` cards
- Hand-feel: subtle hand-drawn arrows, squiggle underlines, tilted stickers
- Generous use of emoji-style spot illustrations or simple geometric mascots (NOT actual emojis unless requested)
- Type mixes friendly geometric sans with the occasional handwritten accent
- Motion has personality — small overshoots, bounces, springs (spring physics, not linear easing)

## Color palette
- `paper`: `#fffaf3` (soft warm off-white) OR `#fef6ee`
- `ink`: `#1f1d1a` (warm near-black)
- `muted`: `#6b6359`
- `accent-1`: `#ff6b4a` (coral/tangerine — primary)
- `accent-2`: `#7c5cff` (lavender — secondary)
- `accent-3`: `#22c5a8` (mint — tertiary, used as highlights/checkmarks)

Three accent colors is the maximum. Pastel backgrounds (light versions of each accent) tint section panels.

## Typography
- **Display:** Cabinet Grotesk 700/800 OR General Sans 700 — chunky, geometric
- **Body:** General Sans 400/500 OR Inter 400
- **Accent (used sparingly):** Caveat or Reenie Beanie — handwritten for callouts/scribbles

Tracking is normal. Headlines are colorful — words can be individually colored (e.g., "Automate the **boring**, Scale the *fun*").

## Layout language
- Hero: centered, illustrated background blob, big chunky headline with colored emphasis words. Pill CTA. Small product visual or 3D-ish illustration to the right.
- Sections: alternating tinted backgrounds (soft pastel) to break visual rhythm
- Services: 3 or 4 cards with `rounded-3xl`, a colored icon, generous padding. Each card has a soft accent shadow.
- Process: numbered timeline with bubble nodes, connected by hand-drawn dotted lines
- Testimonials: avatar + name, set on rounded cards, subtle tilt (-1° or +1°) for personality
- Footer: warm, illustrated, with the brand mascot waving or similar

## Hover/interaction
- Spring physics — Framer Motion `transition={{type:'spring', stiffness:300, damping:20}}`
- Cards lift on hover (translateY -4px) with growing colored shadow
- Buttons: scale 1.04 + slight rotate
- Background blobs slowly drift on scroll (parallax)
- Emoji-style spot illustrations gently bobble (sine animation)

## Anti-patterns (do NOT do)
- Pure white background
- Heavy gradients (one accent at a time, flat preferred)
- Tiny body text (<15px) — playful needs breathing room
- Sharp `border-radius: 0` anywhere
- Cluttered illustrations — one or two delightful spots per section max
- Comic Sans or actual childish fonts (Cabinet Grotesk and General Sans are the safe modern playful choices)
