# "Mass" intro score, 6.5 s at 120 BPM (beat = 0.5 s). Deterministic, everything computed in code.
# Cues (s): build 0-1.0 | stabs 1.0 1.5 2.0 | riser 2.25-3.0 | BIG HIT 3.0 (logo) |
#           name 16ths 3.5-4.0 | groove 3.0-5.5 | final boom 5.5 with tail to 6.5
import numpy as np, wave, sys
SR = 48000; DUR = 6.5; N = int(SR * DUR)
rng = np.random.default_rng(42)
L = np.zeros(N); R = np.zeros(N)
def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def env_exp(n, k): return np.exp(-np.arange(n) / SR * k)
def boom(dur=1.6, f0=70, f1=32):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 9); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env_exp(n, 2.2)
    click = rng.standard_normal(n) * env_exp(n, 90) * 0.5
    sub = np.tanh(2.2 * (body + click))
    return sub
def taiko(f0=150, f1=75, dur=0.45, bright=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 25); ph = 2 * np.pi * np.cumsum(f) / SR
    skin = np.sin(ph) * env_exp(n, 9)
    slap = rng.standard_normal(n) * env_exp(n, 60) * bright
    return np.tanh(1.8 * (skin + slap))
def clap(dur=0.25):
    n = int(dur * SR); x = rng.standard_normal(n)
    e = np.zeros(n)
    for d in (0, 0.011, 0.022): i = int(d * SR); e[i:] += env_exp(n - i, 38)
    # crude band-pass: difference of two one-pole smoothings
    y = x * e; a = np.convolve(y, np.ones(4) / 4, 'same'); b = np.convolve(y, np.ones(40) / 40, 'same')
    return (a - b) * 1.6
def brass(notes, dur=0.42, k=5.0, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        for d in (-0.08, 0.0, 0.08):
            ff = f * 2 ** (d / 12)
            for h in range(1, 14):  # band-limited saw
                if ff * h > 9000: break
                out += np.sin(2 * np.pi * ff * h * t) / h * (bright if h > 3 else 1.0)
    att = np.minimum(1, t / 0.012); out *= att * env_exp(n, k)
    return np.tanh(0.35 * out)
def riser(dur=0.75):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    f = 200 + 2200 * p ** 2; ph = 2 * np.pi * np.cumsum(f) / SR
    noise = rng.standard_normal(n); hp = noise - np.convolve(noise, np.ones(12) / 12, 'same')
    return (0.5 * np.sin(ph) + 0.6 * hp) * p ** 2.2
def cym(dur=1.8):
    n = int(dur * SR); x = rng.standard_normal(n); hp = x - np.convolve(x, np.ones(6) / 6, 'same')
    return hp * env_exp(n, 2.6) * 0.5
D = [38, 45, 50]          # D power chord (low)
Dh = [50, 57, 62, 66]     # D major high stab
# 1) build: taiko hits accelerating 0 -> 1.0
for t, g in [(0.0, .7), (0.5, .75), (0.75, .8), (0.875, .85), (0.9375, .9)]:
    add(taiko(), t, g, -0.2); add(taiko(110, 60), t + 0.01, g * 0.6, 0.2)
add(boom(1.0, 55, 30), 0.0, 0.6)
# 2) three stabs on the word slams
for i, t in enumerate([1.0, 1.5, 2.0]):
    add(boom(0.6), t, 0.8); add(brass([m + (0, 0, 2)[i] for m in D], 0.38), t, 0.55)
    add(clap(), t, 0.5); add(taiko(), t, 0.8)
    for s in (0.25,): add(taiko(170, 95, 0.3), t + s, 0.45, 0.3)
# 3) riser into the hit
add(riser(0.75), 2.25, 0.55)
for t in np.arange(2.5, 3.0, 0.0625): add(taiko(190, 100, 0.2, 0.2), t, 0.25 + (t - 2.5) * 0.9, -0.3 if int(t * 16) % 2 else 0.3)
# 4) BIG HIT at 3.0
add(boom(2.2, 80, 28), 3.0, 1.2); add(brass(Dh + D, 1.6, 1.6), 3.0, 0.75); add(cym(2.4), 3.0, 0.6); add(clap(0.4), 3.0, 0.6)
# 5) groove 3.5-5.5: kick-ish taiko on beats, claps on 2/4, 16th name slams 3.5-4.0
for b in np.arange(3.5, 5.5, 0.5):
    add(taiko(120, 60, 0.4), b, 1.2); add(boom(0.45, 62, 38), b, 0.75)
    if int(round(b * 2)) % 2 == 1: add(clap(), b, 0.7)
    add(taiko(200, 120, 0.15, 0.15), b + 0.25, 0.5, 0.25)
for k, t in enumerate(np.arange(3.5, 4.0, 0.0625)): add(brass([62 + (k % 3) * 0], 0.08, 30, 1.2), t, 0.22, -0.4 + 0.1 * k)
add(brass(D, 0.5, 4), 4.25, 0.45); add(brass([m + 2 for m in D], 0.5, 4), 4.5, 0.45)
# 6) final boom 5.5, ring out
add(boom(1.0, 75, 26), 5.5, 1.1); add(brass(Dh + D, 1.0, 2.2), 5.5, 0.7); add(cym(1.0), 5.5, 0.5)
# reverb (seeded noise IR) + glue
irn = int(1.4 * SR); ti = np.arange(irn) / SR
def conv(x, ir):
    n = len(x) + len(ir); nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[: len(x)]
for ch in (0, 1):
    ir = rng.standard_normal(irn) * np.exp(-ti * 4.0); ir[: int(0.015 * SR)] = 0
    x = L if ch == 0 else R
    w = conv(x, ir); w *= 0.22 * np.max(np.abs(x)) / (np.max(np.abs(w)) + 1e-9)
    if ch == 0: L = x + w
    else: R = x + w
mix = np.stack([L, R], 1); mix = np.tanh(1.3 * mix / (np.max(np.abs(mix)) + 1e-9)) 
fo = int(0.35 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
mix *= 0.89 / np.max(np.abs(mix))
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('wrote', sys.argv[1])
