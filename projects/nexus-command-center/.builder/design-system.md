---
project: NexusCommandCenter
aesthetic: "NexusPoint mission-control HUD — precision terminal, living data"
platform: web
created: 2026-07-10T16:02:00Z
---

## 1. Direction (the why)

The user is an operator (Aleem) and, over his shoulder, prospective clients — the screen must read as "this agency runs on its own AI OS" in the first three seconds. The register is precise, calm, quietly powerful: a mission-control room, not a gamer dashboard. Everything is near-black charcoal; the single brand blue is reserved for life — the graph, live status, and glows — so the eye always lands on the system itself. The living force-graph IS the interface; chrome recedes to hairlines and fog.

- **Aesthetic:** mission-control HUD on NexusPoint brand (dark, hairline chrome, glow-accented data)
- **Register / mood:** precise, alive, premium restraint
- **Reference points:** Aleem's V.A.U.L.T. / Claude Code OS / "AI Stack Connected" screenshots; reel-engine BrandBackground
- **taste-skill sub-skill used:** none — direction pre-pinned by brand + user screenshots (decisions.md)

## 2. Color System

| Role | Token | Value | Notes |
|------|-------|-------|-------|
| Primary | `--np-blue` | #208EC7 | brand blue: live data, links, active states |
| Primary deep | `--np-blue-deep` | #1F5B99 | gradient partner: `linear-gradient(135deg, #208EC7, #1F5B99)` |
| Primary tint | `--np-blue-300` | #63B3DD | hover on blue, highlighted edges |
| Glow | `--np-glow` | rgba(32,142,199,0.55) | canvas shadowBlur, focus rings, live pulses |
| Canvas base | `--np-black` | #0B0B0B | page background under aurora |
| Surface | `--np-charcoal` | #232323 -> #161616 | panel gradient (135deg), cards, docks |
| Hairline | `--np-hairline` | rgba(255,255,255,0.12) | ALL borders; no other border colors |
| Text primary | `--np-white` | #F5F7FA | headings, values |
| Text secondary | `--np-fog` | rgba(255,255,255,0.62) | labels, descriptions |
| Success | `--np-ok` | #34C388 | run complete, sync ok |
| Warning | `--np-warn` | #E5A83B | ceiling lock, drift |
| Error | `--np-err` | #E25A5A | failed run, missing graph |
| Graph communities | `--np-c0..c9` | 10-step categorical: #208EC7 #7A5AF8 #34C388 #E5A83B #E25A5A #2FB6BC #C25AC2 #8AA84B #D97C4A #5A78E2 | node/community coloring; all readable on #0B0B0B |

- **Dark mode:** the only mode (brand requirement).
- **Contrast:** fog on charcoal 7.8:1, white on charcoal 13:1 — AA everywhere; blue #208EC7 used >= 18px or non-text.

## 3. Typography

| Role | Font | Weight | Size / scale |
|------|------|--------|--------------|
| Display / H1 | QuicheSans | 600 | 28px — wordmark + panel titles only |
| Headings | QuicheSans | 500 | 20 / 16px |
| Body | Urbanist | 400/500 | 14px / 1.55 |
| Mono / data | JetBrains Mono (system fallback: Consolas) | 400 | 12-13px — vitals numbers, node ids, run log, statuses |

- **Pairing rationale:** QuicheSans (brand display) gives the editorial-premium signature; Urbanist keeps density readable; mono carries the terminal-HUD register for anything machine-generated.
- **Type scale:** 12 / 13 / 14 / 16 / 20 / 28 — tight, dashboard-real, honest hierarchy.

## 4. Tokens

- **Spacing:** 4 / 8 / 12 / 16 / 24 / 32 / 48 (Tailwind default subset; panels pad 16/24)
- **Radius:** 6 (chips/buttons) / 10 (cards) / 999 (pills — brand motif)
- **Shadow / elevation:** no gray shadows on dark; elevation = hairline border + subtle glow: `0 0 0 1px var(--np-hairline), 0 0 24px rgba(32,142,199,0.10)`; modal adds backdrop blur 8px
- **Border:** 1px hairline only
- **Z-index:** 0 aurora / 10 graph / 20 chrome (docks, bars) / 30 drawers+panel / 50 modal
- **Breakpoints:** desktop-first cockpit; min supported 1024px; below that, panels stack and the graph stays full-bleed (this is a control room, not a phone app — documented, not pretended)

## 5. Motion

- **Language:** calm precision — nothing bounces; things settle. The graph supplies the life; UI motion stays short and eased.
- **Durations / easing:** 150ms `cubic-bezier(.4,0,.2,1)` for hover/state; 240ms same curve for drawer/panel slide; graph settle handled by d3 cooldown.
- **Signature transitions:** side panel slides from right with 8px glow bloom on the selected node; deck confirm modal scales 0.98 -> 1 with backdrop blur; a 2s soft pulse (glow radius breathing) on any node whose run/status is live.
- **Reduced motion:** aurora pauses to a static gradient; pulses become steady rings; slides become fades.

## 6. Component Treatments

- **Buttons:** pill (radius 999) per brand motif. Primary = blue 135deg gradient, white text; ghost = transparent + hairline, fog text, blue text on hover. Focus: 2px glow ring. Disabled: 40% opacity, no pointer.
- **Chips (legend/filters):** pill, hairline, community dot + label; active = community color at 18% fill; keyboard toggleable.
- **Panels/drawers (SidePanel, CatalogDrawer):** charcoal 135deg gradient, hairline edge, 24px pad; title in QuicheSans; body Urbanist; machine values mono.
- **VitalsBar:** mono numbers with fog labels, separated by hairline dots; live values tick with a 150ms opacity blink on change.
- **CommandDeck:** bottom dock, charcoal, hairline top; preset buttons as pills with a mono cost hint; running state = inline pulse dot + elapsed mono timer; ceiling lock = warning banner with Acknowledge ghost button.
- **Confirm modal:** centered card, QuicheSans title, the preset description, mono ceiling line ("max $0.50 - run will be killed past 5:00"), Cancel ghost + Run primary.
- **Graph nodes (canvas):** filled circle in community color, 1px darker rim, `shadowBlur 12 / shadowColor --np-glow` on hover/selected; labels (Urbanist 11px, fog) fade in above zoom 1.4; selected node gets a white 1.5px ring; edges hairline-white at 12% opacity, blue at 45% when touching the selection.
- **Empty/error states:** designed — "graph missing" state shows the scanner command in a mono copy-block with a Run hint; empty catalog search shows "nothing matches — the system doesn't do that yet."

## 7. Signature Moments

1. **The living system graph:** on load, nodes bloom outward from the NexusPoint logo position and settle in ~2s (d3 cooldown), community colors emerging as it stabilizes — the "whole agency coming online" beat. This is the client-showcase money shot.
2. **Aurora under glass:** the reel-engine aurora (2-3 slow blue blobs + sparse drifting particles) re-implemented as a rAF canvas at z-0 under a frosted charcoal veil; the HUD appears lit from beneath. Paired with hairline chrome it reads as NexusPoint instantly.

## 8. States Checklist

Custom-designed: graph missing (scanner hint), command running (pulse + timer), over-ceiling lock (warning banner), run failed (error card with exit reason + log path), empty catalog search, vitals unavailable (dash placeholders). All interactive elements ship hover/focus/active/disabled; canvas interactions mirrored by keyboard via the catalog (a11y note: the canvas is exempt, the catalog is the accessible path to every node).

---

## Checkpoint summary (present this to the user)

- **Aesthetic + why:** NexusPoint mission-control HUD — hairline chrome and fog text on near-black charcoal, with the brand blue reserved for living data (graph, glows, statuses), so the system itself is the hero. Fits an operator cockpit that doubles as a client showcase.
- **Palette:** blue #208EC7 -> #1F5B99 on charcoal #232323/#161616 over #0B0B0B; hairline rgba(255,255,255,.12); fog text; 10-color community set anchored by brand blue.
- **Type:** QuicheSans display + Urbanist body + mono for machine data — premium editorial over terminal precision.
- **Motion/feel:** calm precision; the graph supplies the life (bloom-and-settle open, glow pulses), UI motion stays 150-240ms eased.
- **Signature moments:** (1) the graph blooming from the logo and settling into communities on load; (2) the aurora-under-glass backdrop ported from the reel-engine brand system.
