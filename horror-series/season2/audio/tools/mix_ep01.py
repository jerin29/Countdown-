"""COUNTDOWN S2 Ep 1 soundtrack (Malayalam): voices (ElevenLabs), sound effects (ElevenLabs), a dark bed and 40 bells.
Writes horror-series/season2/audio/mix/ep01_ml.wav (48 kHz stereo, -14 LUFS, -1 dBTP).
Usage: python3 mix_ep01.py
"""
import os, subprocess, json
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.dirname(HERE)
LANG = os.environ.get("S2LANG", "ml")
VO, FX, OUT = os.path.join(A, f"voice_{LANG}"), os.path.join(A, "sfx_el"), os.path.join(A, "mix")
DUR = 90.0
CHIMES = [36 + 28.5 * (1 - (1 - i / 39) ** 1.6) for i in range(40)]


def load(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af: cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


mix = np.zeros((int(DUR * SR) + SR, 2), np.float32)


def place(x, t, db=0.0, pan=0.0, pan_to=None, fade_in=0.0, fade_out=0.0, length=None):
    """add clip x at time t; pan -1..1 (or a sweep pan -> pan_to)"""
    x = x.copy()
    if length: x = x[: int(length * SR)]
    n = len(x)
    if fade_in: k = min(n, int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(n, int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    p = np.full(n, pan) if pan_to is None else np.linspace(pan, pan_to, n)
    mono = x.mean(axis=1)
    l, r = np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4)
    st = np.stack([mono * l, mono * r], 1) * 10 ** (db / 20) * np.sqrt(2)
    i = int(t * SR); j = min(len(mix), i + n)
    if j > i: mix[i:j] += st[: j - i]


def loop_to(x, seconds, xf=1.0):
    """loop a clip with crossfades until it lasts `seconds`"""
    n, k = int(seconds * SR), int(xf * SR)
    out = x.copy()
    while len(out) < n:
        a, b = out[-k:] * np.linspace(1, 0, k)[:, None], x[:k] * np.linspace(0, 1, k)[:, None]
        out = np.concatenate([out[:-k], a + b, x[k:]])
    return out[:n]


WHISPER = "aecho=0.8:0.6:45|95:0.22|0.12,highpass=f=120"
v = {k[:-4]: load(os.path.join(VO, k), WHISPER if "clara" in k else "highpass=f=90") for k in os.listdir(VO) if k.endswith(".mp3")}
fx = {k[:-4]: load(os.path.join(FX, k)) for k in os.listdir(FX) if k.endswith(".mp3")}
# signature sound: the bell slowed and reversed, ending in a breath
sig = load(os.path.join(FX, "bell_toll.mp3"), "asetrate=48000*0.75,aresample=48000,areverse")
bells = [load(os.path.join(FX, "bell_toll.mp3"), f"asetrate=48000*{r},aresample=48000") for r in (1.0, 0.94, 1.06, 0.89)]

# ---- 0–3 hook ----
place(fx["clock_spin"], 0.0, -4)
place(fx["tick_loop"], 0.0, -20, length=2.0, fade_out=0.3)
place(v["e01_clara_hook"], 0.9, -3, pan=0.15)
place(fx["impact_hit"], 2.02, -1)
# ---- 3–8 headphone warning: whisper travels left → right; the signature swell leads into the story ----
place(v["e01_clara_warn"], 3.7, -4, pan=-0.95, pan_to=0.95)
place(sig, 8.0 - len(sig) / SR, -12, fade_in=1.0)
place(fx["breath_ear"], 7.0, -10, pan=0.6)
# ---- 8–70 bed: a dark drone (ducked to near-silence before the 40th chime's breath) ----
bed = loop_to(fx["drone_dark"], 62.5, 2.0)
env = np.ones(len(bed), np.float32)
def ramp(a, b, g0, g1):
    i, j = int((a - 8) * SR), int((b - 8) * SR); env[i:j] = np.linspace(g0, g1, j - i)
ramp(8, 10, 0, 1)
ramp(64.6, 65.4, 1, 0.02); env[int((65.4 - 8) * SR):int((67.3 - 8) * SR)] = 0.02; ramp(67.3, 69.0, 0.02, 0.8)
bed *= env[:, None]
place(bed, 8.0, -9)
# ticking in the room, louder as he wakes, gone as we pass through the glass
tick = loop_to(fx["tick_loop"], 26.0, 0.5)
tick *= np.interp(np.arange(len(tick)) / SR, [0, 4, 10, 14, 23, 26], [0, .35, .5, 1, .8, 0])[:, None]
place(tick, 8.0, -10, pan=-0.2)
place(v["e01_aadi_wake"], 19.6, -2, pan=-0.35)
place(fx["whoosh_dark"], 31.0, -5)
place(fx["glass_creak"], 32.4, -12, pan=0.3)
# ---- 36–64.5 forty bells, closer together, alternating sides ----
for i, c in enumerate(CHIMES):
    b = bells[i % 4]
    place(b, c, -4 - 3 * (i % 3 == 2), pan=[-0.5, 0.5, 0.0, -0.25, 0.25][i % 5], fade_out=0.8)
place(v["e01_aadi_count1"], CHIMES[0] + 0.5, -1, pan=-0.1)
place(v["e01_aadi_count2"], 47.4, -1, pan=-0.1)
place(v["e01_aadi_count3"], 61.2, -1, pan=-0.1)
# ---- after the fortieth: silence… then a breath right behind your ear (left → right) ----
place(fx["breath_ear"], 66.6, -2, pan=-0.9, pan_to=0.9)
place(fx["giggle"], 70.6, -14, pan=0.85)
place(v["e01_clara_line"], 73.4, -2, pan=0.45)
place(fx["glass_creak"], 76.6, -8, pan=-0.2)
place(fx["impact_hit"], 78.38, 0)
# ---- 80–85 count card: one deep bell; 85–90 the title song's ending under the credits ----
place(bells[3], 80.0, -2)
place(fx["impact_hit"], 80.35, -6)
song = load(os.path.join(A, "..", "song", {"ml": "naalpathu-ml-v2_master.mp3", "hi": "chaalis-hi_master.mp3", "ta": "naarpathu-ta_master.mp3"}[LANG]))
place(song[-int(6.0 * SR):], 84.6, -6, fade_in=0.6, fade_out=1.2)

# ---- extra horror layer ----
import sys; sys.path.insert(0, os.path.join(A, "..", "video", "tools")); import horrorfx as HFX
hb = fx["heartbeat"]
def thumps(times, db):
    one = hb[: int(.42 * SR)] * np.hanning(int(.42 * SR))[:, None]
    for i, b in enumerate(times[::2]): place(one, b, db, pan=0.0)
thumps(HFX.heartbeats(12, 19.2, 62, 118), -8)
thumps(HFX.heartbeats(36.5, 64.4, 84, 112), -12)
thumps(HFX.heartbeats(70.5, 79.2, 120, 150), -6)
for t0 in (2.12, 27.4, 71.0, 75.2): place(fx["screech"], t0, -7, pan=0.3 if t0 % 2 > 1 else -0.3)
for t0 in (2.05, 18.0, 27.3, 32.9, 50.2, 64.5, 70.9, 78.38, 80.0): place(fx["static_glitch"], t0, -14, length=0.5, fade_out=0.15)
for t0 in (2.04, 33.0, 64.5, 78.38): place(fx["sub_drop"], t0, -4)
place(fx["rev_whisper"], 3.2, -15, pan=0.9, pan_to=-0.9, fade_in=0.5, fade_out=0.8)
place(fx["rev_whisper"], 65.4, -16, pan=-0.9, pan_to=0.9, fade_in=0.4, fade_out=0.6)
place(fx["steps_behind"], 20.4, -13, pan=0.75, fade_out=0.5)
place(fx["door_creak"], 24.6, -14, pan=-0.6)
place(loop_to(fx["wind_howl"], 27.0, 1.5), 33.0, -16, fade_in=2.0, fade_out=2.0)
place(loop_to(fx["clock_gears"], 28.0, 1.0), 36.0, -18, fade_in=3.0, fade_out=1.0)
place(loop_to(fx["low_choir"], 24.0, 2.0), 40.5, -17, fade_in=6.0, fade_out=1.5)
place(fx["scream_far"], 52.0, -17, pan=0.7)
place(fx["crowd_murmur"], 56.5, -18, fade_in=1.5, fade_out=1.0)
place(fx["water_drip"], 72.0, -20, pan=-0.5, length=5.0, fade_out=1.0)

# master: gentle limiting, -14 LUFS / -1 dBTP
mix = mix[: int(DUR * SR)]
peak = np.abs(mix).max(); mix = np.tanh(mix / max(peak, 1e-6) * 1.6) / np.tanh(1.6)
os.makedirs(OUT, exist_ok=True)
raw = os.path.join(OUT, f"ep01_{LANG}_raw.wav"); fin = os.path.join(OUT, f"ep01_{LANG}.wav")
import soundfile as sf
sf.write(raw, mix, SR, subtype="FLOAT")
m = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):])
lin = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
       f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", lin, "-ar", str(SR), fin], check=True)
os.remove(raw)
json.dump({"chimes": CHIMES}, open(os.path.join(OUT, "ep01_cues.json"), "w"), indent=1)
print("wrote", fin)
