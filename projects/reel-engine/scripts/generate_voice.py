#!/usr/bin/env python
"""
generate_voice.py <slug> [--speed 0.82] [--device cuda|cpu]
                         [--chunk scene|sentence|none] [--ref PATH] [--ref-text "..."]
                         [--no-post] [--pitch-semitones -0.6] [--bass-db 3.8]

Generate the reel voiceover with a CLONED voice using OmniVoice (k2-fsa), so a
reel can render end-to-end without a manual ElevenLabs recording.

It reads `voiceScript` from public/reels/<slug>/content.json, synthesizes it in
the reference voice, applies the locked "heavy + warm" voice profile, and writes
the FINISHED public/reels/<slug>/voiceover.wav (24 kHz) — ready for prepare.mjs.

Defaults bake in the tuned recipe: per-scene chunking (natural period pauses, no
phantom filler words), 0.82 speed, 48 decoding steps, onset-protected seams, and
a pitch-down + low-shelf + loudness post-process. Override any of it via flags,
or pass --no-post for the raw cloned voice.

The reference voice is resolved in this order:
  1. --ref / --ref-text flags
  2. $REEL_VOICE_REF / $REEL_VOICE_REF_TEXT env vars
  3. voice/aleem-ref.wav (+ voice/aleem-ref.txt if present)
If no reference transcript is found, OmniVoice auto-transcribes the clip with
Whisper, so aleem-ref.txt is optional.

ElevenLabs stays as a fallback: if you instead drop a manual voiceover.mp3 into
the reel folder, prepare.mjs prefers it over this generated wav.

Run AFTER content.json is written + validated, then:
  node scripts/prepare.mjs <slug>
"""
import argparse
import os
import re
import sys
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE = 24000  # OmniVoice output rate

# --- Defaults: the locked "Aleem reel voice" recipe (tuned + approved) ---
DEFAULT_SPEED = 0.82       # measured, natural reel pace
DEFAULT_NUM_STEP = 48      # cleaner than the model's default 32
DEFAULT_CHUNK = "scene"    # per-scene = natural period pauses, no phantom fillers
GAP_SECONDS = 0.42         # silence between scene chunks
LEAD_PAD_MS = 30           # silent pad prepended to each chunk; the fade-in ramps over THIS,
                           # not over speech, so the first word is never clipped/half-spoken
FADE_OUT_MS = 60           # ease each chunk out so it decays into the pause (no hiccup)

# Post-process "heavy + warm" profile (ffmpeg). Applied unless --no-post.
DEFAULT_PITCH_SEMITONES = -0.6   # slight drop = heavier voice
DEFAULT_BASS_DB = 3.8            # low-shelf depth/warmth
DEFAULT_LOUDNESS_LUFS = -14.5    # normalized loudness

# Pronunciation map: words the cloned voice mis-says, respelled phonetically for the
# TTS ONLY (display text + captions keep the real spelling). "Claude" otherwise comes
# out as "code/cloud" and collapses "Claude Code" into "code code". Extend by editing
# scripts/pronunciation.json (merged over these built-in defaults).
DEFAULT_PRONUNCIATION = {"Claude": "Clawd"}


def smooth_chunk(wav, sr, lead_pad_ms, fade_out_ms):
    """Prepend a silent pad and fade it in (protects the word onset), fade the tail out."""
    wav = wav.copy()
    pad_n = int(sr * lead_pad_ms / 1000)
    if pad_n > 0:
        wav = np.concatenate([np.zeros(pad_n, dtype=np.float32), wav])
        # ramp 0->1 across the silent pad so speech starts at full level, uncut
        wav[:pad_n] *= np.linspace(0.0, 1.0, pad_n, dtype=np.float32)
    n_out = min(len(wav), int(sr * fade_out_ms / 1000))
    if n_out > 0:
        wav[-n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)
    return wav

ROOT = Path(__file__).resolve().parent.parent


def _ffmpeg_bin():
    cand = ROOT / "node_modules" / "ffmpeg-static" / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    return str(cand) if cand.exists() else "ffmpeg"


def load_pronunciation():
    """Built-in defaults merged with scripts/pronunciation.json (if present)."""
    mapping = dict(DEFAULT_PRONUNCIATION)
    p = Path(__file__).resolve().parent / "pronunciation.json"
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                mapping.update({str(k): str(v) for k, v in data.items()})
        except Exception as e:  # noqa: BLE001
            log(f"  ⚠ could not read pronunciation.json ({e}); using built-in defaults")
    return mapping


def apply_pronunciation(text, mapping):
    """Respell mapped words (whole-word, case-insensitive) for the TTS input only."""
    out = text
    for key, val in mapping.items():
        out = re.sub(rf"\b{re.escape(key)}\b", val, out, flags=re.IGNORECASE)
    return out


def post_process(wav_path, pitch_semitones, bass_db, loudness_lufs):
    """Apply the heavy+warm voice profile in place: pitch-down (tempo-preserved),
    low-shelf depth, gentle presence, loudness normalization."""
    factor = 2 ** (pitch_semitones / 12.0)  # <1 lowers pitch
    af = (
        f"asetrate={SAMPLE_RATE}*{factor:.5f},aresample={SAMPLE_RATE},atempo={1/factor:.5f},"
        f"bass=g={bass_db}:f=120:w=0.5,"
        f"equalizer=f=90:width_type=q:w=0.8:g=1.5,"
        f"treble=g=1.5:f=4000:w=0.6,"
        f"loudnorm=I={loudness_lufs}:TP=-1.5:LRA=11"
    )
    tmp = str(wav_path) + ".post.wav"
    subprocess.run(
        [_ffmpeg_bin(), "-i", str(wav_path), "-af", af, "-ar", str(SAMPLE_RATE), "-ac", "1", tmp, "-y"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.replace(tmp, str(wav_path))


def log(msg):
    print(msg, flush=True)


def resolve_reference(args):
    """Return (ref_audio_path, ref_text_or_None)."""
    ref = args.ref or os.environ.get("REEL_VOICE_REF")
    ref_text = args.ref_text or os.environ.get("REEL_VOICE_REF_TEXT")

    if not ref:
        default_ref = ROOT / "voice" / "aleem-ref.wav"
        if default_ref.exists():
            ref = str(default_ref)
        else:
            log(
                "No reference voice found.\n"
                f"  Provide one via --ref, $REEL_VOICE_REF, or place a 3-10s clip at\n"
                f"  {default_ref}\n"
                "  (see .claude/skills/reel-creator/references/voice-cloning.md)"
            )
            sys.exit(1)

    if not Path(ref).exists():
        log(f"Reference audio not found: {ref}")
        sys.exit(1)

    # Optional sidecar transcript next to the default ref clip.
    if not ref_text:
        default_txt = ROOT / "voice" / "aleem-ref.txt"
        if default_txt.exists():
            ref_text = default_txt.read_text(encoding="utf-8").strip()

    return ref, (ref_text or None)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def build_chunks(content, mode):
    script = content["voiceScript"].strip()
    if mode == "none":
        return [script]
    if mode == "scene":
        chunks = [s["voiceText"].strip() for s in content["scenes"] if s.get("voiceText", "").strip()]
        return chunks or [script]
    if mode == "sentence":
        sents = split_sentences(script)
        # Merge very short sentences (< 4 words) into the previous chunk. Isolated
        # tiny generations make OmniVoice prepend a phantom filler word (e.g. a
        # stray "Just" before "Follow for more."); kept together it reads cleanly
        # with the model's own natural pause at the period.
        merged = []
        for s in sents:
            if merged and len(s.split()) < 4:
                merged[-1] = merged[-1] + " " + s
            else:
                merged.append(s)
        return merged
    raise ValueError(f"unknown chunk mode: {mode}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--speed", type=float, default=DEFAULT_SPEED,
                    help=f"speaking rate; >1 faster, <1 slower (default {DEFAULT_SPEED})")
    ap.add_argument("--device", choices=["cuda", "cpu"], default=None,
                    help="default: cuda if available, else cpu")
    ap.add_argument("--chunk", choices=["scene", "sentence", "none"], default=DEFAULT_CHUNK,
                    help=f"how to split text (default: {DEFAULT_CHUNK}; scene = natural period pauses, no phantom fillers)")
    ap.add_argument("--gap", type=float, default=GAP_SECONDS,
                    help=f"silence (s) inserted between chunks for breathing room (default {GAP_SECONDS})")
    ap.add_argument("--lead-pad-ms", type=float, default=LEAD_PAD_MS,
                    help=f"silent pad before each chunk; fade-in ramps over it so the first word is never clipped (default {LEAD_PAD_MS})")
    ap.add_argument("--fade-out-ms", type=float, default=FADE_OUT_MS,
                    help=f"per-chunk fade-out so speech decays into the pause (default {FADE_OUT_MS})")
    ap.add_argument("--ref", default=None)
    ap.add_argument("--ref-text", default=None)
    # Voice-quality knobs (passed to OmniVoice generation config).
    ap.add_argument("--language", default="English",
                    help="target language; slightly better quality when set (default: English)")
    ap.add_argument("--num-step", type=int, default=DEFAULT_NUM_STEP,
                    help=f"decoding steps; higher = cleaner/slower (default {DEFAULT_NUM_STEP})")
    ap.add_argument("--guidance", type=float, default=None,
                    help="guidance scale; higher = closer to your voice (default 2.0; try 2.5-3.0)")
    ap.add_argument("--temperature", type=float, default=None,
                    help="sampling temp; 0 = consistent/greedy, higher = more expressive/varied (default 0.0)")
    ap.add_argument("--no-denoise", action="store_true",
                    help="disable reference denoising (keep on for noisy clips)")
    # Post-process voice profile (ffmpeg). Defaults bake in the approved heavy+warm sound.
    ap.add_argument("--no-post", action="store_true",
                    help="skip the heavy+warm post-process (raw cloned voice)")
    ap.add_argument("--pitch-semitones", type=float, default=DEFAULT_PITCH_SEMITONES,
                    help=f"pitch shift; negative = heavier (default {DEFAULT_PITCH_SEMITONES})")
    ap.add_argument("--bass-db", type=float, default=DEFAULT_BASS_DB,
                    help=f"low-shelf depth/warmth in dB (default {DEFAULT_BASS_DB})")
    ap.add_argument("--loudness-lufs", type=float, default=DEFAULT_LOUDNESS_LUFS,
                    help=f"normalized loudness target (default {DEFAULT_LOUDNESS_LUFS})")
    args = ap.parse_args()

    reel_dir = ROOT / "public" / "reels" / args.slug
    content_path = reel_dir / "content.json"
    if not content_path.exists():
        log(f"Missing {content_path}. Write + validate content.json first.")
        sys.exit(1)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    if not content.get("voiceScript", "").strip():
        log(f"{content_path} has no voiceScript.")
        sys.exit(1)

    ref_audio, ref_text = resolve_reference(args)

    # Torch / device selection.
    import torch  # imported here so --help works without the heavy deps
    device = args.device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        log("CUDA requested but not available; falling back to CPU.")
        device = "cpu"
    device_map = "cuda:0" if device == "cuda" else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    log(f"→ Loading OmniVoice on {device_map} ({dtype})... (first run downloads weights from HuggingFace)")
    from omnivoice import OmniVoice
    model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=device_map, dtype=dtype)

    # Optional generation-config overrides (None values are simply not passed).
    gen_kwargs = {"denoise": not args.no_denoise}
    if args.num_step is not None:
        gen_kwargs["num_step"] = args.num_step
    if args.guidance is not None:
        gen_kwargs["guidance_scale"] = args.guidance
    if args.temperature is not None:
        gen_kwargs["class_temperature"] = args.temperature

    pron = load_pronunciation()
    chunks = build_chunks(content, args.chunk)
    # Scene ids parallel to the chunks (scene mode only), so we can emit chunks.json
    # mapping each scene to its exact audio span — preflight uses it for rock-solid
    # scene anchoring + seam-gap windows.
    scene_ids = None
    if args.chunk == "scene":
        ids = [s["id"] for s in content["scenes"] if s.get("voiceText", "").strip()]
        if len(ids) == len(chunks):
            scene_ids = ids
    log(f"→ Synthesizing {len(chunks)} chunk(s) in cloned voice (ref: {Path(ref_audio).name}, transcript: {'auto' if not ref_text else 'provided'})...")

    gap = np.zeros(int(SAMPLE_RATE * max(0.0, args.gap)), dtype=np.float32)
    pieces = []
    offsets = []  # (start_sample, end_sample) per chunk in the pre-post concatenation
    cursor = 0
    for i, chunk in enumerate(chunks, 1):
        log(f"   [{i}/{len(chunks)}] {chunk[:60]}{'...' if len(chunk) > 60 else ''}")
        spoken = apply_pronunciation(chunk, pron)  # respell hard words for the TTS only
        audio = model.generate(
            text=spoken,
            language=args.language,
            ref_audio=ref_audio,
            ref_text=ref_text,
            speed=args.speed,
            **gen_kwargs,
        )
        wav = np.asarray(audio[0], dtype=np.float32)
        # Smooth seams only when there's more than one chunk: pad+fade-in protects
        # the next word's onset; fade-out decays cleanly into the silent gap.
        if len(chunks) > 1:
            wav = smooth_chunk(wav, SAMPLE_RATE, args.lead_pad_ms, args.fade_out_ms)
        start = cursor
        pieces.append(wav)
        cursor += len(wav)
        offsets.append((start, cursor))
        if i < len(chunks):
            pieces.append(gap)
            cursor += len(gap)

    full = np.concatenate(pieces) if len(pieces) > 1 else pieces[0]
    pre_post_frames = len(full)
    out_path = reel_dir / "voiceover.wav"
    sf.write(str(out_path), full, SAMPLE_RATE)

    if not args.no_post:
        log(f"→ Post-processing (pitch {args.pitch_semitones:+g} st, bass +{args.bass_db}dB, {args.loudness_lufs} LUFS)...")
        post_process(out_path, args.pitch_semitones, args.bass_db, args.loudness_lufs)

    # Emit chunks.json: exact per-scene audio spans (scene mode). Post-process is
    # duration-preserving (atempo cancels asetrate), but scale by the measured
    # ratio just in case so the offsets stay valid against the final wav.
    if scene_ids:
        final_frames = sf.info(str(out_path)).frames
        scale = (final_frames / pre_post_frames) if pre_post_frames else 1.0
        chunk_meta = []
        for sid, (s0, s1) in zip(scene_ids, offsets):
            a, b = int(round(s0 * scale)), int(round(s1 * scale))
            chunk_meta.append({
                "sceneId": sid,
                "startSample": a, "endSample": b,
                "startMs": round(a / SAMPLE_RATE * 1000, 1),
                "endMs": round(b / SAMPLE_RATE * 1000, 1),
            })
        (reel_dir / "chunks.json").write_text(
            json.dumps({"sampleRate": SAMPLE_RATE, "gapMs": round(args.gap * 1000, 1), "scenes": chunk_meta}, indent=2),
            encoding="utf-8",
        )

    info = sf.info(str(out_path))
    dur = info.frames / info.samplerate
    log(f"\n✓ Wrote {out_path.relative_to(ROOT)} ({dur:.1f}s @ {SAMPLE_RATE} Hz)")
    if dur > 52:
        log(f"  ⚠ {dur:.1f}s is over the 40-50s target. Re-run with --speed 0.9, or trim the script.")
    log("\nNext:")
    log(f"  node scripts/prepare.mjs {args.slug}")


if __name__ == "__main__":
    main()
