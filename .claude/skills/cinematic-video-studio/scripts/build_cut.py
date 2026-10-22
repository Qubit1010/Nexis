"""Build a cinematic 9:16 cut (1080x1920, 24 fps) from a film spec JSON + a client profile JSON.

    python -I build_cut.py <film>/spec.json [--draft]

--draft encodes fast (ultrafast, no grain) for a timing check; the default is the delivery
encode. Writes <film>/<spec.out>, then a smaller "-share" copy for messaging apps.
See references/spec-format.md for the spec and profile schemas.

How it works:
  * every shot is normalised to 1080x1920 @ 24 fps; non-final shots get a one-second frozen
    handle, because xfade drops the first input after the transition and a first input that
    ends early derails the whole chain (it silently falls through to the last shot);
  * transitions start on frame boundaries; a "cut" is a one-frame fade;
  * captions are timed to the voice lines, not to the shots, so a line can run across a cut;
  * the score (score.py) is cued to named shots and side-chain ducked under the voice.
"""
import argparse, json, subprocess, sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from overlay import Overlays, run, W, H  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 24
CUT = 1 / FPS


def media_dur(path):
    out = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True).stderr
    if "Duration: " not in out:
        sys.exit(f"Cannot read duration of {path} (missing or not media)")
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def timeline(shots):
    """Start time of each shot = its xfade offset (transitions overlap the previous shot)."""
    starts, length = {shots[0]["name"]: 0.0}, shots[0]["dur"]
    for s in shots[1:]:
        td = trans(s)[1]
        off = round((length - td) * FPS) / FPS
        starts[s["name"]], length = off, off + s["dur"]
    return starts, round(length, 3)


def trans(s):
    t = s.get("trans", ["cut"])
    kind, d = (t[0], t[1] if len(t) > 1 else 0.5)
    return ("fade", CUT) if kind == "cut" else (kind, d)


def shot_input(s, d, base, ov):
    """ffmpeg input args + filter chain for one shot, d seconds long."""
    if s["name"] == "black" or s.get("color"):
        return ["-f", "lavfi", "-t", str(d), "-i", f"color=c={s.get('color', 'black')}:s={W}x{H}:r={FPS}"], "null"
    if s.get("end_card") is not None:
        ec = s["end_card"] or {}
        png = ov.end_card(ec.get("extra_primary", ""), ec.get("extra_secondary", ""), ec.get("qr", False))
        return ["-loop", "1", "-framerate", str(FPS), "-t", str(d), "-i", str(png)], f"scale={W}:{H},format=yuv420p"
    src = Path(s["src"])
    src = src if src.is_absolute() else (base / src).resolve()
    if not src.exists():
        sys.exit(f"Missing clip for shot {s['name']}: {src}")
    f = (f"setpts=PTS/{s.get('slow', 1)},scale={W}:{H}:force_original_aspect_ratio=increase,"
         f"crop={W}:{H},fps={FPS}")
    if s.get("zoom_tail"):        # [t0, t1, amount, cx, cy]: push in from t0 to t1
        t0, t1, amount, cx, cy = s["zoom_tail"]
        f0, span = int(t0 * FPS), max(1, int((t1 - t0) * FPS))
        z = f"if(gte(in,{f0}),1+{amount}*pow(min((in-{f0})/{span},1),2),1)"
        f += (f",scale={W * 2}:{H * 2},zoompan=z='{z}':x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}'"
              f":d=1:s={W}x{H}:fps={FPS}")
    f += f",tpad=stop_mode=clone:stop_duration=2,trim=duration={d},setpts=PTS-STARTPTS,format=yuv420p"
    return ["-ss", str(s.get("start", 0)), "-i", str(src)], f


def finish_score(path, mutes, sfx):
    """Drop the music out in `mutes` windows (comic beats) and lay synthesized SFX into the score.

    SFX types: ping (phone notification), stamp (rubber-stamp thump), tick (clock), whoosh (swipe).
    They are synthesized here, so they are original and licence-safe like the score.
    """
    import wave
    import numpy as np
    with wave.open(str(path), "rb") as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(float) / 32767
    for a, b in mutes:
        i, j, r = int(a * sr), int(b * sr), int(0.15 * sr)
        x[i:j] *= 0
        if i - r > 0:
            x[i - r:i] *= np.linspace(1, 0, r)[:, None]
        x[j:j + r] *= np.linspace(0, 1, len(x[j:j + r]))[:, None]
    rng = np.random.default_rng(3)

    def tone(fs, d, decay):
        t = np.arange(int(d * sr)) / sr
        return sum(np.sin(2 * np.pi * f * t) for f in fs) / len(fs) * np.exp(-t * decay)

    for kind, t0, gain in sfx:
        if kind == "ping":
            s = np.concatenate([tone([1568, 3136], 0.12, 18), tone([2093, 4186], 0.3, 10)]) * 0.35
        elif kind == "stamp":
            n = int(0.18 * sr)
            s = (tone([70, 140], 0.18, 25) + rng.standard_normal(n) * np.exp(-np.arange(n) / sr * 60) * 0.4) * 0.6
        elif kind == "tick":
            n = int(0.02 * sr)
            s = rng.standard_normal(n) * np.exp(-np.arange(n) / sr * 300) * 0.25
        elif kind == "whoosh":
            n = int(0.6 * sr)
            s = rng.standard_normal(n) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.12
        else:
            sys.exit(f"Unknown sfx type: {kind}")
        i = int(t0 * sr)
        s = s[: max(0, len(x) - i)] * gain
        x[i:i + len(s)] += s[:, None]
    x /= max(1.0, np.abs(x).max() / 0.95)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def card_png(c, ov):
    k = c.get("kind", "html")
    if k == "title":
        return ov.title(c["primary"], c.get("secondary", ""))
    if k == "label":
        return ov.label(c["primary"], c.get("secondary", ""), c.get("top", 150))
    if k == "placeholder":
        return ov.placeholder(c["heading"], c.get("sub", ""), c.get("note", ""),
                              c.get("line_primary", ""), c.get("line_secondary", ""), c.get("who", ""))
    return ov.html(c["html"], c.get("css", ""))


def build(spec_path, draft=False):
    spec_path = Path(spec_path).resolve()
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    prof_path = (base / spec["profile"]).resolve()
    profile = json.loads(prof_path.read_text(encoding="utf-8"))
    ov = Overlays(profile, prof_path.parent)
    shots = spec["shots"]
    starts, total = timeline(shots)

    vo = []
    for ln in spec.get("lines", []):
        f = (base / ln["file"]).resolve()
        if not f.exists():
            sys.exit(f"Missing voice line: {f}")
        vo.append({**ln, "path": f, "t0": round(starts[ln["shot"]] + ln.get("at", 0), 3), "d": media_dur(f)})

    # score
    sc = spec.get("score", {})
    cue = lambda key: (starts[sc[key][0]] + sc[key][1]) if sc.get(key) else None   # noqa: E731
    cues = {"total": total, "breath": sc.get("breath", False), "waves": sc.get("waves", False),
            "micro": cue("swell_at") or total * 0.45, "surface": cue("resolve_at") or total - 8}
    if sc.get("heartbeat_from"):
        cues["dive"] = cue("heartbeat_from")
    score = ov.tmp / "score.wav"
    run([sys.executable, "-I", str(HERE / "score.py"), str(score), json.dumps(cues)])
    mutes = [(starts[m[0]] + m[1], starts[m[0]] + m[2]) for m in sc.get("mute", [])]
    sfx = [(e["type"], starts[e["shot"]] + e.get("at", 0), e.get("gain", 1.0)) for e in spec.get("sfx", [])]
    if mutes or sfx:
        finish_score(score, mutes, sfx)

    # overlays: tag, captions (faded, never overlapping), cards
    over = [(ov.tag(profile.get("tag", "CONCEPT CUT")), 0, total, False)]
    caps = [v for v in vo if v.get("primary")]
    for k, v in enumerate(caps):
        t1 = v["t0"] + v["d"] + 0.3
        if k + 1 < len(caps):
            t1 = min(t1, caps[k + 1]["t0"] - 0.05)
        over.append((ov.caption(v["primary"], v.get("secondary", ""), v.get("who", "")), v["t0"] - 0.1, t1, True))
    for c in spec.get("cards", []):
        over.append((card_png(c, ov), starts[c["shot"]] + c["from"], starts[c["shot"]] + c["to"], True))

    cmd, chains = [FF, "-y"], []
    for i, s in enumerate(shots):
        args, f = shot_input(s, s["dur"] + (1 if i < len(shots) - 1 else 0), base, ov)
        cmd += args
        chains.append(f"[{i}:v]{f},fps={FPS},settb=AVTB,setsar=1[v{i}]")
    last = "v0"
    for i, s in enumerate(shots[1:], start=1):
        kind, td = trans(s)
        chains.append(f"[{last}][v{i}]xfade=transition={kind}:duration={td:.4f}:offset={starts[s['name']]:.4f}[x{i}]")
        last = f"x{i}"
    grade = "eq=contrast=1.04:saturation=1.03,vignette=angle=PI/5" + ("" if draft else ",noise=alls=5:allf=t")
    chains.append(f"[{last}]{grade}[g]")
    last = "g"
    n_in = len(shots)
    for k, (p, t0, t1, fade) in enumerate(over):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(total), "-i", str(p)]
        fd = (f",fade=t=in:st={max(t0, 0):.3f}:d=0.3:alpha=1,fade=t=out:st={t1 - 0.3:.3f}:d=0.3:alpha=1"
              if fade else "")
        chains.append(f"[{n_in + k}:v]format=rgba{fd}[o{k}]")
        chains.append(f"[{last}][o{k}]overlay=0:0:enable='between(t,{max(t0, 0):.3f},{t1:.3f})'[y{k}]")
        last = f"y{k}"

    a0 = n_in + len(over)
    cmd += ["-i", str(score)]
    for v in vo:
        cmd += ["-i", str(v["path"])]
    if vo:
        for k, v in enumerate(vo):
            ms = int(v["t0"] * 1000)
            chains.append(f"[{a0 + 1 + k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[l{k}]")
        chains.append("".join(f"[l{k}]" for k in range(len(vo))) +
                      f"amix=inputs={len(vo)}:normalize=0,apad,atrim=0:{total},asplit=2[voa][vob]")
        chains.append(f"[{a0}:a]aresample=48000,atrim=0:{total}[sc]")
        chains.append("[sc][vob]sidechaincompress=threshold=0.03:ratio=5:attack=30:release=500[duck]")
        chains.append("[duck][voa]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]")
    else:
        chains.append(f"[{a0}:a]aresample=48000,atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11[a]")

    out = base / spec["out"]
    enc = ["-preset", "ultrafast", "-crf", "26"] if draft else ["-preset", "medium", "-crf", "19"]
    cmd += ["-filter_complex", ";".join(chains), "-map", f"[{last}]", "-map", "[a]", "-t", str(total),
            "-c:v", "libx264", *enc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", str(out)]
    run(cmd)
    if not draft:
        share = out.with_name(out.stem + "-share.mp4")
        run([FF, "-y", "-i", str(out), "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-maxrate", "6M",
             "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(share)])
    (base / "timeline.json").write_text(json.dumps({"total": total, "starts": starts}, indent=1), encoding="utf-8")
    print(f"{out}  ({total}s)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--draft", action="store_true")
    a = ap.parse_args()
    build(a.spec, a.draft)
