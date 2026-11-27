"""COUNTDOWN S2 · Episodes 2–15 soundtrack (shared mixer). Usage: python3 s2mix.py N [--lang ml]
Timelines in video/tools/eps.py. Common to every episode: hook spin/impact, headphone-warning whisper travelling L→R,
reversed whispers, the signature reversed bell, a dark bed, whooshes between scenes, a silence before the final
scare, a heartbeat build, the count-card bell, and the title song's ending under the credits."""
import os, sys, json, subprocess, argparse
import numpy as np, soundfile as sf

SR, DUR = 48000, 90.0
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(A, '..', 'video', 'tools'))
from eps import EPS
import horrorfx as HFX

_cache = {}
def load(path, af=None):
    k = (path, af)
    if k not in _cache:
        cmd = ['ffmpeg', '-v', 'error', '-i', path] + (['-af', af] if af else []) + ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
        _cache[k] = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    return _cache[k]

def loop_to(x, seconds, xf=1.0):
    n, k = int(seconds * SR), int(xf * SR); out = x.copy()
    while len(out) < n:
        out = np.concatenate([out[:-k], out[-k:] * np.linspace(1, 0, k)[:, None] + x[:k] * np.linspace(0, 1, k)[:, None], x[k:]])
    return out[:n]

def mix_episode(n, lang='ml'):
    E = EPS[n]
    mix = np.zeros((int(DUR * SR) + SR, 2), np.float32)
    def place(x, t, db=0., pan=0., pan_to=None, fade_in=0., fade_out=0., length=None):
        x = x.copy()
        if length: x = x[:int(length * SR)]
        m = len(x)
        if m == 0: return
        if fade_in: k = min(m, int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
        if fade_out: k = min(m, int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
        p = np.full(m, pan) if pan_to is None else np.linspace(pan, pan_to, m)
        mono = x.mean(1); st = np.stack([mono * np.cos((p + 1) * np.pi / 4), mono * np.sin((p + 1) * np.pi / 4)], 1) * 10 ** (db / 20) * np.sqrt(2)
        i = int(t * SR); j = min(len(mix), i + m)
        if j > i: mix[i:j] += st[:j - i]
    FX = lambda k: load(os.path.join(A, 'sfx_el', k + '.mp3'))
    WHISPER = 'aecho=0.8:0.6:45|95:0.22|0.12,highpass=f=120'
    PHONE = 'highpass=f=350,lowpass=f=3300,acrusher=bits=10:mix=0.25'
    def V(key, filt=None):
        p = os.path.join(A, f'voice_{lang}', key + '.mp3')
        return load(p, filt or (WHISPER if 'clara' in key or 'refl' in key else 'highpass=f=90'))
    # ---- hook + warning (common) ----
    place(FX('clock_spin'), 0.0, -8); place(FX('impact_hit'), 2.02, -1); place(FX('sub_drop'), 2.04, -4)
    place(FX('screech'), 2.1, -8, pan=.3); place(FX('static_glitch'), 2.0, -14, length=.5)
    place(V('e01_clara_warn'), 3.7, -4, pan=-.95, pan_to=.95)
    place(FX('rev_whisper'), 3.2, -15, pan=.9, pan_to=-.9, fade_in=.5, fade_out=.8)
    sig = load(os.path.join(A, 'sfx_el', 'bell_toll.mp3'), 'asetrate=48000*0.75,aresample=48000,areverse')
    place(sig, 8.0 - len(sig) / SR, -12, fade_in=1.0)
    # ---- beds ----
    for t0, t1, key, db in E.get('bed', []):
        b = loop_to(FX(key), t1 - t0, 1.5)
        env = np.ones(len(b), np.float32); r = min(len(b), int(1.5 * SR)); env[:r] = np.linspace(0, 1, r)
        if E['count'] > 0 and t1 >= 78:   # silence before the final scare
            i0, i1 = int((76.9 - t0) * SR), int((78.3 - t0) * SR)
            if 0 < i0 < len(env): env[i0:min(len(env), i1)] = .03
        place(b * env[:, None], t0, db, fade_out=1.0)
    # ---- whooshes through the darkness between scenes ----
    for (t0, t1, *_r) in E['segs']:
        if t0 >= 8 and t0 > 8.5: place(FX('whoosh_dark'), t0 - 1.2, -9)
    # ---- voices ----
    for v in E.get('voice', []):
        t, key, db, pan = v[:4]
        place(V(key, PHONE if len(v) > 4 and v[4] == 'phone' else None), t, db, pan=pan)
    # ---- episode sound effects ----
    for t, key, db, pan in E.get('sfx', []): place(FX(key), t, db, pan=pan, fade_out=.4)
    # ---- heartbeat ----
    hb = FX('heartbeat'); one = hb[:int(.42 * SR)] * np.hanning(int(.42 * SR))[:, None]
    beats = []
    for a, b, b0, b1 in E.get('heart', []): beats += HFX.heartbeats(a, b, b0, b1)[::2]
    if E['count'] > 0: beats += HFX.heartbeats(70.5, 76.8, 118, 150)[::2]
    for bt in beats: place(one, bt, -9)
    # ---- special beds ----
    song = load(os.path.join(A, '..', 'song', {'ml': 'naalpathu-ml-v2_master.mp3', 'hi': 'chaalis-hi_master.mp3', 'ta': 'naarpathu-ta_master.mp3'}[lang]))
    for t0, t1, db in E.get('music', []): place(song[:int((t1 - t0) * SR)], t0, db, fade_in=2, fade_out=2)
    for t0, t1 in E.get('dawn_music', []):
        p = os.path.join(A, '..', '..', 'audio', 'songs', 'wind-it-back-ml.mp3')
        if os.path.exists(p): place(load(p)[:int((t1 - t0) * SR)], t0, -10, fade_in=3, fade_out=3)
    # ---- final scare (silence → hit) ----
    if E['count'] > 0:
        place(FX('impact_hit'), 78.38, 0); place(FX('sub_drop'), 78.38, -3); place(FX('screech'), 78.45, -6, pan=-.3)
        place(FX('static_glitch'), 78.38, -12, length=.6)
    else:
        place(FX('breath_ear'), 78.2, -6, pan=-.9, pan_to=.9)
    # ---- count card + credits ----
    place(load(os.path.join(A, 'sfx_el', 'bell_toll.mp3'), 'asetrate=48000*0.89,aresample=48000'), 80.0, -2)
    place(FX('impact_hit'), 80.35, -6); place(FX('static_glitch'), 80.0, -16, length=.4)
    place(song[-int(6.0 * SR):], 84.6, -6, fade_in=.6, fade_out=1.2)
    # ---- master ----
    mix = mix[:int(DUR * SR)]
    peak = np.abs(mix).max(); mix = np.tanh(mix / max(peak, 1e-6) * 1.6) / np.tanh(1.6)
    out = os.path.join(A, 'mix'); os.makedirs(out, exist_ok=True)
    raw, fin = os.path.join(out, f'ep{n:02d}_{lang}_raw.wav'), os.path.join(out, f'ep{n:02d}_{lang}.wav')
    sf.write(raw, mix, SR, subtype='FLOAT')
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):])
    lin = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
           f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', lin, '-ar', str(SR), fin], check=True); os.remove(raw)
    print('wrote', fin)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('n', nargs='+', type=int); ap.add_argument('--lang', default='ml')
    a = ap.parse_args()
    for n in a.n: mix_episode(n, a.lang)
