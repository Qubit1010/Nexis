#!/usr/bin/env python
"""
preflight.py <slug> [--fix] [--dry-run] [--fix-head] [--restore] [--force]

QA gate between prepare.mjs and render. We HAVE the ground-truth text
(content.json voiceScript == concat of scenes[].voiceText). Whisper is only
needed for TIMING. So this:

  1. Aligns the ground-truth words against the Whisper transcript (captions.json).
  2. Rebuilds captions.json from the GROUND TRUTH (correct spelling/casing always),
     using Whisper's timing -> fixes every mis-hear, split ("a"+"i"->"AI",
     "car"+"work"->"Cowork", CODCODES->"Claude Code's"), and lowercasing at once.
  3. Audio surgery (RMS): trims audible phantom "ah"/"Just"/"Yes" words at the
     head/seams, restores a dropped "Follow for more" tail (+ extends the timeline
     so it isn't clipped), and (only when unambiguous) trims a garbled first word.
  4. Recomputes scene cuts from chunks.json (exact) or the alignment.
  5. Triple-checks text + audio + sync and writes preflight.json (the render gate
     marker). Exits non-zero if anything is unresolved.

Modes: default = report only (writes nothing, exits non-zero on FAIL).
  --fix       apply auto-fixes.
  --dry-run   with --fix: print planned mutations, write nothing.
  --fix-head  allow trimming a suspected garbled first word even if not unambiguous.
  --restore   revert voiceover.wav / captions.json / timeline.json from .bak.
  --force     lift the blast-radius cap (>2 trims or >1.0s total).

Run: .venv/Scripts/python.exe scripts/preflight.py <slug> --fix
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

VERSION = 3
FPS = 30
ROOT = Path(__file__).resolve().parent.parent

# ---- text normalization (mirrors prepare.mjs norm) + number canonicalization ----
_NUM = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50",
    "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90",
    "hundred": "100", "thousand": "1000", "million": "1000000", "billion": "1000000000",
}


def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9']", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def canon_keys(surface):
    """Normalize one surface token to a list of alignment keys (handles % and number words)."""
    s = surface.lower().replace("%", " percent ")
    out = []
    for w in norm(s).split():
        out.append(_NUM.get(w, w))
    return out


# ------------------------------- data classes -------------------------------
class GTWord:
    __slots__ = ("surface", "keys", "scene_id", "scene_local", "start", "end", "matched", "dropped")

    def __init__(self, surface, scene_id, scene_local):
        self.surface = surface
        self.keys = canon_keys(surface)
        self.scene_id = scene_id
        self.scene_local = scene_local  # index within its scene (0 = scene's first word)
        self.start = None
        self.end = None
        self.matched = False
        self.dropped = False  # head-trimmed away


class HypTok:
    __slots__ = ("surface", "keys", "start", "end", "conf")

    def __init__(self, surface, start, end, conf):
        self.surface = surface
        self.keys = canon_keys(surface)
        self.start = start
        self.end = end
        self.conf = conf


def log(m=""):
    print(m, flush=True)


# ------------------------------- loading -------------------------------
def build_gt(content):
    words = []
    for sc in content["scenes"]:
        vt = (sc.get("voiceText") or "").strip()
        if not vt:
            continue
        for li, surf in enumerate(vt.split()):
            words.append(GTWord(surf, sc["id"], li))
    return words


def build_hyp(captions):
    # merge apostrophe-leading fragments ("doesn"+"'t") and pure-punctuation tokens
    toks = []
    for c in captions:
        t = c.get("text", "")
        stripped = t.strip()
        is_punct = norm(t) == ""
        if toks and (stripped.startswith("'") or is_punct):
            prev = toks[-1]
            prev.surface = prev.surface + t
            prev.end = c.get("endMs", prev.end)
            prev.keys = canon_keys(prev.surface)
            continue
        toks.append(HypTok(t, c.get("startMs", 0), c.get("endMs", 0), c.get("confidence", 1.0)))
    return [t for t in toks if t.keys]  # drop tokens with no alignable key


# ------------------------------- audio (RMS) -------------------------------
class Audio:
    def __init__(self, wav_path):
        a, sr = sf.read(str(wav_path))
        if a.ndim > 1:
            a = a.mean(axis=1)
        self.a = a.astype(np.float32)
        self.sr = sr
        self.dur_ms = len(a) / sr * 1000.0
        hop = int(sr * 0.02)
        win = int(sr * 0.04)
        n = max(1, (len(a) - win) // hop + 1) if len(a) >= win else 1
        rms = np.empty(n, dtype=np.float32)
        for i in range(n):
            seg = a[i * hop:i * hop + win]
            rms[i] = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        self.hop_ms = hop / sr * 1000.0
        self.rms = rms
        nz = rms[rms > 1e-5]
        floor = float(np.percentile(nz, 10)) if len(nz) else 0.0
        p50 = float(np.percentile(rms, 50)) if len(rms) else 0.0
        self.t_speech = max(floor * 4.0, p50 * 0.15, 1e-4)

    def _slice(self, t0, t1):
        i0 = max(0, int(t0 / self.hop_ms))
        i1 = min(len(self.rms), int(t1 / self.hop_ms) + 1)
        return self.rms[i0:i1] if i1 > i0 else np.array([0.0], dtype=np.float32)

    def peak(self, t0, t1):
        return float(np.max(self._slice(t0, t1)))

    def voiced_fraction(self, t0, t1):
        s = self._slice(t0, t1)
        return float(np.mean(s >= self.t_speech)) if len(s) else 0.0

    def is_voiced(self, t0, t1):
        return self.peak(t0, t1) >= self.t_speech and self.voiced_fraction(t0, t1) >= 0.3

    def last_voiced_end(self):
        """End time (ms) of the last hop at/above speech threshold."""
        idx = np.where(self.rms >= self.t_speech)[0]
        return float((idx[-1] + 1) * self.hop_ms) if len(idx) else 0.0

    def voiced_after(self, t):
        """Return (start_ms, end_ms) of the next voiced region after t, or None."""
        i0 = int(t / self.hop_ms)
        above = self.rms >= self.t_speech
        start = None
        for i in range(max(0, i0), len(self.rms)):
            if above[i] and start is None:
                start = i
            elif not above[i] and start is not None:
                if (i - start) * self.hop_ms >= 120:
                    return (start * self.hop_ms, i * self.hop_ms)
                start = None
        if start is not None:
            return (start * self.hop_ms, len(self.rms) * self.hop_ms)
        return None


# ------------------------------- alignment -------------------------------
def align(gt, hyp):
    """Flatten to per-key streams, run difflib, return opcodes over flat indices
    plus back-pointers (flat key -> gt word index / hyp tok index + subindex)."""
    gt_keys, gt_ptr = [], []
    for gi, w in enumerate(gt):
        for k in w.keys:
            gt_keys.append(k)
            gt_ptr.append(gi)
    hyp_keys, hyp_ptr = [], []
    for hi, t in enumerate(hyp):
        for ki in range(len(t.keys)):
            hyp_keys.append(t.keys[ki])
            hyp_ptr.append(hi)
    sm = difflib.SequenceMatcher(None, gt_keys, hyp_keys, autojunk=False)
    return sm.get_opcodes(), gt_ptr, hyp_ptr, gt_keys, hyp_keys


# ------------------------------- main fix logic -------------------------------
def planned_times_from_hyp_block(gt_block, hyp_toks):
    """Distribute the hyp block's [start,end] span across gt_block words by char length."""
    if not hyp_toks:
        return
    t0 = hyp_toks[0].start
    t1 = max(t.end for t in hyp_toks)
    if t1 <= t0:
        t1 = t0 + 1
    weights = [max(1, len(w.surface)) for w in gt_block]
    total = sum(weights)
    cur = t0
    for w, wt in zip(gt_block, weights):
        span = (t1 - t0) * (wt / total)
        w.start = cur
        w.end = cur + span
        w.matched = True
        cur += span


def assign_and_classify(gt, hyp):
    opcodes, gt_ptr, hyp_ptr, gt_keys, hyp_keys = align(gt, hyp)
    relabels = []   # (hyp_surfaces, gt_surfaces) for report
    phantoms = []   # hyp token indices that are inserts (no GT)
    interior_deletes = []
    tail_delete_gis = []

    def gt_words_for(i1, i2):
        gis = sorted(set(gt_ptr[i] for i in range(i1, i2)))
        return [gt[gi] for gi in gis]

    def hyp_toks_for(j1, j2):
        his = sorted(set(hyp_ptr[j] for j in range(j1, j2)))
        return his, [hyp[hi] for hi in his]

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            # assign each gt key's word the time of the matching hyp token
            for off in range(i2 - i1):
                gi = gt_ptr[i1 + off]
                hi = hyp_ptr[j1 + off]
                w, t = gt[gi], hyp[hi]
                if not w.matched:
                    w.start, w.end, w.matched = t.start, t.end, True
                else:
                    w.end = t.end
        elif tag == "replace":
            gblock = gt_words_for(i1, i2)
            his, hblock = hyp_toks_for(j1, j2)
            planned_times_from_hyp_block(gblock, hblock)
            relabels.append(([h.surface.strip() for h in hblock], [w.surface for w in gblock]))
        elif tag == "delete":
            gis = sorted(set(gt_ptr[i] for i in range(i1, i2)))
            if i2 >= len(gt_keys):  # trailing delete -> dropped tail
                tail_delete_gis.extend(gis)
            else:
                interior_deletes.extend(gis)
        elif tag == "insert":
            his = sorted(set(hyp_ptr[j] for j in range(j1, j2)))
            phantoms.extend(his)

    return {
        "relabels": relabels, "phantoms": phantoms,
        "interior_deletes": interior_deletes, "tail_delete_gis": tail_delete_gis,
    }


def merge_trims(trims):
    trims = sorted(trims)
    out = []
    for a, b in trims:
        if out and a <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def remap_factory(trims):
    def remap(t):
        cut = 0.0
        for a, b in trims:
            if t >= b:
                cut += (b - a)
            elif t > a:
                cut += (t - a)
        return t - cut
    return remap


def cut_wav(a, sr, trims_ms):
    """Return wav with [t0,t1] intervals removed, 5ms equal-power crossfade at splices."""
    xf = int(sr * 0.005)
    keep_bounds = []
    prev = 0
    for a0, a1 in trims_ms:
        s0, s1 = int(round(a0 / 1000 * sr)), int(round(a1 / 1000 * sr))
        keep_bounds.append((prev, max(prev, s0)))
        prev = min(len(a), s1)
    keep_bounds.append((prev, len(a)))
    segs = [a[s:e] for s, e in keep_bounds if e > s]
    if not segs:
        return a
    out = segs[0]
    for seg in segs[1:]:
        if xf > 0 and len(out) >= xf and len(seg) >= xf:
            fade = np.linspace(0, 1, xf, dtype=np.float32)
            tail = out[-xf:] * (1 - fade)
            head = seg[:xf] * fade
            out = np.concatenate([out[:-xf], tail + head, seg[xf:]])
        else:
            out = np.concatenate([out, seg])
    return out


def scene_windows(content, chunks, gt, remap):
    """Return list of (sceneId, startMs) in final (post-trim) coords."""
    ids = [s["id"] for s in content["scenes"] if (s.get("voiceText") or "").strip()]
    if chunks and len(chunks.get("scenes", [])) == len(ids):
        return [(c["sceneId"], remap(c["startMs"])) for c in chunks["scenes"]]
    # fallback: first matched word of each scene
    out = []
    seen = set()
    for w in gt:
        if w.scene_id not in seen and w.scene_local == 0 and w.matched and not w.dropped:
            out.append((w.scene_id, remap(w.start)))
            seen.add(w.scene_id)
    # ensure all scenes present + first at 0
    if out:
        out[0] = (out[0][0], 0.0)
    return out


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fix-head", action="store_true")
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    d = ROOT / "public" / "reels" / args.slug
    p_content = d / "content.json"
    p_caps = d / "captions.json"
    p_tl = d / "timeline.json"
    p_chunks = d / "chunks.json"
    p_wav = d / "voiceover.wav"
    p_mark = d / "preflight.json"

    for p in (p_content, p_caps, p_wav):
        if not p.exists():
            log(f"FAIL: missing {p.name} (run prepare.mjs first).")
            sys.exit(2)

    if args.restore:
        n = 0
        for p in (p_wav, p_caps, p_tl):
            bak = Path(str(p) + ".bak")
            if bak.exists():
                shutil.copy(bak, p)
                n += 1
        log(f"Restored {n} file(s) from .bak.")
        sys.exit(0)

    content = json.loads(p_content.read_text(encoding="utf-8"))
    captions = json.loads(p_caps.read_text(encoding="utf-8"))
    chunks = json.loads(p_chunks.read_text(encoding="utf-8")) if p_chunks.exists() else None

    # idempotency gate: already passed + nothing changed -> exit 0
    if p_mark.exists() and not args.dry_run:
        try:
            mk = json.loads(p_mark.read_text(encoding="utf-8"))
            if (mk.get("passed") and mk.get("version") == VERSION
                    and mk.get("wav_sha256") == sha(p_wav)
                    and mk.get("captions_sha") == sha(p_caps)
                    and mk.get("timeline_sha") == sha(p_tl)):
                log(f"✓ preflight: {args.slug} already passed (unchanged). Nothing to do.")
                sys.exit(0)
        except Exception:
            pass

    gt = build_gt(content)
    hyp = build_hyp(captions)
    audio = Audio(p_wav)

    # ground-truth integrity
    gt_concat = norm(" ".join(w.surface for w in gt))
    script_norm = norm(content.get("voiceScript", ""))
    fails, warns, fixes = [], [], []
    if gt_concat != script_norm:
        fails.append("scenes[].voiceText concat != voiceScript (content.json is inconsistent).")

    cls = assign_and_classify(gt, hyp)

    # ---- decide audio trims (head garbled + voiced seam/head phantoms) ----
    durs = [w.end - w.start for w in gt if w.matched and w.end and w.start is not None and w.end > w.start]
    med = float(np.median(durs)) if durs else 300.0
    # Boundary times where per-scene chunking plants phantoms: each chunk's start +
    # end (a phantom rides the tail of one chunk or the head of the next).
    boundaries = []
    if chunks:
        for c in chunks["scenes"]:
            boundaries.extend([c["startMs"], c["endMs"]])
    SEAM_PAD = 500  # ms tolerance to a chunk boundary

    def in_seam(t):
        if t < 700:
            return True
        return any(abs(t - b) <= SEAM_PAD for b in boundaries)

    trims = []
    head_drop_gis = set()

    # voiced phantom inserts -> trim; silent -> just drop from captions (rebuild ignores them)
    for hi in cls["phantoms"]:
        t = hyp[hi]
        voiced = audio.is_voiced(t.start, t.end)
        if voiced and in_seam((t.start + t.end) / 2):
            trims.append((max(0, t.start - 20), t.end + 20))
            fixes.append(f"trim phantom '{t.surface.strip()}' [{t.start:.0f}-{t.end:.0f}ms]")
        elif voiced:
            fails.append(f"voiced phantom '{t.surface.strip()}' at {t.start:.0f}ms is mid-speech (not a seam) — likely a missing script word; not auto-trimmed.")
        else:
            fixes.append(f"drop hallucinated caption '{t.surface.strip()}' (silent)")

    # garbled first word: leading interior/tail delete OR low-conf+long first token
    if gt and hyp:
        first = gt[0]
        first_tok = hyp[0]
        leading_delete = (not first.matched) or (0 in cls["interior_deletes"]) or (0 in cls["tail_delete_gis"])
        first_dur = (first_tok.end - first_tok.start)
        anomalous = first_dur > 2.5 * med and first_tok.start < 700
        low_conf = first_tok.conf is not None and first_tok.conf < 0.5
        if (leading_delete and anomalous) or (args.fix_head and anomalous):
            # trim to the first clean speech onset after the anomaly
            vr = audio.voiced_after(first_tok.end)
            cut_to = vr[0] if vr else first_tok.end
            trims.append((0, cut_to))
            head_drop_gis.add(0)
            fixes.append(f"trim garbled first word (to {cut_to:.0f}ms); '{first.surface}' dropped from script")
        elif anomalous or leading_delete:
            warns.append(f"possible garbled first word '{first.surface}' (dur {first_dur:.0f}ms, conf {first_tok.conf}). Not auto-trimmed; pass --fix-head to cut, or re-listen.")

    trims = merge_trims([(a, b) for a, b in trims if b > a])
    total_trim = sum(b - a for a, b in trims)
    if not args.force and (len(trims) > 2 or total_trim > 1000):
        fails.append(f"blast-radius cap: {len(trims)} trims / {total_trim:.0f}ms total — refuse without --force.")

    remap = remap_factory(trims)

    # mark head-dropped GT words (those fully inside a head trim) and remap times
    for gi in head_drop_gis:
        gt[gi].dropped = True
    for w in gt:
        if w.matched and w.start is not None:
            if any(a <= w.start and w.end <= b for a, b in trims):
                w.dropped = True
            else:
                w.start, w.end = remap(w.start), remap(w.end)

    # ---- dropped tail: synthesize timing for unmatched trailing GT words ----
    tail_gis = [gi for gi in cls["tail_delete_gis"] if not gt[gi].dropped]
    tail_ok = True
    speech_end = audio.last_voiced_end()  # original coords
    speech_end = remap(speech_end)
    if tail_gis:
        matched_before = [w for w in gt if w.matched and not w.dropped and w.end]
        last_end = max((w.end for w in matched_before), default=0.0)
        vr = audio.voiced_after(max(0.0, last_end))  # post-trim wav not yet written; approx on original
        # approximate: detect any speech beyond last matched word end (remapped original env)
        if speech_end > last_end + 80:
            tail_words = [gt[gi] for gi in tail_gis]
            wsum = sum(max(1, len(w.surface)) for w in tail_words)
            cur = last_end + 120
            span_total = max(120.0, speech_end - cur)
            for w in tail_words:
                seg = span_total * (max(1, len(w.surface)) / wsum)
                w.start, w.end, w.matched = cur, cur + seg, True
                cur += seg
            fixes.append(f"restore dropped tail: {' '.join(w.surface for w in tail_words)}")
        else:
            tail_ok = False
            fails.append(f"tail words {[gt[gi].surface for gi in tail_gis]} not found in audio (script/audio mismatch).")

    # interior deletes (rare): interpolate
    for gi in cls["interior_deletes"]:
        w = gt[gi]
        if w.dropped or w.matched:
            continue
        prev_end = max((gt[k].end for k in range(gi) if gt[k].matched and not gt[k].dropped and gt[k].end), default=0.0)
        nxt = next((gt[k].start for k in range(gi + 1, len(gt)) if gt[k].matched and not gt[k].dropped and gt[k].start is not None), prev_end + med)
        w.start, w.end, w.matched = prev_end, min(nxt, prev_end + med), True
        warns.append(f"interior word '{w.surface}' had no transcript token; interpolated timing.")

    # ---------------- report ----------------
    kept = [w for w in gt if not w.dropped]
    relabel_n = len(cls["relabels"])
    log(f"── preflight: {args.slug} ──")
    log(f"  ground-truth words: {len(gt)} | hyp tokens: {len(hyp)} | audio {audio.dur_ms/1000:.2f}s | chunks.json: {'yes' if chunks else 'no'}")
    if cls["relabels"]:
        log(f"  relabel (caption text -> script): {relabel_n} block(s)")
        for hs, gs in cls["relabels"][:12]:
            log(f"     '{' '.join(hs)}' -> '{' '.join(gs)}'")
    for f in fixes:
        log(f"  fix: {f}")
    for w in warns:
        log(f"  WARN: {w}")
    for f in fails:
        log(f"  FAIL: {f}")

    if not args.fix:
        log("\n(report only — pass --fix to apply)")
        sys.exit(2 if fails else 0)

    if fails:
        log("\nFAIL: unresolved issues above — not writing. Fix and re-run.")
        sys.exit(2)

    # ---------------- build outputs ----------------
    new_caps = []
    for idx, w in enumerate(kept):
        if w.start is None or w.end is None:
            continue
        text = w.surface if idx == 0 else " " + w.surface
        new_caps.append({
            "text": text,
            "startMs": int(round(w.start)),
            "endMs": int(round(w.end)),
            "timestampMs": int(round(w.end)),
            "confidence": 0.99,
        })

    # timeline from scene windows (post-trim)
    sw = scene_windows(content, chunks, gt, remap)
    final_dur_ms = audio.dur_ms - total_trim
    tail_end = speech_end if tail_gis and tail_ok else (max((w.end for w in kept if w.end), default=final_dur_ms))
    duration_ms = int(min(final_dur_ms, max(tail_end + 600, max((c["endMs"] for c in new_caps), default=0) + 200)))
    duration_ms = max(duration_ms, int(max((c["endMs"] for c in new_caps), default=0)) + 100)
    duration_frames = int(np.ceil(duration_ms / 1000 * FPS))
    scenes_out = []
    for i, (sid, st) in enumerate(sw):
        sf_ = int(round(st / 1000 * FPS))
        ef = int(round(sw[i + 1][1] / 1000 * FPS)) if i + 1 < len(sw) else duration_frames
        scenes_out.append({"sceneId": sid, "startFrame": max(0, sf_), "endFrame": ef})
    timeline = {"fps": FPS, "durationInFrames": duration_frames, "durationMs": duration_ms, "aligned": True, "scenes": scenes_out}

    if args.dry_run:
        log("\n[dry-run] would write captions.json / timeline.json" + (f" and trim {len(trims)} segment(s)" if trims else ""))
        log(f"  scenes: " + ", ".join(f"{s['sceneId']}@{s['startFrame']/FPS:.2f}s" for s in scenes_out))
        log(f"  duration {duration_ms/1000:.2f}s")
        sys.exit(0)

    # backups (once)
    for p in (p_wav, p_caps, p_tl):
        bak = Path(str(p) + ".bak")
        if p.exists() and not bak.exists():
            shutil.copy(p, bak)

    # apply wav trims
    if trims:
        out = cut_wav(audio.a, audio.sr, trims)
        tmp = str(p_wav) + ".tmp.wav"
        sf.write(tmp, out, audio.sr)
        os.replace(tmp, p_wav)

    p_caps.write_text(json.dumps(new_caps, indent=2), encoding="utf-8")
    p_tl.write_text(json.dumps(timeline, indent=2), encoding="utf-8")

    # ---------------- verify (re-read on-disk) ----------------
    vfails = []
    caps2 = json.loads(p_caps.read_text(encoding="utf-8"))
    tl2 = json.loads(p_tl.read_text(encoding="utf-8"))
    audio2 = Audio(p_wav)
    concat = norm("".join(c["text"] for c in caps2))
    # allow a head-dropped leading word
    if concat != script_norm:
        if head_drop_gis:
            tail_norm = norm(" ".join(w.surface for w in kept))
            if concat != tail_norm:
                vfails.append("verify: caption text != script after fixes.")
        else:
            vfails.append("verify: caption text != script after fixes.")
    # tail not clipped
    if audio2.last_voiced_end() > tl2["durationMs"] + 120:
        vfails.append(f"verify: speech at {audio2.last_voiced_end():.0f}ms exceeds timeline {tl2['durationMs']}ms (clipped tail).")
    # scene sync: first caption word near each scene start
    cap_starts = [c["startMs"] for c in caps2]
    for s in tl2["scenes"]:
        st_ms = s["startFrame"] / FPS * 1000
        near = min((abs(cs - st_ms) for cs in cap_starts), default=9999)
        if near > 500 and s["startFrame"] > 0:
            warns.append(f"scene {s['sceneId']} start {st_ms:.0f}ms is {near:.0f}ms from nearest caption.")
    # monotonic
    fr = [0] + [s["endFrame"] for s in tl2["scenes"]]
    if any(fr[i + 1] < fr[i] for i in range(len(fr) - 1)):
        vfails.append("verify: timeline scene frames not monotonic.")

    passed = not vfails
    for v in vfails:
        log(f"  FAIL: {v}")

    p_mark.write_text(json.dumps({
        "version": VERSION, "passed": passed,
        "wav_sha256": sha(p_wav), "captions_sha": sha(p_caps), "timeline_sha": sha(p_tl),
        "fixes": fixes, "trims_ms": trims, "warns": warns,
    }, indent=2), encoding="utf-8")

    if passed:
        log(f"\n✓ preflight PASSED — {len(new_caps)} caption words, {len(scenes_out)} scenes, {duration_ms/1000:.2f}s. Safe to render.")
        sys.exit(0)
    else:
        log("\n✗ preflight FAILED verification — see above.")
        sys.exit(2)


if __name__ == "__main__":
    main()
