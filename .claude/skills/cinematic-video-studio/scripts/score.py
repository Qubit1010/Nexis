"""Synthesize a calm original score for a cut (no samples, no licensed music).

A slow A - F#m - D - E chord bed, an optional breath + sea texture, an optional soft heartbeat,
an airy swell into a mid-film shift, and one warm A-major chord where the film resolves.
build_cut.py calls this with cue times computed from the spec's "score" block.

Usage: python -I score.py <out.wav> '<cues json>'
cues: {"total": 54.6, "micro": 30.2, "surface": 45.1, "breath": false, "waves": false, "dive": 11.3}
  micro   = the airy swell (e.g. the cut into a macro/science world)
  surface = where the warm resolving chord lands
  dive    = optional; adds an underwater rumble and soft heartbeat from here to "surface"
History: a rising Shepard tone was tried first and judged too intense by the client; do not
reintroduce it without asking.
"""
import json, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env(n, a, r):
    e = np.ones(n)
    a, r = int(a * SR), int(r * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def place(buf, sig, t):
    i = int(t * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def noise_band(dur, lo, hi):
    n = int(dur * SR)
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def breath(dur, inhale=True):
    x = noise_band(dur, 250, 2600)
    t = np.linspace(0, 1, len(x))
    shape = np.sin(np.pi * t) ** 1.5 if not inhale else t ** 1.8 * (1 - t ** 8)
    return x * shape


def tones(freqs, dur, amps=None, detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    amps = amps or [1] * len(freqs)
    return sum(a * np.sin(2 * np.pi * f * (1 + detune) * t + i) for i, (f, a) in enumerate(zip(freqs, amps)))


def heartbeat(start, end, bpm0, bpm1):
    out = np.zeros(int((end - start + 1) * SR))
    t, k = 0.0, 0
    while start + t < end:
        bpm = bpm0 + (bpm1 - bpm0) * t / max(end - start, 1e-6)
        for off, amp in ((0.0, 1.0), (0.28, 0.6)):
            n = int(0.18 * SR)
            tt = np.arange(n) / SR
            thump = amp * np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 22)
            place(out, thump, t + off)
        t += 60.0 / bpm
        k += 1
    return out


def pad(freqs, dur, detune=0.0):
    """Soft warm chord: sines plus a quiet octave, slow swell in and out."""
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * f * (1 + detune) * t + i) + 0.18 * np.sin(4 * np.pi * f * (1 + detune) * t)
            for i, f in enumerate(freqs)) / len(freqs)
    return x * env(len(x), min(2.5, dur / 3), min(3.0, dur / 2.5))


# A, F#m, D, E (with add9/7 colours), voiced low and close for a calm bed
CHORDS = [[110, 164.81, 246.94, 277.18], [92.5, 138.59, 220, 277.18],
          [73.42, 146.83, 220, 277.18], [82.41, 123.47, 207.65, 246.94]]


def main(path, cues):
    total, micro, surface = cues["total"], cues["micro"], cues["surface"]
    dive = cues.get("dive")
    breaths, sea = cues.get("breath", True), cues.get("waves", True)
    L = np.zeros(int((total + 1) * SR))
    R = np.zeros_like(L)

    def both(sig, t, gain, pan=0.0):
        place(L, sig * gain * (1 - pan), t)
        place(R, sig * gain * (1 + pan), t)

    # 1. inhale into silence
    if breaths:
        both(breath(1.1, inhale=True), 0.0, 0.22)

    # 2. tranquil bed: a slow A - F#m - D - E progression, each chord ~7s, overlapping swells
    t, k, step = 1.3, 0, 7.0
    while t < surface - 1.0:
        d = min(step + 3.0, surface + 1.5 - t)
        place(L, pad(CHORDS[k % 4], d) * 0.11, t)
        place(R, pad(CHORDS[k % 4], d, detune=0.002) * 0.11, t)
        t, k = t + step, k + 1
    if sea:
        waves = noise_band(micro - 1.3, 60, 700)
        waves *= (0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * np.arange(len(waves)) / SR)) * env(len(waves), 2.0, 2.0)
        both(waves, 1.3, 0.05)

    if dive is not None:
        # 3. underwater rumble during the dive
        rumble = noise_band(micro - dive, 25, 160) * env(int((micro - dive) * SR), 0.4, 1.0)
        both(rumble, dive, 0.08)
        # 4. heartbeat from the dive, through the micro world
        hb = heartbeat(dive, surface - 0.05, 54, 58)
        both(hb, dive, 0.14)

    # 5. a soft airy swell into the micro world (the old rising Shepard tone read as too intense)
    sw = noise_band(2.0, 300, 3000) * np.sin(np.linspace(0, np.pi, int(2.0 * SR))) ** 2
    both(sw, micro - 1.2, 0.05)

    # 6. hard cut to the surface: exhale + warm A-major chord, held under the end card
    if breaths:
        both(breath(1.6, inhale=False), surface, 0.20)
    chord_d = total - surface
    chord = tones([110, 138.59, 164.81, 220, 329.63], chord_d, [1, .7, .7, .5, .25])
    chord *= env(len(chord), 0.9, 3.0)
    place(L, chord * 0.09, surface + 0.15)
    place(R, tones([110.2, 138.8, 165.0, 220.4, 330.0], chord_d, [1, .7, .7, .5, .25]) * env(len(chord), 0.9, 3.0) * 0.09,
          surface + 0.15)

    st = np.stack([L, R], 1)[: int(total * SR)]
    st /= max(1.0, np.abs(st).max() / 0.89)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], json.loads(sys.argv[2]))
