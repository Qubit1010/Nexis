"""Median pitch (F0) and spectral centroid per audio file: objective proxies for how a voice sounds.

    python -I voice_pitch.py audition-*.mp3

Use it to cast placeholder voices without listening (and to report what was picked):
  * pitch separates roles: elderly/heavy male ~70-100 Hz, mature male ~110-150 Hz,
    older woman ~165-190 Hz, younger woman/girl ~220-245 Hz;
  * a low centroid (< ~1100 Hz) reads warmer/softer, a high one brighter/sharper.
A client once rejected a 68 Hz narrator as "very heavy"; 148 Hz was accepted.
"""
import subprocess, sys
import numpy as np
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 16000


def load(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def stats(x):
    frame, hop = 1024, 256
    f0s, cents = [], []
    for i in range(0, len(x) - frame, hop):
        w = x[i:i + frame] * np.hanning(frame)
        if np.sqrt(np.mean(w ** 2)) < 0.02:
            continue
        ac = np.correlate(w, w, "full")[frame - 1:]
        lo, hi = SR // 350, SR // 60          # search 60-350 Hz
        lag = lo + np.argmax(ac[lo:hi])
        if ac[lag] > 0.35 * ac[0]:
            f0s.append(SR / lag)
        spec = np.abs(np.fft.rfft(w))
        freqs = np.fft.rfftfreq(frame, 1 / SR)
        cents.append((spec * freqs).sum() / spec.sum())
    return np.median(f0s), np.median(cents), len(x) / SR


for p in sys.argv[1:]:
    f0, c, d = stats(load(p))
    print(f"{p.rsplit('/', 1)[-1]:<28} F0 {f0:6.1f} Hz   centroid {c:6.0f} Hz   {d:4.1f}s")
