"""Small synthesis toolkit for the COUNTDOWN soundtrack. Everything is computed (no samples)."""
import numpy as np
from scipy import signal
import soundfile as sf
import subprocess, os

SR = 48000
rng = np.random.default_rng(1986)


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def silence(dur, ch=2):
    return np.zeros((int(dur * SR), ch)) if ch == 2 else np.zeros(int(dur * SR))


def note_hz(name):
    """'D4' / 'Bb3' / 'C#5' -> Hz."""
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n = names[name[0]]
    rest = name[1:]
    if rest[0] == '#':
        n += 1; rest = rest[1:]
    elif rest[0] == 'b':
        n -= 1; rest = rest[1:]
    octave = int(rest)
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12)


# ---------- envelopes / filters ----------

def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na, endpoint=False)
    nd = min(nd, n - na); e[na:na + nd] = np.linspace(1, s, nd, endpoint=False)
    nr = min(nr, n)
    if nr > 0:
        e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype='band', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def lowpass(x, f, order=2):
    sos = signal.butter(order, f, btype='low', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def highpass(x, f, order=2):
    sos = signal.butter(order, f, btype='high', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=0)


def resonator(x, f, q):
    """Two-pole resonant bandpass (peaking) at f with quality q."""
    b, a = signal.iirpeak(f, q, fs=SR)
    return signal.lfilter(b, a, x)


def sweep_lowpass(x, f_start, f_end, q=0.7):
    """Time-varying one-pole-ish lowpass via block processing (cheap, smooth enough for pads/stabs)."""
    out = np.zeros_like(x)
    block = 512
    zi = None
    n = len(x)
    for i in range(0, n, block):
        frac = i / max(1, n - 1)
        f = f_start * (f_end / f_start) ** frac
        sos = signal.butter(2, min(f, SR * 0.45), btype='low', fs=SR, output='sos')
        if zi is None:
            zi = signal.sosfilt_zi(sos) * 0
        seg, zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
        out[i:i + block] = seg
    return out


# ---------- sources ----------

def noise(n):
    return rng.standard_normal(n)


def pink(n):
    w = rng.standard_normal(n)
    b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    p = signal.lfilter(b, a, w)
    return p / (np.max(np.abs(p)) + 1e-9)


def brown(n):
    b = np.cumsum(rng.standard_normal(n))
    b = highpass(b, 20)
    return b / (np.max(np.abs(b)) + 1e-9)


def saw(freq, dur, harmonics=None, vib_rate=0, vib_depth=0, phase=0.0):
    """Band-limited sawtooth with optional vibrato (depth in semitones)."""
    t = t_axis(dur)
    if vib_depth:
        f = freq * 2 ** (vib_depth / 12 * np.sin(2 * np.pi * vib_rate * t + rng.uniform(0, 6.28)))
    else:
        f = np.full_like(t, freq)
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    nmax = harmonics or max(1, min(40, int((SR * 0.45) / freq)))
    out = np.zeros_like(t)
    for k in range(1, nmax + 1):
        out += np.sin(k * ph) / k
    return out * 0.6


# ---------- instruments ----------

def music_box_note(freq, dur=2.5, detune_cents=0.0, bright=1.0):
    """Comb-tine: strong fundamental, inharmonic upper modes, tiny pluck click."""
    t = t_axis(dur)
    f = freq * 2 ** (detune_cents / 1200)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.4)
         + 0.25 * bright * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.5)
         + 0.18 * bright * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.12)
         + 0.08 * bright * np.sin(2 * np.pi * f * 8.9 * t) * np.exp(-t / 0.05))
    click = highpass(noise(len(t)), 3000) * np.exp(-t / 0.002) * 0.15
    a = np.minimum(1, t / 0.002)
    return (x * a + click) * 0.5


def piano_note(freq, dur=3.0, vel=0.8):
    """Additive piano-ish string with inharmonicity and hammer noise."""
    t = t_axis(dur)
    B = 0.0004
    x = np.zeros_like(t)
    for k in range(1, 14):
        fk = k * freq * np.sqrt(1 + B * k * k)
        if fk > SR * 0.45:
            break
        amp = (1 / k ** 1.3) * (0.6 + 0.4 * vel)
        tau = 2.5 / (1 + 0.35 * k) * (220 / max(freq, 80)) ** 0.3
        x += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    hammer = lowpass(noise(len(t)), 2500) * np.exp(-t / 0.008) * 0.08 * vel
    rel = np.ones_like(t); nr = int(0.15 * SR); rel[-nr:] = np.linspace(1, 0, nr)
    return (x * np.minimum(1, t / 0.003) + hammer) * rel * 0.35


def string_pad(freq, dur, voices=3, vib=0.08, attack=1.5, release=1.5, bright=2500):
    out = np.zeros(int(dur * SR))
    for v in range(voices):
        det = rng.uniform(-8, 8)
        out += saw(freq * 2 ** (det / 1200), dur, vib_rate=rng.uniform(4.5, 5.5), vib_depth=vib)
    out = lowpass(out / voices, bright)
    bow = bandpass(noise(len(out)), freq * 2, min(freq * 8, 9000)) * 0.03
    return (out + bow) * adsr(len(out), attack, 0.2, 1.0, release)


def choir(freqs, dur, vowel='a', attack=2.0, release=2.0, breath=0.15):
    """Formant-filtered detuned saws: an 'aah' choir."""
    formants = {'a': [(730, 80), (1090, 90), (2440, 120)], 'o': [(570, 70), (840, 80), (2410, 120)],
                'u': [(300, 50), (870, 80), (2240, 120)]}[vowel]
    n = int(dur * SR)
    src = np.zeros(n)
    for f in freqs:
        for v in range(4):
            src += saw(f * 2 ** (rng.uniform(-12, 12) / 1200), dur, vib_rate=rng.uniform(4.8, 5.8), vib_depth=0.12)
    src += breath * pink(n)
    out = np.zeros(n)
    for fc, bw in formants:
        out += bandpass(src, fc - bw, fc + bw, order=2)
    out /= (np.max(np.abs(out)) + 1e-9)
    return out * adsr(n, attack, 0.3, 1.0, release) * 0.5


def tower_bell(fund=98.0, dur=9.0, detune=1.0):
    """Minor-third church bell: hum, prime, tierce, quint, nominal... slightly out of tune, with beating."""
    t = t_axis(dur)
    partials = [(0.5, 0.6, 6.0), (1.0, 0.8, 4.5), (1.19, 0.55, 3.5), (1.5, 0.3, 2.6), (2.0, 0.7, 2.4),
                (2.51, 0.25, 1.6), (2.66, 0.25, 1.4), (3.01, 0.2, 1.1), (4.17, 0.15, 0.7), (5.43, 0.1, 0.45),
                (6.8, 0.06, 0.3)]
    x = np.zeros_like(t)
    for r, a, tau in partials:
        f = fund * r * (1 + rng.uniform(-0.004, 0.004) * detune)
        beat = 1 + 0.25 * np.sin(2 * np.pi * rng.uniform(0.3, 1.2) * t)  # doublet beating
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / tau) * beat
    strike = bandpass(noise(len(t)), 800, 6000) * np.exp(-t / 0.01) * 0.6
    clang = lowpass(noise(len(t)), 400) * np.exp(-t / 0.05) * 0.5
    return (x * np.minimum(1, t / 0.002) + strike + clang) * 0.35


def modal_hit(freqs, taus, amps, dur, excite_tau=0.003, noise_amt=0.3):
    t = t_axis(dur)
    x = np.zeros_like(t)
    for f, tau, a in zip(freqs, taus, amps):
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    x += noise_amt * noise(len(t)) * np.exp(-t / excite_tau)
    return x


def tick(dur=0.12, bright=1.0, pitch=1.0):
    """Close pocket-watch escapement tick: two tiny metallic clicks a few ms apart."""
    t = t_axis(dur)
    x = np.zeros_like(t)
    for off, a in [(0.0, 1.0), (0.006, 0.55)]:
        i = int(off * SR)
        tt = t[: len(t) - i]
        burst = highpass(noise(len(tt)), 1800 * pitch) * np.exp(-tt / 0.0015)
        ring = (np.sin(2 * np.pi * 4200 * pitch * tt) * 0.5 + np.sin(2 * np.pi * 6900 * pitch * tt) * 0.3) * np.exp(-tt / 0.006)
        x[i:] += a * (burst + bright * ring)
    body = resonator(x, 900 * pitch, 6) * 0.6
    return (x * 0.5 + body) * 0.6


# ---------- space ----------

def reverb_ir(seconds=2.5, predelay=0.02, damp=4000, stereo=True, early=True):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    chans = []
    for c in range(2 if stereo else 1):
        tail = noise(n) * np.exp(-t * 6.9 / seconds)
        tail = lowpass(tail, damp)
        if early:
            for k in range(8):
                i = int(rng.uniform(0.003, 0.06) * SR)
                tail[i] += rng.uniform(0.3, 0.8) * (-1) ** k
        pd = np.zeros(int(predelay * SR))
        chans.append(np.concatenate([pd, tail]))
    ir = np.stack(chans, axis=1)
    return ir / np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))


_IR_CACHE = {}


def reverb(x, seconds=2.5, wet=0.3, damp=4000, predelay=0.02):
    key = (seconds, damp, predelay)
    if key not in _IR_CACHE:
        _IR_CACHE[key] = reverb_ir(seconds, predelay, damp)
    ir = _IR_CACHE[key]
    x = to_stereo(x)
    pad = np.zeros((ir.shape[0], 2))
    xp = np.concatenate([x, pad])
    wetsig = np.stack([signal.fftconvolve(xp[:, c], ir[:, c])[: len(xp)] for c in range(2)], axis=1)
    return xp * (1 - wet) + wetsig * wet


def to_stereo(x, pan=0.0):
    if x.ndim == 2:
        return x
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l * 1.414, x * r * 1.414], axis=1)


def place(buf, x, at, gain=1.0, pan=0.0):
    """Mix x into buf at time `at` (seconds). Extends nothing: clips to buf length."""
    x = to_stereo(x, pan) * gain
    i = int(at * SR)
    if i >= len(buf):
        return buf
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]
    return buf


def fade(x, fin=0.01, fout=0.05):
    x = x.copy()
    ni, no = int(fin * SR), int(fout * SR)
    if ni:
        x[:ni] *= np.linspace(0, 1, ni)[:, None] if x.ndim == 2 else np.linspace(0, 1, ni)
    if no:
        x[-no:] *= np.linspace(1, 0, no)[:, None] if x.ndim == 2 else np.linspace(1, 0, no)
    return x


def loop_crossfade(x, xf=1.0):
    """Make a seamless loop: overlap the tail onto the head and cut the tail."""
    n = int(xf * SR)
    x = to_stereo(x).copy()
    head, tail = x[:n], x[-n:]
    w = np.linspace(0, 1, n)[:, None]
    x[:n] = head * w + tail * (1 - w)
    return x[:-n]


def tape_wobble(x, rate=0.6, depth_ms=2.5):
    """Wow/flutter by time-varying delay (cassette feel)."""
    x = to_stereo(x)
    n = len(x)
    t = np.arange(n) / SR
    d = (depth_ms / 1000) * SR * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) + \
        (depth_ms / 4000) * SR * np.sin(2 * np.pi * 7.3 * t)
    idx = np.clip(np.arange(n) - d, 0, n - 1)
    i0 = np.floor(idx).astype(int); fr = idx - i0
    i1 = np.minimum(i0 + 1, n - 1)
    return x[i0] * (1 - fr)[:, None] + x[i1] * fr[:, None]


def crackle(n, density=8.0, level=0.15):
    x = np.zeros(n)
    k = int(density * n / SR)
    pos = rng.integers(0, n - 200, k)
    for p in pos:
        L = rng.integers(10, 120)
        x[p:p + L] += rng.uniform(-1, 1) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1)
    hiss = highpass(noise(n), 3000) * 0.02
    return (highpass(x, 800) + hiss) * level


# ---------- output ----------

def normalize_peak(x, peak_db=-1.0):
    p = np.max(np.abs(x)) + 1e-12
    return x * (10 ** (peak_db / 20) / p)


def write(path, x, peak_db=-1.0, mp3=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = normalize_peak(to_stereo(x) if x.ndim == 2 else x, peak_db)
    if mp3:
        tmp = path[:-4] + ".tmp.wav"
        sf.write(tmp, x, SR, subtype='PCM_24')
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libmp3lame", "-b:a", "320k", path],
                       check=True)
        os.remove(tmp)
    else:
        sf.write(path, x, SR, subtype='PCM_16')
    return path
