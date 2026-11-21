"""Build THE SHADOW TRIAL - Episode 1 (ചാരം / Ashes).
Stills -> Ken Burns clips with effects -> concat -> letterbox/grain/subtitles; numpy sound design + MMS Malayalam TTS.
Usage: python build.py <work_dir> <out.mp4>
Expects <work_dir>/ep1/*.png (stills) and venv with torch, transformers, scipy."""
import os, sys, subprocess, json
import numpy as np, scipy.io.wavfile as wavf, scipy.signal as sig

W = sys.argv[1]; OUT = sys.argv[2]
IMG = os.path.join(W, "ep1"); TMP = os.path.join(W, "ep1_build"); os.makedirs(TMP, exist_ok=True)
FPS, SR = 24, 48000
rng = np.random.default_rng(7)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

# ---------------------------------------------------------------- timeline
# (start, dur, image or None for black, motion, effect, rain)
SHOTS = [
    (0,   5,  None,                 None,     None,      True),
    (5,   7,  "s02_highway_5",      "in",     None,      True),
    (12,  8,  "s03_crash_5",        "in",     "crash",   True),
    (20,  8,  "s04_firecrew_5",     "left",   "police",  True),
    (28,  10, "s05_idcard_17",      "in",     "police",  True),
    (38,  4,  None,                 None,     None,      False),
    (42,  8,  "s07_club_5",         "right",  "club",    False),
    (50,  10, "s08_rona_5",         "in",     "club",    False),
    (60,  10, "s09_christy_5",      "in",     "club",    False),
    (70,  8,  "basement_crop",      "in",     None,      False),
    (78,  8,  "s11_lightsoff_5",    "in",     "lightsoff", False),
    (86,  6,  "s12_figure_5",       "in",     None,      False),
    (92,  6,  "s13_stungun_5",      "in",     "stun",    False),
    (98,  6,  "s14_van_5",          "out",    None,      True),
    (104, 5,  "s15_shadow_17",      "in",     None,      True),
    (109, 7,  None,                 None,     None,      False),
]
TOTAL = 116

# ---------------------------------------------------------------- subtitles / titles (ASS)
def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
EV = []
def title(a, b, ml, en=None):
    txt = r"{\fad(600,600)}" + ml + (r"\N{\fs34\b0\c&HB0B0B0&}" + en if en else "")
    EV.append(f"Dialogue: 0,{ts(a)},{ts(b)},Title,,0,0,0,,{txt}")
def sub(a, b, ml, en):
    EV.append(f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{ml}" + r"\N{\fs30\c&HC8C8C8&}" + en)
def cap(a, b, t):
    EV.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(300,300)}}{t}")

title(0.6, 4.6, "360 ദിവസം മുൻപ്", "360 DAYS AGO — WALAYAR HIGHWAY")
cap(30.5, 37.5, "DR. ANJALI DAS — SENIOR BIO-ENGINEER")
title(38.3, 41.8, "ഇന്ന് — കൊച്ചി", "PRESENT DAY — KOCHI")
cap(70.5, 77, "11:40 PM — BASEMENT PARKING")
title(109.5, 115.5, r"{\fs96}THE SHADOW TRIAL", "നിഴൽ വിചാരണ  ·  EPISODE 1 — ചാരം (ASHES)")

LINES = [  # (start, who, malayalam, english)
    (29.6, "radio",   "അനിയന്റെ മരണശേഷമുള്ള കടുത്ത വിഷാദം... ആത്മഹത്യ. കേസ് ക്ലോസ്ഡ്.",
                      "Severe depression after her brother's death... suicide. Case closed."),
    (51.2, "rona",    "ചിയേഴ്സ് ക്രിസ്റ്റീ! ഷെൽ കമ്പനിക്ക് അപ്രൂവൽ കിട്ടി. ഇനി ആർക്കും നമ്മളെ തൊടാൻ പറ്റില്ല!",
                      "Cheers, Christy! The shell company got approved. Nobody can touch us now!"),
    (61.4, "christy", "രാഹുലിന്റെ ഗതി ഓർമ്മയുള്ളതുകൊണ്ട് ഒരുത്തനും ഇനി വാ തുറക്കില്ല!",
                      "After what happened to Rahul, nobody will dare open their mouth again!"),
]

# ---------------------------------------------------------------- voices
def tts():
    import torch
    from transformers import VitsModel, AutoTokenizer
    m = VitsModel.from_pretrained("facebook/mms-tts-mal"); tok = AutoTokenizer.from_pretrained("facebook/mms-tts-mal")
    out = []
    for i, (st, who, ml, en) in enumerate(LINES):
        raw = os.path.join(TMP, f"vo{i}_raw.wav"); fin = os.path.join(TMP, f"vo{i}.wav")
        torch.manual_seed(3 + i)
        with torch.no_grad():
            y = m(**tok(ml, return_tensors="pt")).waveform[0].numpy()
        wavf.write(raw, 16000, (y / np.abs(y).max() * 0.9).astype(np.float32))
        af = {
            "radio":   "highpass=f=400,lowpass=f=3000,acrusher=bits=10:mix=0.3,volume=1.4",
            "rona":    "rubberband=pitch=1.55:tempo=0.92,equalizer=f=3000:t=q:w=1:g=3,aecho=0.8:0.6:40:0.15",
            "christy": "rubberband=pitch=1.68:tempo=1.0,equalizer=f=4000:t=q:w=1:g=2,aecho=0.8:0.6:40:0.15",
        }[who]
        run(["ffmpeg", "-y", "-i", raw, "-af", af + ",aresample=48000", "-ac", "1", fin])
        sr, a = wavf.read(fin); a = a.astype(np.float32); a /= (np.abs(a).max() + 1e-9)
        dur = len(a) / SR
        sub(st, st + dur + 0.6, ml, en)
        out.append((st, who, a))
    return out

# ---------------------------------------------------------------- sound design
N = int(TOTAL * SR)
L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)
def at(t): return int(t * SR)
def add(x, t, g=1.0, pan=0.0):
    i = at(t); x = x[: max(0, N - i)]
    L[i:i + len(x)] += x * g * (1 - max(0, pan)); R[i:i + len(x)] += x * g * (1 + min(0, pan))
def env(n, a=0.01, r=0.3):
    e = np.ones(n, np.float32); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def lp(x, f, o=2): return sig.sosfilt(sig.butter(o, f, "low", fs=SR, output="sos"), x).astype(np.float32)
def hp(x, f, o=2): return sig.sosfilt(sig.butter(o, f, "high", fs=SR, output="sos"), x).astype(np.float32)
def bp(x, a, b, o=2): return sig.sosfilt(sig.butter(o, [a, b], "band", fs=SR, output="sos"), x).astype(np.float32)
def reverb(x, dec=1.2, wet=0.35):
    ir = noise(dec) * np.exp(-np.linspace(0, 6, int(dec * SR))).astype(np.float32); ir = lp(ir, 5000)
    y = sig.fftconvolve(x, ir)[: len(x) + len(ir) - 1].astype(np.float32)
    y = y / (np.abs(y).max() + 1e-9) * np.abs(x).max()
    xx = np.pad(x, (0, len(y) - len(x)))
    return (1 - wet) * xx + wet * y
def norm(x, p=1.0): return (x / (np.abs(x).max() + 1e-9) * p).astype(np.float32)
def tone(f, d, kind="sine"):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR if np.ndim(f) else 2 * np.pi * f * t
    return (np.sin(ph) if kind == "sine" else sig.sawtooth(ph)).astype(np.float32)

def rain(d, heavy=1.0):
    x = lp(hp(noise(d), 300), 7000) * 0.5
    drops = np.zeros(int(d * SR), np.float32)
    idx = rng.integers(0, len(drops), int(d * 60 * heavy)); drops[idx] = rng.uniform(-1, 1, len(idx))
    drops = bp(drops, 1500, 6000)
    return norm(x + drops * 3) * env(int(d * SR), 1.0, 1.0)

# rain beds
add(rain(38.5, 1.2), 0, 0.22); add(rain(18, 1.0), 98, 0.2)
# thunder
for t0 in (1.5, 24.0):
    th = lp(noise(4), 180, 4) * np.exp(-np.linspace(0, 4, 4 * SR)).astype(np.float32); add(norm(th), t0, 0.5)
# engine approach 5-12.5
d = 7.6; t = np.linspace(0, 1, int(d * SR))
f = 70 + 60 * t ** 2
eng = lp(tone(f, d, "saw") + 0.5 * tone(f * 2, d, "saw") + 0.3 * lp(noise(d), 400), 900) * (0.2 + 0.8 * t ** 2)
add(norm(eng) * env(len(eng), 0.5, 0.05), 5, 0.45, pan=0.0)
# crash 12.5
imp = norm(lp(noise(0.5), 3000) * np.exp(-np.linspace(0, 12, int(0.5 * SR))).astype(np.float32))
boom = norm(tone(np.linspace(80, 30, int(3 * SR)), 3) * np.exp(-np.linspace(0, 5, 3 * SR)).astype(np.float32))
rumble = norm(lp(noise(5), 250, 4) * np.exp(-np.linspace(0, 3, 5 * SR)).astype(np.float32))
glass = norm(hp(noise(1.2), 4000) * np.exp(-np.linspace(0, 6, int(1.2 * SR))).astype(np.float32))
add(imp, 12.5, 0.9); add(boom, 12.5, 0.9); add(rumble, 12.55, 0.7); add(glass, 12.55, 0.35)
# fire crackle 13-38
d = 25; cr = np.zeros(int(d * SR), np.float32); idx = rng.integers(0, len(cr), 1800); cr[idx] = rng.uniform(-1, 1, len(idx))
cr = bp(cr, 800, 5000) * 4 + lp(noise(d), 300) * 0.15
add(norm(cr) * env(len(cr), 0.5, 2), 13, 0.18)
# sirens 19-38
d = 19; t = np.arange(int(d * SR)) / SR
f = np.where((t % 1.4) < 0.7, 680, 920).astype(np.float32)
sir = lp(tone(sig.lfilter([1], [1, -0.9995], f) * 0.0005 + f * 0.9995, d), 2500) * env(int(d * SR), 3, 2)
add(norm(reverb(sir, 1.5, 0.5)), 19, 0.12, pan=-0.3)
# radio static & beeps around VO
st = bp(noise(8.5), 1000, 4000) * 0.5; add(norm(st) * env(len(st), 0.1, 0.3), 29.0, 0.05)
for b in (29.1, 37.0): add(tone(1400, 0.12) * env(int(0.12 * SR), 0.005, 0.02), b, 0.12)
# whoosh into title 37.6 & bass drop 42
def whoosh(d=1.2, up=True):
    n = noise(d); fc = np.linspace(300, 5000, len(n)) if up else np.linspace(5000, 300, len(n))
    out = np.zeros_like(n); s = 256
    for i in range(0, len(n), s):
        out[i:i+s] = bp(n[i:i+s+512], max(100, fc[i]*0.6), min(20000, fc[i]*1.4))[:len(n[i:i+s])]
    return norm(out * np.sin(np.linspace(0, np.pi, len(n))) ** 2)
add(whoosh(1.4), 36.8, 0.35)
add(norm(tone(np.linspace(90, 35, int(1.5 * SR)), 1.5) * np.exp(-np.linspace(0, 3, int(1.5 * SR)))), 42, 0.9)

# club music 42-86 (124 bpm); full 42-70, muffled 70-86
bpm = 124; beat = 60 / bpm
d = 44; mus = np.zeros(int(d * SR), np.float32)
kick = norm(tone(np.geomspace(150, 45, int(0.25 * SR)), 0.25) * np.exp(-np.linspace(0, 8, int(0.25 * SR))))
hat = norm(hp(noise(0.05), 7000) * np.exp(-np.linspace(0, 10, int(0.05 * SR))))
notes = [55, 55, 65.4, 49]
for k in range(int(d / beat)):
    i = int(k * beat * SR)
    if i + len(kick) < len(mus): mus[i:i + len(kick)] += kick
    j = int((k + 0.5) * beat * SR)
    if j + len(hat) < len(mus): mus[j:j + len(hat)] += hat * 0.25
    bf = notes[(k // 8) % 4]; bl = int(beat * 0.45 * SR)
    jb = int((k + 0.5) * beat * SR)
    if jb + bl < len(mus): mus[jb:jb + bl] += lp(tone(bf, beat * 0.45, "saw"), 400) * env(bl, 0.005, 0.05) * 0.5
pad = lp(sum(tone(f, d, "saw") for f in (220, 261.6, 329.6)), 1200) * 0.06 * (0.6 + 0.4 * np.sin(np.linspace(0, 40, int(d * SR))))
mus = norm(mus + pad)
split = int(28 * SR)
full = mus[:split] * env(split, 0.05, 0.4)
muff = lp(mus[split:], 250, 4) * env(len(mus) - split, 0.3, 6)
add(full, 42, 0.38); add(norm(reverb(muff, 1.5, 0.5)), 70, 0.4)
# crowd murmur in club
add(norm(bp(noise(28), 300, 2500)) * env(int(28 * SR), 1, 1), 42, 0.05)
# heels 70.3-78
for k in range(14):
    c = norm(hp(noise(0.04), 1500) * np.exp(-np.linspace(0, 12, int(0.04 * SR))))
    add(norm(reverb(c, 1.2, 0.5)), 70.3 + k * 0.5 + rng.uniform(-0.04, 0.04), 0.25, pan=(-0.2 if k % 2 else 0.2))
# light clunks 78-86
for k in range(5):
    c = norm(lp(noise(0.15), 600) * np.exp(-np.linspace(0, 9, int(0.15 * SR))) + tone(60, 0.15) * np.exp(-np.linspace(0, 6, int(0.15 * SR))))
    add(norm(reverb(c, 2.0, 0.6)), 79 + k * 1.4, 0.55 + 0.08 * k)
# figure whoosh 86.4, stun 92.6, spray 95.4, gasp-thud 96
add(whoosh(0.9, False), 86.2, 0.5)
d = 2.2; zap = np.zeros(int(d * SR), np.float32); idx = rng.integers(0, len(zap), 6000); zap[idx] = rng.uniform(-1, 1, len(idx))
zap = norm(hp(zap, 2000) + 0.4 * tone(120, d, "saw")) * env(int(d * SR), 0.01, 0.3)
add(zap, 92.6, 0.5)
add(norm(hp(noise(0.9), 3000)) * env(int(0.9 * SR), 0.02, 0.3), 95.4, 0.3)
add(norm(lp(noise(0.3), 300) * np.exp(-np.linspace(0, 10, int(0.3 * SR)))), 96.2, 0.6)
# van: door slam 98.5, screech 99.2, engine away
add(norm(lp(noise(0.25), 800) * np.exp(-np.linspace(0, 14, int(0.25 * SR)))), 98.5, 0.8)
d = 1.8; scr = norm(bp(noise(d), 1800, 3200) + 0.5 * tone(np.linspace(2400, 2100, int(d * SR)), d)) * env(int(d * SR), 0.05, 0.6)
add(norm(reverb(scr, 1.2, 0.5)), 99.2, 0.3)
d = 4.5; t = np.linspace(0, 1, int(d * SR))
van = lp(tone(70 + 40 * t, d, "saw"), 700) * (1 - t) ** 2
add(norm(van), 99.4, 0.35)
# tension drone 68-109 and heartbeat 103-116
d = 41; t = np.arange(int(d * SR)) / SR
dr = lp(tone(41.2, d, "saw") + tone(41.6, d, "saw") + 0.5 * tone(61.7, d, "saw"), 300) * (0.5 + 0.5 * t / d)
add(norm(dr) * env(len(dr), 6, 2), 68, 0.18)
hb = norm(tone(np.geomspace(70, 40, int(0.18 * SR)), 0.18) * np.exp(-np.linspace(0, 7, int(0.18 * SR))))
for k in range(12):
    b = 103.5 + k * 1.05
    add(hb, b, 0.6); add(hb, b + 0.28, 0.4)
# title hit 109.3
add(boom, 109.3, 0.9); add(norm(reverb(imp, 2.5, 0.7)), 109.3, 0.4)

# voices (with ducking)
VOICES = tts()
for st, who, a in VOICES:
    g = {"radio": 0.75, "rona": 0.95, "christy": 0.95}[who]
    i = at(st); n = len(a); duck = np.ones(N, np.float32); duck[max(0, i - 4800):i + n + 9600] = 0.45
    L *= duck; R *= duck
    add(a, st, g, pan=(0.15 if who == "rona" else -0.15 if who == "christy" else 0))

import score
bgm = score.make_score(TOTAL)
for st, who, a in VOICES:  # duck score under dialogue
    i = at(st); bgm[max(0, i - 4800):i + len(a) + 9600] *= 0.4
L += bgm[:, 0] * 0.55; R += bgm[:, 1] * 0.55
mix = np.stack([L, R], 1)
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.6) * 0.89
wavf.write(os.path.join(TMP, "mix.wav"), SR, mix.astype(np.float32))

# ---------------------------------------------------------------- motion clips (2.5D depth parallax)
from multiprocessing import Pool
import motion
DEP = os.path.join(W, "ep1_depth")
def P(name): return os.path.join(IMG, name + ".png"), os.path.join(DEP, name + ".png")
R = [("rain", 380)]
SPEC = [
  dict(img=None, dur=5, dust=True),
  dict(n="s02_highway_5", dur=7, cam=dict(z=(1.0, 1.22), dolly=(0, 0.35), py=(0, -20)), particles=R, shake=6, shake_freq=1.6, whip_out=0),
  dict(n="s03_crash_5", dur=8, cam=dict(z=(1.05, 1.2), px=(-70, 70), dolly=(0.1, 0.2)), particles=[("embers", 140)] + R, fire=True,
       hits=[(0.0, 40)], flashes=[(0.0, 0.9)], shake=5),
  dict(n="s04_firecrew_5", dur=8, cam=dict(z=(1.08, 1.12), x=(-90, 90), px=(-110, 110)), particles=[("embers", 80)] + R, fire=True, fx="police", shake=4),
  dict(n="s05_idcard_17", dur=10, cam=dict(z=(1.0, 1.3), rot=(-2, 1.5), dolly=(0, 0.25)), particles=R, fire=True, fx="police", shake=2, whip_out=1),
  dict(img=None, dur=4, dust=True),
  dict(n="s07_club_5", dur=8, cam=dict(z=(1.1, 1.18), x=(80, -80), px=(120, -120)), fx="club", t0=42, whip_in=1, shake=3,
       punches=[(42 - 42 + i * 60 / 124 * 4, 0.025) for i in range(4)]),
  dict(n="s08_rona_5", dur=10, cam=dict(z=(1.05, 1.22), px=(-90, 90), rot=(1, -1)), fx="club", t0=50, shake=3, particles=[("dust", 40)]),
  dict(n="s09_christy_5", dur=10, cam=dict(z=(1.18, 1.04), px=(90, -90), rot=(-1, 1)), fx="club", t0=60, shake=3, particles=[("dust", 40)], whip_out=1),
  dict(n="bs_b", crop=(200, 110, 540, 304), dur=8, cam=dict(z=(1.0, 1.18), dolly=(0, 0.3)), fx="basement", particles=[("dust", 70)], shake=5, shake_freq=1.3, whip_in=1),
  dict(n="s11_lightsoff_5", dur=8, cam=dict(z=(1.0, 1.15), dolly=(0, 0.25)), fx="lightsoff", hits=[(st, 8) for st in (1.0, 2.4, 3.8, 5.2, 6.6)], shake=3),
  dict(n="s12_figure_5", dur=6, cam=dict(z=(1.0, 1.4), dolly=(0, 0.5), px=(60, -60)), hits=[(0.2, 25)], particles=[("dust", 50)], shake=4, ca=1),
  dict(n="s13_stungun_5", dur=6, cam=dict(z=(1.1, 1.25), rot=(2, -2)), fx="stun", hits=[(0.6, 30), (1.6, 15)], punches=[(0.6, 0.08)], shake=6, ca=2),
  dict(n="s14_van_5", dur=6, cam=dict(z=(1.3, 1.0), dolly=(0.4, 0), px=(0, 0)), hits=[(0.5, 25)], particles=[("dust", 60)], shake=6, whip_out=0),
  dict(n="s15_shadow_17", dur=5, cam=dict(z=(1.0, 1.15), px=(-50, 30), dolly=(0, 0.2)), particles=R, shake=2,
       punches=[(103.5 + k * 1.05 - 104, 0.02) for k in range(1, 5)], fade_out=0.6),
  dict(img=None, dur=7),
]
assert sum(x["dur"] for x in SPEC) == TOTAL
clips, jobs = [], []
for k, sp in enumerate(SPEC):
    sp = dict(sp); out = os.path.join(TMP, f"m{k:02d}.mp4"); clips.append(out); sp["out"] = out; sp["seed"] = k + 3
    if "n" in sp: sp["img"], sp["depth"] = P(sp.pop("n"))
    if not os.path.exists(out): jobs.append(sp)
with Pool(4) as pool:
    for o in pool.imap_unordered(motion.render_shot, jobs): print("clip", os.path.basename(o), flush=True)

lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(TMP, "raw.mp4")])

# ---------------------------------------------------------------- ASS + final
ass = os.path.join(TMP, "ep1.ass")
open(ass, "w", encoding="utf-8").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Noto Sans Malayalam,42,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2.5,1,2,120,120,150,1
Style: Title,Noto Sans Malayalam,70,&H00F0F0F0,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,60,60,60,1
Style: Cap,Inter,30,&H00D8D8D8,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,4,0,1,1.5,0,7,160,160,170,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(EV) + "\n")
bar = 138
vf = (f"curves=preset=medium_contrast,vignette=PI/4.5,noise=alls=4:allf=t,"
      f"drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill,"
      f"fade=t=in:st=0:d=1,ass={ass}")
run(["ffmpeg", "-y", "-i", os.path.join(TMP, "raw.mp4"), "-i", os.path.join(TMP, "mix.wav"), "-vf", vf,
     "-c:v", "libx264", "-crf", "25", "-preset", "medium", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-shortest", "-movflags", "+faststart", OUT])
print("done", OUT)
