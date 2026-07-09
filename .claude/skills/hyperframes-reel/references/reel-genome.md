# Reel Genome — the reusable DNA of a "flagship motion-graphics reel"

This is the persisted memory of the inspiration reel (`docs/Reel-Inspiration-Motion-Graphics.mp4`,
an ElevenLabs product film) plus the motion-graphics principles that make a reel read as premium.
It is the **style source of truth** for the `hyperframes-reel` skill.

Read this as a **genome, not a template.** The genome is the small set of things held constant so
every reel feels like it comes from the same studio. Everything structural — how many beats, their
order, which visual devices appear — is **invented fresh per post.** Two posts should produce two
structurally different reels that still feel like siblings. If you ever find yourself reaching for
"beat 1 is always the logo, beat 6 is always the count-up," stop: that is a template, and templates
are what this skill exists to avoid.

---

## 1. What the inspiration actually is (the extracted core)

Analyzed frame-by-frame (scene detection + 1fps sampling). The facts worth remembering:

**Technical fingerprint**
- 43s, originally 1920×1080 @ **60fps**. Ours is **1080×1920 (9:16) @ 30fps** (reel-engine's `VIDEO`).
- **~1 hard cut in the entire film.** Soft transitions at ~21.8s and ~25.1s; the one hard cut is a
  deliberate "register shift" into a dark interlude. This is the single most important structural
  fact: it is a **near-continuous morph piece**, not a jump-cut reel. Motion is the connective
  tissue — one idea flows into the next by transformation, not by cutting.
- Elements live on a **spatial canvas** that the "camera" pans and zooms across. Depth is built with
  **scale + blur**, not hard layered cards.

**Identity of the inspiration (NOT ours — see §2 for ours)**
- Light near-white canvas, near-black text.
- A signature **blue↔orange gradient "orb"** — a soft, blurred radial sphere that constantly
  morphs and rotates. It is the recurring "AI presence" anchor.
- One dark-navy particle interlude for contrast.

**The 8-beat arc it happened to use** (an example of good structure, **never a template to copy**):
1. Setup — logo forms, config cards build.
2. Integration — second logo, a call UI, the orb appears.
3. Use case — real chat-UI mockups, a concrete conversation.
4. Logic — an agent decision-tree / flow graph.
5. Transition — zoom into the orb → **the one hard cut** → dark particle field.
6. Global — wireframe globe + orb + a **count-up 19→32** "Languages."
7. Multilingual — full-bleed gradient + a burst of chat bubbles.
8. Payoff + outro — kinetic type "Understand / Respond / Act" → logo assembles → fade out.

The lesson from the arc is the **shape of energy**, not the beats: it *builds* to a climax (the
globe/count-up) then *resolves* to a brand lockup. Each beat holds ~3–5s. Reveals are staggered,
never all-at-once.

---

## 2. The genome — what stays CONSTANT across every reel

These are the only fixed things. They are what make a reel "one of ours."

### 2a. Brand skin (the `nexis-reel` frame preset)
Sourced from `projects/reel-engine/src/brand.ts`. Tonally **inverted** from the inspiration: dark
canvas, not light.

- **Canvas:** charcoal `#232323` → `#161616` vertical gradient (dark, deep). Never pure black,
  never light.
- **Accent / voltage:** tech-blue gradient `#208EC7` (bright cyan-blue) → `#1F5B99` (royal blue),
  135°. This is the scarce "voltage" — the CTA, the one hot moment, the orb's core.
- **Text:** white `#FFFFFF` for display; `rgba(255,255,255,0.62)` fog for body on dark.
- **Hairline:** `rgba(255,255,255,0.12)`. **Glow:** `rgba(32,142,199,0.55)` blue glow for pills.
- **Type:** QuicheSans (display) / Urbanist (body). Display carries hooks + payoff lines; body
  carries support copy + chrome.
- **The gradient orb is an OCCASIONAL accent, NOT a persistent background.** Blue → cyan →
  white-bloom (no orange). Use it *sparingly* — a hook flourish, a single "AI presence" beat, or a
  bloom on a transition. **Never leave it sitting behind every scene.** A static orb in all beats
  reads as one blurry blob and kills the variety that makes a reel feel premium. Most beats should
  have NO orb; the beat's own device (a diagram, a UI, numbers, kinetic type) is the focal element.
  If in doubt, leave it out.

- **Variety IS the flow (the principle behind the inspiration).** The inspiration was NOT one motif
  repeated — it was a *sequence of distinct visual worlds* (config cards → UI mockups → a flow graph
  → a globe → count-ups → kinetic type), each its own scene, welded together by continuous motion.
  That variety is the point. Every beat must look meaningfully different from its neighbors; the
  through-line is the **palette + type + motion doctrine**, never a single repeated element. If two
  beats look like the same layout with new text, redesign one.

### 2b. The motion doctrine (the quality bar — hard rules)
Folds the inspiration's feel with HyperFrames' own `hyperframes-creative/references/motion-principles.md`
(read that file in full when building frames — these are the load-bearing GSAP rules too). The
checklist every reel must pass:

- **Easing = emotion.** Never constant-speed. `.out` for entrances (fast→settle, responsive),
  `.in` for exits (slow→accelerate away), `.inOut` for moves between positions. No more than 2
  tweens share an ease per scene.
- **Speed = weight.** Fast 0.15–0.3s = energy; medium 0.3–0.5s = professional; slow 0.5–0.8s =
  luxury; very slow 0.8–2s = cinematic. The slowest scene should be ≥3× the fastest. Vary
  deliberately.
- **Build / breathe / resolve.** Every beat: staggered entrance (0–30%), ONE ambient motion while
  it lives (30–70%), decisive exit (70–100%, exits faster than entrances). Don't dump everything in
  the build.
- **Choreography = hierarchy.** The element that moves first reads as most important — stagger by
  importance, not DOM order; total stagger sequence <500ms.
- **≤1 hard cut per reel.** Reserve the single hard cut for a register shift (as the inspiration
  does). Everything else is crossfade ("this continues") or dissolve ("drift with me"). Continuous
  motion is the spine — one idea morphs into the next.
- **Fill the frame.** Hero text 60–80% of width; 2 focal points min per scene; 3 layers min
  (background treatment / content / accents). Background is never empty — radial blue glow,
  oversized faded type bleeding off-frame, hairline rules. A flat dark fill reads as "nothing
  loaded."
- **Anchor to edges, not float-and-center.** Vertical stacks, zone-based layouts. In 9:16 the orb
  owns the center; focal moments stack top/bottom.

### 2c. The aesthetic bar (the "expensive" read)
From the Exa motion-graphics research + the inspiration's feel:
- Clarity and focus — one dominant focal element per moment; generous negative space.
- Controlled pacing — slow-to-medium, "breathing," not frantic. Every frame could be a still.
- Intentional framing, atmospheric depth (scale + blur), emotionally-driven timing.
- 30fps here (60 in the source) — smoothness still matters; avoid jitter, prefer eased continuous
  motion over stepped changes.

---

## 3. The blueprint palette — a vocabulary, NOT a sequence

HyperFrames ships blueprints (shot shapes) and rules (atomic motion recipes). They live in
`hyperframes/hyperframes-animation/` — read `blueprints-index.md` and `rules-index.md` on demand.
The genome maps the inspiration's building blocks onto them so you can reach for the right one **when
the post's content calls for it** — using few or many, in any order, or composing a new shot shape.
Story truth decides structure; a blueprint is used only when the content needs it.

| When the post needs… | Reach for (blueprint) | Supporting rules |
|---|---|---|
| A hook / payoff line / tagline | `kinetic-type-beats`, `discrete-text-sequence` | `kinetic-beat-slam` |
| The AI-presence anchor (the orb) | *custom* (layered radial-gradient + blur) | `ambient-glow-bloom`, `sine-wave-loop`, `depth-of-field-blur` |
| A number / metric / proof point | `dataviz-countup`, `stat-bars-and-fills` | `counting-dynamic-scale` |
| A system / flow / relationship | `constellation-hub` | `svg-path-draw` |
| A concept, UI, or product moment | `grid-card-assemble`, `device-surface-showcase`, `cursor-ui-demo` | `spring-pop-entrance`, `card-morph-anchor`, `depth-scatter-assemble` |
| Volume / "too much" / a register shift | `overwhelm-surround` | `depth-scatter-assemble` |
| The brand outro (near-constant sign-off) | `logo-assemble-lockup` | `press-release-spring` |
| The continuous-camera spine tying it together | `spatial-pan-stations` | `multi-phase-camera`, `camera-cursor-tracking` |

**The orb is the one non-native element** — there is no orb blueprint. Build it in HTML/CSS:
layered `radial-gradient` spheres (blue core → cyan mid → white bloom), heavy CSS `blur()`, and
morph/rotate it on the seekable `tl` via `ambient-glow-bloom` + `sine-wave-loop`. It must attach to
the timeline (never a bare `gsap.to()`), or it won't scrub in the render.

---

## 4. How to compose a reel from a post (the free part)

Given a post (caption + source + optional infographic), **read it first**, then invent structure:

1. **Find the story.** What is the one idea? What is the hook (first 3s payoff or sharp question)?
   Is there a number worth a count-up? A system worth a flow graph? A "too much / here's the fix"
   tension worth a register shift? A list? Let the content dictate which devices earn a place.
2. **Draft the energy curve, not a beat count.** Build → climax → resolve. Decide where the peak is
   (often a stat, a reveal, or the orb at full bloom) and let the outro resolve to the brand lockup.
3. **Assign devices to moments** from the §3 palette — only the ones the story needs. A stat-heavy
   post leans on `dataviz-countup`; a conceptual post leans on kinetic type + the orb + a flow
   graph; a list post leans on `grid-card-assemble` / sequential reveals. Vary it. If two posts
   come out with the same device order, you are templating — recompose.
4. **Thread the spine.** Use a continuous-camera / morph transition between moments so the reel
   reads as one flowing piece with ≤1 hard cut. The orb is a natural connective element — it can
   persist across beats, morphing.
5. **Hold the genome.** Dark charcoal canvas, blue voltage, the orb, the motion doctrine, fill the
   frame. Check every scene against §2b before building it.

The proof that this skill works is **structural diversity**: feed it three different posts, get
three genuinely different reels that are unmistakably from the same studio.
