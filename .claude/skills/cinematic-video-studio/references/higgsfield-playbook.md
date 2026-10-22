# Higgsfield playbook

The Higgsfield MCP server (`higgsfield`, user scope, `https://mcp.higgsfield.ai/mcp`) generates
everything. The claude.ai connector named "Higgsfield AI" is read-only (balance, model list,
history) and cannot generate: do not mistake it for the real one.

## Gate

1. `session_connectors_status`: the `higgsfield` row must be `connected`. If it is
   `needs_auth`, the user must sign in from `/mcp` *in this session*. You cannot start OAuth, and
   a sign-in done in another session does not carry over. Stop and ask.
2. Load the tools by ToolSearch (`select:mcp__higgsfield__...`). Usual set: balance,
   list_workspaces, select_workspace, models_explore, generate_image(_batch),
   generate_video(_batch), generate_audio(_batch), jobs_wait, manage_reference_elements, list_voices.
3. `list_workspaces`, then `select_workspace` to the profile's workspace (the selection persists
   across sessions; still confirm it). Read `balance` and record it.

## Models and measured costs (team plan, October 2026)

| Use | Model | Settings | Credits |
|---|---|---|---|
| Keyframe still | `nano_banana_pro` | `resolution: 2k`, `aspect_ratio: 9:16` | 2 |
| Animate a still | `kling3_0` | `mode: pro` (1080p), `sound: off`, `duration: 6`, `medias: [{role: start_image, value: <image job id>}]` | 10.5 |
| Animate at 4K | `kling3_0` | `mode: 4k` | 36 (rarely worth it for 9:16 social) |
| Text-to-video (no still) | `seedance_2_0` | std, 720p | 4.5 per second (quality is visibly lower) |
| Voice line | `elevenlabs_v4` | `dialogue: [{text, voice_type: preset, voice_id}]`, `stability: 0.45` | about 0.23 |

Always preflight a new configuration with `get_cost: true` (single generate call, not batch).
Prices change. A 55s film with 8 clips cost about 100 credits end to end.

## Characters (consistent faces)

1. Generate one clear portrait per character (Nano Banana Pro, 3:4, "fictional, generic
   everyday face, not resembling any real person").
2. `manage_reference_elements` with `action: create`, `category: character`,
   `medias: [{id: <image job id>, type: image_job, url: <result url>}]`. It returns an element id.
3. Put `<<<element_id>>>` inside still prompts. Nano Banana Pro, GPT Image 2, Seedream and
   Seedance 2.0 honour it; Kling only through the start image. That is another reason to go
   still first. Record the ids in the client profile.

## Keyframe-first flow

- Batch stills with `generate_image_batch` (up to 12). Poll with `jobs_wait` (max 15s per call;
  stills take 1-4 min, Kling clips 2-4 min). Keep an index → job id map in a scratch file.
- Result URLs look like `https://d8j0ntlcm91z4.cloudfront.net/user_<id>/hf_<YYYYMMDD>_<HHMMSS>_<jobid>.<ext>`.
  Copy them from `jobs_wait` output; the timestamp is not predictable.
- Download with `scripts/fetch.py <film> '{"keyframes/k01.png": "<url>", ...}'`.
- Animate with `generate_video_batch`, `start_image` = the still's **job id** (not its URL).

## The preset hijack

Kling submissions sometimes come back `submission_failed` with "Preset "IN THE DARK" was
recommended instead of submitting a job". Nothing was charged. Resubmit the same item with
`declined_preset_id: <the preset id it gave>`. Putting `declined_preset_id` on every Kling
request from the start avoids the extra round trip.

## Gotchas

- Job status may say `"type": "image"` while a video is still in progress; trust `result_url`.
- `nano_banana_pro` jobs report as `nano_banana_2` in status; billing shows Nano Banana Pro.
- Batch submission partial failures do not make the batch safe to blindly retry. Resubmit only
  the failed indices.
- `generate_audio_batch` with `elevenlabs_v4` still requires a `prompt` field; any short string works.
