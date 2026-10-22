---
name: cinematic-video-studio
description: Produce a cinematic 9:16 client film (45-65s) with AI live-action and recurring fictional characters: script, Higgsfield keyframe stills animated with Kling, cast AI voices, an original score and a verified 1080p edit. Use for client explainer or campaign films, upgrading a concept cut, or planning one with a credit estimate. NexusPoint's own post-to-reel motion graphics belong to nexis-reel-studio or reel-creator.
---

# Cinematic Video Studio

Turns a brief into a finished, verified 1080x1920 film that reads like a short cinematic piece:
the opposite of a slideshow of AI clips. The pipeline was proven on CURE Medical Centers
(Pearl Diver, Majlis Question and Three Generations v2), where the client approved the result.

The single biggest quality lever is **keyframe-first generation**: write each shot as a 2K
still, look at every still, reject the off-brief ones (a cent each), and only then animate the
approved stills. Animating straight from text produced wrong hands, modern boats and plain
pearls; the still gate caught a dozen problems before they cost a video render.

## Before anything: the client profile

Every client gets a `video-profile.json` in their gitignored client folder
(`client-projects/<client>/...`), never in this skill. It holds brand colours, logo PNG, fonts,
end card, the Higgsfield workspace, hard rules, saved character element IDs, cast voices and
reusable footage. Read it first and treat its `hard_rules` as non-negotiable.

- **Existing client:** find the profile (CURE: `client-projects/primara/cure/video-profile.json`).
- **New client:** build one with `references/client-onboarding.md` before writing a script.
  It takes ten minutes and prevents most rework.

## Plan-only requests

When the user wants to check a plan with the client first, stop after step 2 plus prompts:
deliver `script.md`, the still and motion prompts, `spec.json` (written for its real folder)
and a credit estimate (unit costs from the playbook, plus a reroll allowance), with no
generation calls. List the open client decisions. That is a complete deliverable, not a half-done film.

## The workflow

Work in a film folder (`<films_dir>/<n>-<slug>/v2/` for an upgrade, or `<n>-<slug>/` new) with
`keyframes/`, `clips/`, `vo/`, `script.md`, `spec.json`, `generations.md`.

1. **Gate on Higgsfield.** Check `session_connectors_status` for the `higgsfield` server. If it
   is `needs_auth`, stop and ask the user to sign in via `/mcp` (you cannot do it). Select the
   profile's workspace and read the balance. Details: `references/higgsfield-playbook.md`.
2. **Script and shot list** (`script.md`): one idea, told in pictures, 45-65s, 8-12 shots of
   4-6s. If the client has other films, read their scripts first. Vary the opener and setting,
   and respect the profile's `canon` (who is alive, who is related). Arabic (or the client language) lines drafted short enough to fit their shots. See
   `references/story-craft.md` for structures that worked, timing maths and the placeholder
   pattern for anything that must be filmed for real (doctor, real staff, real patients).
3. **Estimate cost, then generate stills.** Preflight with `get_cost`. Generate one 2K still per
   shot with Nano Banana Pro, putting saved characters in via `<<<element_id>>>`. Download,
   build a contact sheet, **look at every still** and regenerate the off-brief ones. The
   rejection checklist in `references/prompt-craft.md` lists real failures to look for.
4. **Animate approved stills** with Kling 3.0 Pro (start_image = the still's job id, 1080p, 6s,
   sound off; about 10.5 credits a clip). Review the clips as frame strips; reject anything
   that drifts (creatures appearing, smoke-like breath, a character standing up).
5. **Voices.** Generate each line separately (Eleven v4) so timing stays editable. Audition 3-5
   voices on one line and pick by `scripts/voice_pitch.py`, because you cannot listen. Reuse the
   profile's cast voices. Never voice a role the profile forbids (e.g. an AI doctor); children
   stay silent.
6. **Spec and build.** Write `spec.json` (`references/spec-format.md`), then
   `python -I scripts/build_cut.py <film>/spec.json --draft` for a fast timing check, and the
   same without `--draft` for the delivery master plus a small `-share` copy.
7. **Verify.** `python -I scripts/verify_cut.py <film>/spec.json` must PASS. It catches the
   silent failure where a broken transition shows the end card for half the film. Then look at
   `verify-sheet.jpg` and a few frames around every transition and caption.
8. **Deliver.** Log everything in `generations.md` (models, job ids, prompts, rejects and why,
   voices with pitch, credits before and after). Add the film's review flags to the client's
   review file, send the `-share` copy, and offer the Drive sync (`gdrive-sync`).

## Things that matter more than they look

- **Say what you did not check.** You cannot hear the voices or the score. Report loudness and
  pitch numbers, and say plainly you have not listened.
- **Placeholders must look like placeholders.** If something must be real in the final (a
  doctor's answer), use a placeholder card, and if it must be audible in a concept cut, use a
  narrator voice with the card saying so. An AI voice in that slot must not survive into a final.
- **Culture beats prettiness.** For Gulf clients especially: no flags, rulers, palaces or
  mosque-like architecture; modest dress; pearl strands must read as jewellery, not prayer
  beads; elders are served by the young; handleless finjan, not a teacup.
- **Calm music.** The score is synthesized locally (`scripts/score.py`), free and licence-safe.
  A rising Shepard tone was judged too intense, so keep it tranquil unless asked.
- **Budget honestly.** Preflight costs, report credits before and after, and do not reroll the
  same shot more than three times. Use the best attempt and flag it for the human reviewer instead.

## Scripts

| Script | Does |
|---|---|
| `build_cut.py` | spec + profile → master MP4 + `-share` copy + `timeline.json` |
| `verify_cut.py` | duration, per-shot content match, loudness, voice presence, contact sheet |
| `overlay.py` | brand-styled captions, titles, labels, placeholder cards, end card (RTL-safe) |
| `score.py` | original calm score cued to the timeline |
| `voice_pitch.py` | median pitch + brightness per audio file, for casting |
| `fetch.py` | download Higgsfield results into the film folder by relative path |

Requirements: `pip install imageio-ffmpeg numpy pillow` (bundled ffmpeg), wkhtmltopdf installed
(for wkhtmltoimage), the Higgsfield MCP server signed in. Run scripts with `python -I`.

## References

- `references/higgsfield-playbook.md` — auth, workspace, models, costs, element creation, the
  preset-hijack retry, polling, downloads.
- `references/prompt-craft.md` — still and motion prompt patterns, the rejection checklist.
- `references/story-craft.md` — structures, pacing, line timing, placeholder slots, titles.
- `references/spec-format.md` — `spec.json` and `video-profile.json` schemas.
- `references/client-onboarding.md` — building a new client profile.
- Worked example: CURE's three v2 films, each folder with `script.md`, `spec.json` and
  `generations.md`, under `client-projects/primara/cure/event-videos/`.
