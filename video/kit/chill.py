# Laid-back soundtrack: electric piano on jazzy 7th/9th chords, sub bass, swung boom-bap drums, soft
# mallet effects in the same key. Same cue JSON as audio.py.  python3 chill.py spec.json out.wav
import json, sys
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 48000
spec = json.load(open(sys.argv[1]))
DUR = spec["duration"]; N = int(DUR * SR)
BPM = spec["bpm"]; BEAT = 60 / BPM; BAR = 4 * BEAT
SWING = spec.get("swing", 0.6)            # where the off-beat eighth lands inside the beat
ROOT = spec["root"]
SCALE = [0, 2, 4, 5, 7, 9, 11]
rng = np.random.default_rng(spec.get("seed", 1))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def deg(d, octave=0): return ROOT + 12 * (octave + d // 7) + SCALE[d % 7]

def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)

buses = {k: np.zeros((2, N)) for k in ("keys", "bass", "drums", "fx")}
send = np.zeros((2, N))
def put(bus, sig, t, gain=1.0, pan=0.0, rev=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    s = sig[: N - i] * gain
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buses[bus][0, i:i + len(s)] += s * gl; buses[bus][1, i:i + len(s)] += s * gr
    send[0, i:i + len(s)] += s * gl * rev; send[1, i:i + len(s)] += s * gr * rev
def sw(beat_pos):                          # beat position (in beats, eighths allowed) -> seconds, swung
    b = np.floor(beat_pos); frac = beat_pos - b
    return (b + (SWING if abs(frac - 0.5) < 1e-6 else frac)) * BEAT

# ---------------------------------------------------------------- instruments
def epiano(m, length, vel=1.0):
    n = int((length + 0.8) * SR); t = np.arange(n) / SR; f = hz(m)
    idx = 1.3 * np.exp(-t * 6) + 0.15                     # the bark at the attack, mellow after
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    x += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    x += 0.08 * np.sin(2 * np.pi * 7.02 * f * t) * np.exp(-t * 25)   # tine ping
    env = np.minimum(1, t / 0.004) * (0.6 * np.exp(-t * 1.4) + 0.4 * np.exp(-t * 0.35))
    rel = np.clip((length + 0.8 - t) / 0.8, 0, 1)
    return x * env * rel * 0.18 * vel

def mallet(m, length=1.2):
    n = int(length * SR); t = np.arange(n) / SR; f = hz(m)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 4) + 0.3 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 14)
    return x * np.minimum(1, t / 0.002) * 0.3

def sub(m, length):
    n = int((length + 0.05) * SR); t = np.arange(n) / SR
    x = np.tanh(1.6 * np.sin(2 * np.pi * hz(m) * t)) * 0.8
    env = np.minimum(1, t / 0.01) * np.clip((length - t) / 0.06 + 1, 0, 1) * (0.7 + 0.3 * np.exp(-t * 3))
    return lp(x, 260) * env * 0.42

def kick():
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 46 + 55 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return lp(x + 0.15 * lp(rng.uniform(-1, 1, n), 1500) * np.exp(-t * 120), 3000) * 0.6

def snare():
    n = int(0.35 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30) * 0.5
    noise = bp(rng.uniform(-1, 1, n), 900, 5000) * np.exp(-t * 16)
    return lp(body + noise, 6000) * 0.28

def rim():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1700 * t) * 0.5 + bp(rng.uniform(-1, 1, n), 2000, 6000)) * np.exp(-t * 70) * 0.12

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return lp(hp(rng.uniform(-1, 1, n), 6500), 11000) * np.exp(-t * (18 if open_ else 70)) * 0.07

def swell(length=0.8):                     # a soft air swell instead of a whoosh
    n = int(length * SR); x = lp(hp(rng.uniform(-1, 1, n), 400), 2500)
    return x * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 0.07

def tap():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * hz(deg(4, 1)) * t) * np.exp(-t * 45) + 0.4 * bp(rng.uniform(-1, 1, n), 800, 2500) * np.exp(-t * 200)) * 0.16

def tick():
    n = int(0.025 * SR)
    return bp(rng.uniform(-1, 1, n), 1500, 4500) * np.exp(-np.arange(n) / SR * 180) * 0.05

# ---------------------------------------------------------------- the song
prog = spec.get("prog", [0, 5, 1, 4])
drop = spec["drop"]; end = spec.get("musicEnd", DUR - 1.5)
bars = int(np.ceil(DUR / BAR))
for b in range(bars):
    t0 = b * BAR
    if t0 >= end: break
    d = prog[b % len(prog)]
    full = t0 + 0.01 >= drop
    # rootless voicing: 3rd, 5th, 7th, 9th around the middle of the keyboard
    voicing = [deg(d + 2), deg(d + 4), deg(d + 6), deg(d + 8)]
    while min(voicing) > ROOT + 7: voicing = [v - 12 for v in voicing]
    hits = [(0, BAR * 0.95, 1.0)] if not full else [(0, 1.4 * BEAT, 1.0), (sw(1.5), 2.3 * BEAT, 0.75)]
    for pos, ln, vel in hits:
        ts = t0 + pos
        if ts >= end: continue
        for j, m in enumerate(voicing):              # a slight strum, low to high
            put("keys", epiano(m, min(ln, end + 0.6 - ts), vel), ts + j * 0.012, 0.9, -0.3 + 0.2 * j, 0.35)
    on = lambda ts: drop - 0.06 <= ts < end          # the groove starts on the first beat at the drop
    if on(t0 + 3 * BEAT):
        r = deg(d, -2)
        for pos, m, ln in ((0, r, 1.3), (sw(2.5), r + 7, 0.45), (3, r, 0.8)):
            if on(t0 + pos * BEAT if pos == 3 or pos == 0 else t0 + pos): put("bass", sub(m, ln * BEAT), t0 + (pos * BEAT if pos in (0, 3) else pos))
        for q in range(4):
            tb = t0 + q * BEAT
            if not on(tb): continue
            if q in (0,): put("drums", kick(), tb, 1.0)
            if q == 2: put("drums", kick(), t0 + sw(2.5), 0.8)
            if q in (1, 3): put("drums", snare() if b % 2 or q == 3 else rim() * 2, tb, 1.0, 0.05, 0.25)
            for e in (q, q + 0.5):
                te = t0 + sw(e)
                if te < end: put("drums", hat(open_=(e == 3.5 and b % 2 == 1)), te, rng.uniform(0.6, 1.0), 0.25)
    if not full:
        # the hook: a few mallet notes over the chord, no drums yet
        for k, e in enumerate((0, 1.5, 2.5)):
            te = t0 + sw(e)
            if te < min(end, drop): put("fx", mallet(deg([4, 6, 8][k], 1)), te, 0.5, 0.3, 0.5)

# ending: the tonic as a major 9 that rings out, one low note
for j, m in enumerate([deg(2), deg(4), deg(6), deg(8)]):
    put("keys", epiano(m, 2.8, 0.9), end + j * 0.02, 0.9, -0.3 + 0.2 * j, 0.5)
put("bass", sub(deg(0, -2), 1.6), end)
put("fx", mallet(deg(7, 1), 2.0), end + 0.35, 0.45, 0.2, 0.6)

# effects from the storyboard, softened and in key
for fx in spec.get("fx", []):
    t, k = fx["t"], fx["type"]; g = fx.get("gain", 1.0) * 0.8; pan = fx.get("pan", 0.0)
    if k == "whoosh": put("fx", swell(fx.get("len", 0.6) + 0.2), t - (fx.get("len", 0.6) + 0.2) * 0.7, g, pan, 0.4)
    elif k == "riser": put("fx", swell(fx.get("len", 1.0)), t - fx.get("len", 1.0) * 0.9, g, pan, 0.4)
    elif k == "tap": put("fx", tap(), t, g, pan, 0.2)
    elif k == "tick": put("fx", tick(), t, g, pan, 0.1)
    elif k in ("pop", "bell"): put("fx", mallet(deg(fx.get("deg", 4), 1), 0.9), t, g * 0.8, pan, 0.4)

# ---------------------------------------------------------------- mix
keys = buses["keys"]
# tape wobble on the keys: a slow, slightly uneven pitch drift
tt = np.arange(N) / SR
wob = 0.0016 * np.sin(2 * np.pi * 0.45 * tt) + 0.0007 * np.sin(2 * np.pi * 1.3 * tt + 1)
for c in range(2): keys[c] = np.interp(tt - wob - 0.003, tt, keys[c])
trem = 1 - 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * tt))
keys[0] *= trem; keys[1] *= 1 - 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.2 * tt + np.pi))
# before the drop the keys sit behind a lowpass that opens as it lands
k_open = np.clip((tt - (drop - 1.2)) / 1.2, 0, 1)
dark = np.stack([lp(keys[c], 900) for c in range(2)])
keys = dark * (1 - k_open) + keys * k_open
keys = np.stack([lp(keys[c], 5500) for c in range(2)])

duck = np.ones(N)                           # the keys and bass breathe with the kick, gently
for b in range(bars):
    for pos in (0, sw(2.5)):
        i0 = int((b * BAR + pos) * SR)
        if b * BAR >= drop - 0.01 and i0 < N:
            n = min(int(0.25 * SR), N - i0); duck[i0:i0 + n] = np.minimum(duck[i0:i0 + n], 0.78 + 0.22 * np.linspace(0, 1, n))
mix = keys * duck * 1.0 + buses["bass"] * duck * 1.0 + buses["drums"] * 0.9 + buses["fx"] * 0.9

vinyl = lp(hp(rng.normal(0, 1, N), 1500), 6000) * 0.0025
for _ in range(int(DUR * 6)):               # sparse, quiet crackle
    i = rng.integers(0, N - 200); vinyl[i:i + 60] += rng.uniform(-1, 1, 60) * np.exp(-np.arange(60) / 12) * rng.uniform(0.005, 0.02)
mix += vinyl

ir_n = int(2.4 * SR); ti = np.arange(ir_n) / SR
irs = [lp(rng.normal(0, 1, ir_n) * np.exp(-ti * 2.6), 4500) for _ in range(2)]
wet = np.stack([fftconvolve(hp(send[c], 300), irs[c])[:N] for c in range(2)])
wet /= np.max(np.abs(wet)) + 1e-9
mix = mix / (np.max(np.abs(mix)) + 1e-9) + wet * 0.16
mix = np.stack([lp(mix[c], 13000) for c in range(2)])
fade = np.minimum(1, tt / 0.03) * np.clip((DUR - tt) / 0.8, 0, 1)
mix = np.tanh(mix * fade * 1.3) / np.tanh(1.3)
mix *= 0.89 / np.max(np.abs(mix))
print("rms dBFS", round(20 * np.log10(np.sqrt(np.mean(mix ** 2))), 1))
wavfile.write(sys.argv[2], SR, (mix.T * 32767).astype(np.int16))
