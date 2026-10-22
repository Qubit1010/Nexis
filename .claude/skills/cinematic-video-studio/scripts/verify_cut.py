"""Verify a built cut before anyone sees it.

    python -I verify_cut.py <film>/spec.json

Checks, and exits non-zero if any fail:
  1. duration matches the timeline;
  2. every clip shot actually appears where the timeline says: the frame at the shot's
     midpoint must resemble its source clip more than the end card. This catches the
     silent xfade fall-through, where everything after a broken transition shows the
     last input (it happened once: 30 seconds of end card where footage should be);
  3. integrated loudness lands near -16 LUFS (dialogue audible, nothing clipping);
  4. a voice line is actually audible in each window where the spec places one.
Writes <film>/verify-sheet.jpg (one frame per shot) for the human look that must follow.
"""
import json, re, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()
SZ = (54, 96)


def frame(path, t, ss_input=False, size=SZ):
    cmd = [FF, "-v", "error"] + (["-ss", f"{t:.3f}", "-i", str(path)] if ss_input else ["-i", str(path), "-ss", f"{t:.3f}"])
    cmd += ["-frames:v", "1", "-vf", f"scale={size[0]}:{size[1]}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = size[0] * size[1] * 3
    if len(raw) < n:
        return None
    return np.frombuffer(raw[:n], np.uint8).reshape(size[1], size[0], 3).astype(float)


def band(a):   # middle band: clear of the tag/labels/placeholder card above and captions/titles below
    return a[int(SZ[1] * 0.36): int(SZ[1] * 0.62)]


def main(spec_path):
    spec_path = Path(spec_path).resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    tl = json.loads((base / "timeline.json").read_text(encoding="utf-8"))
    out = base / spec["out"]
    starts, total = tl["starts"], tl["total"]
    fails = []

    info = subprocess.run([FF, "-i", str(out)], capture_output=True, text=True).stderr
    h, m, s = info.split("Duration: ")[1].split(",")[0].split(":")
    dur = int(h) * 3600 + int(m) * 60 + float(s)
    if abs(dur - total) > 0.25:
        fails.append(f"duration {dur:.2f}s vs timeline {total:.2f}s")

    shots = spec["shots"]
    end = next((s for s in shots if s.get("end_card") is not None), None)
    end_img = frame(out, starts[end["name"]] + end["dur"] - 0.5) if end else None
    sheet = []
    for s in shots:
        mid = starts[s["name"]] + s["dur"] / 2
        got = frame(out, mid)
        big = frame(out, mid, size=(216, 384))
        if big is not None:
            sheet.append(big)
        if not s.get("src") or got is None:
            continue
        src = Path(s["src"]) if Path(s["src"]).is_absolute() else (base / s["src"]).resolve()
        local = s.get("start", 0) + (s["dur"] / 2) * s.get("slow", 1)
        ref = frame(src, local, ss_input=True)
        if ref is None:
            fails.append(f"{s['name']}: cannot read source frame")
            continue
        d_src = np.abs(band(got) - band(ref)).mean()
        d_end = np.abs(band(got) - band(end_img)).mean() if end_img is not None else 999
        if d_src > 45 or d_src > d_end:
            fails.append(f"{s['name']}: frame at {mid:.1f}s does not match its clip (diff {d_src:.0f}, vs end card {d_end:.0f})")

    lo = subprocess.run([FF, "-i", str(out), "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lo)
    lufs = float(m[-1]) if m else None
    if lufs is None or not -19 <= lufs <= -13:
        fails.append(f"integrated loudness {lufs} LUFS (want about -16)")

    for ln in spec.get("lines", []):
        t0 = starts[ln["shot"]] + ln.get("at", 0)
        r = subprocess.run([FF, "-ss", f"{t0:.2f}", "-t", "1.5", "-i", str(out), "-af", "volumedetect", "-vn",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
        mv = re.findall(r"mean_volume: (-?[\d.]+) dB", r)
        if not mv or float(mv[-1]) < -40:
            fails.append(f"voice {ln['file']} at {t0:.1f}s seems silent ({mv[-1] if mv else 'n/a'} dB)")

    if sheet:
        cols = min(6, len(sheet))
        rows = (len(sheet) + cols - 1) // cols
        big = Image.new("RGB", (cols * 216, rows * 384))
        for i, a in enumerate(sheet):
            big.paste(Image.fromarray(a.astype(np.uint8)), ((i % cols) * 216, (i // cols) * 384))
        big.save(base / "verify-sheet.jpg", quality=85)

    print(f"{out.name}: {dur:.2f}s, {lufs} LUFS, {len(shots)} shots, {len(spec.get('lines', []))} voice lines")
    if fails:
        print("FAIL\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("PASS (now look at verify-sheet.jpg and spot-check the cut itself)")


if __name__ == "__main__":
    main(sys.argv[1])
