# Soft romantic bed, 26 s, 80 BPM, D major: piano arpeggios + pad + bass + reverb. Deterministic.
import numpy as np, wave, sys
OFF = 1.8  # cold open before the first bar
SR = 48000; DUR = 30.0 + OFF; N = int(SR * DUR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
BEAT = 0.75; BAR = 4 * BEAT  # 3 s
# chords (midi): D, A/C#, Bm, G  -> repeat; last bar resolves to D and holds
prog = [[62,66,69],[61,64,69],[59,62,66],[55,59,62]]
roots = [38, 37, 35, 31]
bars = [0,1,2,3,0,1,2,3,1]  # 9 bars = 27 s (ends on A), then final D at 27 under the end card
def add(sig, start, pan=0.0, gain=1.0):
    i = int((start + OFF) * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)); R[i:j] += s * np.sqrt(0.5 * (1 + pan))
def piano(m, dur=2.2, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    out = np.zeros(n)
    for k, a in enumerate([1.0, 0.45, 0.22, 0.12, 0.06], 1):
        out += a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.6 + 1.3 * k))
    att = np.minimum(1, t / 0.006)
    return out * att * vel * 0.18
def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for m in ms:
        for d in (-0.07, 0.07):
            f = hz(m) * 2 ** (d / 12)
            out += np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9)
    return out * np.clip(env, 0, 1) * 0.022
def bass(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    out = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.04) * np.exp(-t * 0.6) * np.minimum(1, (dur - t) / 0.2)
    return out * np.clip(env, 0, 1) * 0.10
arp = [0, 1, 2, 1, 2, 0, 1, 2]  # eighth-note pattern over the chord, octave lifts on beats 3-4
# cold open: a held D pad that swells into the first bar
add(pad([62, 66, 69], OFF + 0.9), -OFF, 0.0, 0.9)
add(piano(74, dur=2.4, vel=0.5), -OFF + 0.3, 0.2)
for b, ci in enumerate(bars):
    t0 = b * BAR; ch = prog[ci]
    add(pad(ch, BAR + 0.9), t0, 0.0)
    if b >= 1: add(bass(roots[ci], BAR), t0, 0.0)
    for e, idx in enumerate(arp):
        m = ch[idx] + (12 if e >= 4 else 0)
        vel = 0.9 if e % 2 == 0 else 0.65
        if b == 0 and e < 2: vel *= 0.7
        add(piano(m, vel=vel), t0 + e * BEAT / 2, pan=(-0.35 if idx == 0 else 0.35 if idx == 2 else 0.0))
# melody hint on bars 4-7 (top line), soft
mel = [(4, 0, 74), (4, 2, 73), (5, 0, 73), (5, 2, 71), (6, 0, 71), (6, 2, 69), (7, 0, 67), (7, 2, 69)]
for b, beat, m in mel:
    add(piano(m, dur=2.5, vel=0.75), b * BAR + beat * BEAT + 0.01, pan=0.1)
# final: D major held under the outro, then fade
t0 = 9 * BAR  # 27.0
add(pad([62, 66, 69, 74], 3.0), t0 - 0.05, 0.0, 1.2)
add(bass(38, 3.0), t0, 0.0)
for k, m in enumerate([62, 66, 69, 74, 78]):
    add(piano(m, dur=3.0, vel=0.8), t0 + k * 0.06, pan=-0.3 + 0.15 * k)
# reverb: decaying stereo noise IR (seeded), FFT convolution
irn = int(2.2 * SR); ti = np.arange(irn) / SR
irL = rng.standard_normal(irn) * np.exp(-ti * 3.2); irR = rng.standard_normal(irn) * np.exp(-ti * 3.2)
irL[: int(0.012 * SR)] = 0; irR[: int(0.017 * SR)] = 0
def conv(x, ir):
    n = len(x) + len(ir); nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[: len(x)]
wetL = conv(L, irL); wetR = conv(R, irR)
wetL *= np.max(np.abs(L)) / (np.max(np.abs(wetL)) + 1e-9) * 0.5; wetR *= np.max(np.abs(R)) / (np.max(np.abs(wetR)) + 1e-9) * 0.5
L2 = L + wetL; R2 = R + wetR
# soft lowpass (one-pole) to keep it warm and out of the voice's presence band
def lp(x, fc=5200):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i in range(len(x)): z = (1 - a) * x[i] + a * z; y[i] = z
    return y
L2 = lp(L2); R2 = lp(R2)
fade = np.ones(N); fi = int(0.08 * SR); fo = int(1.6 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo) ** 1.5
L2 *= fade; R2 *= fade
pk = max(np.max(np.abs(L2)), np.max(np.abs(R2))); L2 *= 0.7 / pk; R2 *= 0.7 / pk
out = (np.stack([L2, R2], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('wrote', sys.argv[1])
