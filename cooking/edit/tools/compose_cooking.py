# Cooking-show bed: ukulele-style plucked strums (Karplus-Strong), marimba hook, bass, shaker, claps.
# 104 BPM, G major, I-V-vi-IV. Starts after the intro (START) and resolves under the end card (END_HIT).
import numpy as np, wave, sys
SR = 44100; DUR = 141.7; START = 3.6; END_HIT = 136.7
BPM = 104; B = 60 / BPM; N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)
def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if j <= i or i < 0: return
    s = sig[: j - i] * g
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
def pluck(m, dur=0.9, bright=0.5):
    f = hz(m); n = int(dur * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.996 * (bright * buf[i % p] + (1 - bright) * buf[(i + 1) % p])
    return out * 0.5
pl_cache = {}
def pl(m, dur=0.9):
    k = (m, dur)
    if k not in pl_cache: pl_cache[k] = pluck(m, dur)
    return pl_cache[k]
def marimba(m, dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 22)
    return s * np.minimum(1, t / 0.003) * 0.32
def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t * 1.6) * np.minimum(1, (dur - t) / 0.05).clip(0) * 0.32
def shaker():
    n = int(0.07 * SR); x = rng.standard_normal(n); x = x - np.convolve(x, np.ones(3) / 3, 'same')
    return x * np.exp(-np.arange(n) / SR * 60) * 0.08
def clap():
    n = int(0.18 * SR); x = rng.standard_normal(n); e = np.zeros(n)
    for d in (0, 0.01, 0.02): i = int(d * SR); e[i:] += np.exp(-np.arange(n - i) / SR * 40)
    y = x * e; return (np.convolve(y, np.ones(4) / 4, 'same') - np.convolve(y, np.ones(30) / 30, 'same')) * 0.5
def kick():
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 45 + 80 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.55
chords = [[55, 59, 62, 67], [50, 54, 57, 62], [52, 55, 59, 64], [48, 52, 55, 60]]  # G D Em C
roots = [43, 38, 40, 36]
hook = [(0, 74), (0.5, 76), (1, 74), (1.5, 71), (2, 74), (3, 79), (3.5, 76)]
bar = 4 * B; t = START; k = 0
while t + bar <= END_HIT + 1e-6:
    ch = chords[k % 4]
    for beat in range(4):
        bt = t + beat * B
        # island strum: down on beats, up on the "and"
        for j, m in enumerate(ch): add(pl(m), bt + j * 0.012, 0.5, -0.3 + 0.2 * j)
        for j, m in enumerate(ch[::-1][:3]): add(pl(m + 12, 0.5), bt + B / 2 + j * 0.01, 0.22, 0.3)
        add(shaker(), bt + B / 2, 1.0, 0.4); add(shaker(), bt, 0.6, 0.4)
        if beat in (0, 2): add(kick(), bt, 0.8)
        if beat in (1, 3): add(clap(), bt, 0.55, -0.1)
    add(bass(roots[k % 4], B * 1.5), t, 1.0); add(bass(roots[k % 4] + 7, B * 0.9), t + 2.5 * B, 0.8)
    if (k // 4) % 2 == 1:  # marimba hook every other 4-bar phrase
        for off, m in hook: add(marimba(m + [0, -5, -3, -7][k % 4] + 5), t + off * B, 0.9, 0.2)
    t += bar; k += 1
# end card: big G chord with a marimba run
for j, m in enumerate([43, 55, 59, 62, 67, 71]): add(pl(m, 3.0), END_HIT + j * 0.03, 0.6, -0.3 + 0.12 * j)
for j, m in enumerate([67, 71, 74, 79, 83]): add(marimba(m, 1.2), END_HIT + 0.35 + j * 0.09, 0.9, 0.25)
add(bass(31, 3.5), END_HIT, 1.2); add(kick(), END_HIT, 1.0)
mix = np.stack([L, R], 1)
fo = int(1.2 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 2
fi = int(0.3 * SR); s0 = int(START * SR); mix[s0:s0 + fi] *= np.linspace(0, 1, fi)[:, None]
mix *= 0.85 / np.max(np.abs(mix))
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('wrote', sys.argv[1])
