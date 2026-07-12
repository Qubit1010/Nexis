# Per-short input — Instagram-Short-Template-1 (one detailed prompt per frame)

Dark branded vertical short: a cover, one or two content frames, and a CTA. Best used for any
schedule topic or ad hoc idea that needs a quick Reels/Shorts teaser rather than a full
carousel breakdown.

Build the Gem once from `gem.md` (attach the reference cover image). Then per short:

1. Paste **CONTEXT** (sets the frame count + topic, no image generated).
2. Paste **COVER**, the hook frame.
3. Paste one **CONTENT** prompt per point (1-2 frames).
4. Paste **CTA** for the last frame.

---

## CONTEXT (paste first, no image)

```
We are building a <N>-frame Instagram Short in the Template-1 style (match the Knowledge reference image). I will send ONE detailed prompt per frame; generate ONE 1080x1920 image per prompt. Do not generate anything yet, do not tile frames, do not build a slide deck.

Topic: <what the short is about - e.g. "the Claude Practical Playbook free guide">
Frame count: <3 or 4> (cover, <1 or 2> content frame(s), CTA)

Reply with a one-line confirmation and a numbered frame plan, then wait for my per-frame prompts.
```

---

## COVER (frame 1)

```
Frame 1 of <N>: COVER. Generate ONE 1080x1920 image only.
Style: near-black background (#141414).
Top-left: NexusPoint "N" logomark, white, with small circuit-node accent dots/lines trailing from it.
Below logo: small tracked-out all-caps eyebrow label, white: "<EYEBROW LABEL>"
Center-left (below eyebrow): large bold white headline, left-aligned, <2-4> lines: "<HEADLINE LINE 1>" / "<HEADLINE LINE 2>" / ...
Below headline: one gray subtitle line, left-aligned: "<SUBTITLE>"
Lower-middle: diagonal gradient stripe sweeping from bottom-left to upper-right, light blue (#4FA3F7) to darker blue (#1C5FA8), crossing behind the text block.
Bottom center: "NexusPoint" wordmark, small, gray (#9A9A9A).
One image only.
```

---

## CONTENT (repeat for each point, increment frame number)

```
Frame <N> of <TOTAL>: CONTENT. Generate ONE 1080x1920 image only.
Style: near-black background (#141414), same diagonal blue gradient stripe (#4FA3F7 to #1C5FA8) as the cover, same NexusPoint logo top-left, same wordmark footer.
Center: one bold white statement, large but shorter than the cover headline: "<CONTENT STATEMENT>"
Below the statement (optional): one smaller gray supporting label or stat: "<SUPPORTING LABEL, or omit>"
Bottom center: "NexusPoint" wordmark, small, gray.
One image only.
```

---

## CTA (last frame)

```
Frame <N> of <N>: CTA. Generate ONE 1080x1920 image only.
Style: near-black background (#141414), same diagonal blue gradient stripe as prior frames, brought forward slightly so the pill sits on it.
Center: rounded-rectangle pill, near-black fill (#141414), blue outline (#4FA3F7), bold white text, centered: "<CTA TEXT - URL or short action phrase>"
Below pill (optional): one gray payoff line: "<PAYOFF LINE, or omit>"
Top-left: NexusPoint "N" logomark, white, with circuit-node accents (same as other frames).
Bottom center: "NexusPoint" wordmark, small, gray.
One image only.
```

---

Notes:
- Fix any frame with: `regenerate frame N, same style, change <X>`.
- Default to 3 frames (cover, 1 content, CTA) unless the topic genuinely needs a second
  content frame to land - a short earns its name by staying short.
- See `example-post.md` for a fully filled 3-frame set.
