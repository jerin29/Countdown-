"""'Mass' thriller score for EP1, synthesized in numpy. make_score(total_s, sr) -> (N,2) float32.
Key: D minor. Shadow motif: D F E D A. Hits synced to picture cuts."""
import numpy as np, scipy.signal as sig

rng = np.random.default_rng(11)
SR = 48000
D = {"D1": 36.71, "A1": 55.0, "D2": 73.42, "F2": 87.31, "G2": 98.0, "A2": 110.0, "Bb2": 116.54, "C3": 130.81,
     "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.0, "A3": 220.0, "Bb3": 233.08, "C4": 261.63, "C#4": 277.18,
     "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "A4": 440.0, "Bb4": 466.16, "C5": 523.25, "D5": 587.33,
     "E5": 659.26, "F5": 698.46, "A5": 880.0}


def n(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def t_(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return sig.sosfilt(sig.butter(o, f, "low", fs=SR, output="sos"), x).astype(np.float32)
def hp(x, f, o=2): return sig.sosfilt(sig.butter(o, f, "high", fs=SR, output="sos"), x).astype(np.float32)
def bp(x, a, b, o=2): return sig.sosfilt(sig.butter(o, [a, b], "band", fs=SR, output="sos"), x).astype(np.float32)
def norm(x, p=1.0): return (x / (np.abs(x).max() + 1e-9) * p).astype(np.float32)
def saw(f, d, det=0.0):
    tt = t_(d); return sig.sawtooth(2 * np.pi * f * (1 + det) * tt + rng.uniform(0, 6)).astype(np.float32)
def adsr(d, a, dcy, s, r):
    N = int(d * SR); e = np.full(N, s, np.float32)
    na, nd, nr = int(a * SR), int(dcy * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nd: e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def vfilter(x, f0, f1, f2=None):  # time-varying lowpass via chunked one-pole bank
    out = np.zeros_like(x); ch = 512; N = len(x); z = np.zeros(2)
    for i in range(0, N, ch):
        p = i / max(1, N - 1)
        fc = f0 + (f1 - f0) * min(1, p * 2) if f2 is None else (f0 + (f1 - f0) * p * 3 if p < 1 / 3 else f1 + (f2 - f1) * (p - 1 / 3) * 1.5)
        fc = float(np.clip(fc, 30, 18000))
        sos = sig.butter(2, fc, "low", fs=SR, output="sos")
        if i == 0: zi = np.zeros((1, 2))
        seg, zi = sig.sosfilt(sos, x[i:i + ch], zi=zi); out[i:i + ch] = seg
    return out
def reverb(x, dec=2.5, wet=0.4):
    ir = n(dec) * np.exp(-np.linspace(0, 7, int(dec * SR))).astype(np.float32); ir = lp(ir, 6000)
    y = sig.fftconvolve(x, ir)[: len(x)].astype(np.float32); y = norm(y, np.abs(x).max())
    return (1 - wet) * x + wet * y


class Track:
    def __init__(self, total):
        self.N = int(total * SR); self.L = np.zeros(self.N, np.float32); self.R = np.zeros(self.N, np.float32)
    def add(self, x, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.N: return
        x = x[: self.N - i]
        self.L[i:i + len(x)] += x * g * min(1, 1 - pan); self.R[i:i + len(x)] += x * g * min(1, 1 + pan)


# ----------------------------------------------------------------- instruments
def braam(d=3.5, root="D1"):
    f = D[root]; x = sum(saw(f * m, d, det) for m in (1, 2, 3) for det in (-0.004, 0.0, 0.005))
    x = vfilter(x, 120, 1800, 250); x = np.tanh(x * 0.8) * adsr(d, 0.04, 0.6, 0.7, 1.5)
    return norm(reverb(x, 3, 0.35))
def taiko(f0=110, d=0.9):
    tt = t_(d); f = f0 * (0.5 + 0.5 * np.exp(-tt * 18))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5)
    skin = lp(n(d), 1500) * np.exp(-tt * 30) * 0.6
    return norm(np.tanh((body + skin) * 1.5))
def kick(d=0.4):
    tt = t_(d); f = 45 + 110 * np.exp(-tt * 30)
    return norm(np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * 2.5))
def snare(d=0.35):
    tt = t_(d); x = bp(n(d), 900, 7000) * np.exp(-tt * 14) + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 25) * 0.6
    return norm(reverb(x, 1.2, 0.3))
def hat(d=0.06): tt = t_(d); return norm(hp(n(d), 8000) * np.exp(-tt * 60))
def stab(notes, d=0.45):
    x = sum(saw(D[k], d, det) for k in notes for det in (-0.006, 0.006))
    x = vfilter(x, 300, 3500, 400) * adsr(d, 0.008, 0.15, 0.5, 0.2)
    return norm(np.tanh(x * 0.6))
def pad(notes, d, cutoff=1400):
    x = sum(saw(D[k], d, det) for k in notes for det in (-0.007, 0, 0.006))
    return norm(lp(x, cutoff, 2) * adsr(d, min(2.0, d / 3), 0.1, 1.0, min(2.0, d / 3)))
def choir(notes, d):
    tt = t_(d); out = np.zeros(len(tt), np.float32)
    for k in notes:
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * tt + rng.uniform(0, 6))
        s = sig.sawtooth(2 * np.pi * np.cumsum(D[k] * vib) / SR).astype(np.float32)
        out += bp(s, 600, 800) * 1.0 + bp(s, 1050, 1300) * 0.6 + bp(s, 2400, 2800) * 0.25
    return norm(reverb(out * adsr(d, 0.8, 0.1, 1.0, 1.2), 3, 0.5))
def piano(k, d=2.5):
    tt = t_(d); f = D[k]
    x = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (1.5 + h * 0.9)) / h for h in range(1, 7))
    return norm(reverb(x * (1 - np.exp(-tt * 400)), 2.5, 0.45))
def bass16(k, d):
    x = saw(D[k], d) + 0.6 * saw(D[k] * 2, d, 0.003)
    return norm(np.tanh(lp(x, 700) * 1.8) * adsr(d, 0.004, 0.08, 0.4, 0.03))
def lead(k, d):
    tt = t_(d); vib = 1 + 0.008 * np.sin(2 * np.pi * 5.5 * tt) * np.clip(tt * 2, 0, 1)
    x = sig.sawtooth(2 * np.pi * np.cumsum(D[k] * vib) / SR).astype(np.float32) + 0.5 * sig.square(2 * np.pi * np.cumsum(D[k] * 2 * vib) / SR).astype(np.float32)
    return norm(lp(x, 2800) * adsr(d, 0.03, 0.2, 0.8, 0.15))
def riser(d):
    tt = t_(d); p = tt / d
    nz = n(d); out = np.zeros_like(nz); ch = 1024; zi = np.zeros((2, 2))
    for i in range(0, len(nz), ch):
        fc = 200 + 9000 * (i / len(nz)) ** 2; sos = sig.butter(2, [fc * 0.7, min(fc * 1.3, 23000)], "band", fs=SR, output="sos")
        seg, zi = sig.sosfilt(sos, nz[i:i + ch], zi=zi); out[i:i + ch] = seg
    tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (p * 3)) / SR) * 0.3
    return norm((norm(out) + tone) * p ** 2)
def tick(d=0.03): tt = t_(d); return norm(hp(n(d), 3000) * np.exp(-tt * 200))
def subdrop(d=1.6):
    tt = t_(d); return norm(np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 1.2) + 25) / SR) * np.exp(-tt * 1.8))


def make_score(total):
    T = Track(total)
    # A 0-12.4 : clock ticks, drone, piano Shadow motif, riser into crash
    for k in range(24): T.add(tick(), 0.5 + k * 0.5, 0.25 if k % 2 else 0.4, pan=0.3 if k % 2 else -0.3)
    T.add(pad(["D2", "A2"], 12.4, 500), 0, 0.35)
    for i, (k, tt) in enumerate([("D4", 1.0), ("F4", 2.0), ("E4", 3.0), ("D4", 4.0), ("A3", 5.5), ("D4", 7.5), ("F4", 8.5), ("A4", 9.5)]):
        T.add(piano(k), tt, 0.45, pan=-0.2 + 0.05 * i)
    T.add(riser(2.4), 10.1, 0.55)
    # B 12.5-38 : crash braam, slow taiko, string pad Dm-Bb-Gm-A
    T.add(braam(4.5), 12.45, 1.0); T.add(taiko(70, 1.5), 12.45, 0.9); T.add(subdrop(), 12.45, 0.8)
    chords = [["D3", "F3", "A3"], ["Bb2", "D3", "F3"], ["G2", "Bb2", "D3"], ["A2", "C#4", "E3"]]
    for i, ch in enumerate(chords * 2):
        st = 14 + i * 3.0
        if st < 37: T.add(pad(ch, 3.4, 1100), st, 0.32)
    beat = 60 / 90
    for k in range(int((38 - 14) / beat)):
        tt = 14 + k * beat
        if tt > 37.4: break
        if k % 4 == 0: T.add(taiko(95, 0.9), tt, 0.55, pan=-0.25)
        if k % 4 == 2: T.add(taiko(120, 0.7), tt, 0.4, pan=0.25)
        if tt > 28 and k % 2 == 1: T.add(taiko(160, 0.4), tt, 0.3)
    T.add(braam(3.0, "A1"), 28.0, 0.7); T.add(choir(["D4", "A4"], 8), 28.5, 0.25)
    T.add(riser(3.4), 34.6, 0.5)
    # C 38-42 : silence; club music handled as diegetic sound. low drone under Christy's line
    T.add(pad(["D2", "A2"], 10, 300), 60, 0.25)
    # D 70-86 : 16th ostinato build, 120 bpm
    b16 = 60 / 120 / 4
    seq = ["D2"] * 12 + ["F2", "D2", "G2", "D2"]
    for k in range(int(16 / b16)):
        tt = 70 + k * b16
        g = 0.15 + 0.35 * (k * b16 / 16)
        T.add(bass16(seq[k % 16], b16 * 0.9), tt, g)
        if tt > 78 and k % 2 == 0: T.add(hat(), tt, 0.12 + 0.1 * (tt - 78) / 8, pan=0.35)
    for k in range(5): T.add(taiko(80, 1.2), 79 + k * 1.4, 0.5)  # synced to light clunks
    T.add(riser(3.0), 83.0, 0.6)
    # E 86-104 : MASS section, 120 bpm
    beat = 0.5
    T.add(braam(4.0), 86.0, 1.0); T.add(subdrop(), 86.0, 0.8)
    lead_line = [("D5", 1), ("F5", 1), ("E5", 1), ("D5", 1), ("A4", 2), ("C5", 1), ("D5", 1),
                 ("D5", 1), ("F5", 1), ("E5", 1), ("D5", 1), ("A5", 2), ("F5", 1), ("E5", 1), ("D5", 2)]
    bar_chords = [["D3", "F3", "A3", "D4"], ["Bb2", "F3", "Bb3", "D4"], ["G2", "D3", "G3", "Bb3"], ["A2", "E3", "A3", "C#4"]]
    bass_seq = ["D2", "D2", "F2", "D2", "G2", "D2", "A1", "D2"]
    for k in range(int(18 / beat)):
        tt = 86 + k * beat
        T.add(kick(), tt, 0.75 if k % 2 == 0 else 0.5)
        if k % 2 == 1: T.add(snare(), tt, 0.45, pan=0.1)
        if k % 4 == 3: T.add(taiko(140, 0.5), tt + 0.25, 0.4, pan=-0.3)
        T.add(hat(), tt + 0.25, 0.15, pan=0.4)
        for j in range(2):
            T.add(bass16(bass_seq[(k * 2 + j) % 8], 0.22), tt + j * 0.25, 0.45)
        if k % 4 == 0:
            T.add(stab(bar_chords[(k // 4) % 4]), tt, 0.5)
            T.add(stab(bar_chords[(k // 4) % 4], 0.25), tt + 0.75, 0.3)
    T.add(choir(["D3", "A3", "D4", "F4"], 18), 86.0, 0.35)
    tt = 90.0
    for k, ln in lead_line:
        if tt >= 103.5: break
        T.add(lead(k, ln * beat * 0.95), tt, 0.28); tt += ln * beat
    for h in (92.6, 98.5): T.add(braam(2.5), h, 0.75); T.add(taiko(60, 1.2), h, 0.8)
    # F 104-116 : drop out, reverse swell, final hit + choir
    sw = braam(3.0)[::-1][-int(4.8 * SR):]; T.add(norm(sw) * np.linspace(0, 1, len(sw)), 104.5, 0.5)
    T.add(pad(["D2", "A2"], 5, 260), 104, 0.3)
    T.add(braam(6.0), 109.3, 1.0); T.add(taiko(55, 2.0), 109.3, 1.0); T.add(subdrop(2.5), 109.3, 0.9)
    T.add(choir(["D3", "A3", "D4", "F4", "A4"], 6.5), 109.3, 0.5)
    T.add(piano("D4", 4), 112.5, 0.35); T.add(piano("A3", 3), 113.3, 0.3)
    mix = np.stack([T.L, T.R], 1)
    return norm(np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.4), 0.9)


if __name__ == "__main__":
    import sys, scipy.io.wavfile as w
    w.write(sys.argv[1], SR, make_score(116))
