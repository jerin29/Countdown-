"""Mix each episode's 1:30 soundtrack (dialogue + BGM + SFX) from the cue sheets below.
Times follow the scripts in malayalam/02-scripts-ml.md (a few dialogue lines are nudged so long lines don't overlap).

Cue: (time_s, source, gain, opts)
  source: "v:<line>" voice/processed, "sfx:<name>" sfx, "bgm:<name>" bgm, "end:<n>" end-card hum, "song:<name>" songs
  opts: dur (trim/loop to seconds), fin/fout (fade seconds), pan
"""
import os, sys, subprocess
import numpy as np
import soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from dsp import SR, to_stereo

A = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(A, "episodes")
os.makedirs(OUT, exist_ok=True)
DUR = 90.0
_cache = {}


def load(src):
    if src in _cache:
        return _cache[src]
    kind, name = src.split(":", 1)
    if kind == "end":
        name = f"{int(name):02d}"
    path = {
        "v": "voice/processed/{}.wav", "sfx": "sfx/{}.wav", "bgm": "bgm/{}.mp3",
        "end": "bgm/endcards/endcard_hum_{}.wav", "song": "songs/{}.mp3",
    }[kind].format(name)
    path = os.path.join(A, path)
    if path.endswith(".mp3"):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    else:
        x, sr = sf.read(path)
        assert sr == SR, (path, sr)
        x = to_stereo(x.astype(np.float64))
    _cache[src] = x
    return x


def cue(buf, at, src, gain=1.0, dur=None, fin=0.0, fout=0.0, pan=0.0):
    x = load(src)
    if dur is not None:
        n = int(dur * SR)
        if len(x) < n:  # loop
            reps = int(np.ceil(n / len(x)))
            x = np.concatenate([x] * reps)
        x = x[:n]
    x = x.copy() * gain
    if pan:
        x[:, 0] *= min(1, 1 - pan); x[:, 1] *= min(1, 1 + pan)
    if fin:
        k = min(len(x), int(fin * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fout:
        k = min(len(x), int(fout * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    i = int(at * SR)
    n = min(len(x), len(buf) - i)
    if n > 0:
        buf[i:i + n] += x[:n]


def chimes(start, end, count, src="sfx:chime_tower_bell_distant", gain=0.7, last_close=False):
    step = (end - start) / max(1, count - 1)
    out = []
    for k in range(count):
        s = src
        if last_close and k == count - 1:
            s = "sfx:chime_tower_bell"
        out.append((start + k * step, s, gain, {}))
    return out


def endcard(n):
    return [(85.0, "sfx:chime_tower_bell", 0.65, {"dur": 5.0, "fout": 1.0}),
            (85.6, f"end:{n}", 0.8, {"dur": 4.4, "fout": 0.8})]


TITLE = lambda t=8.0: (t, "bgm:M01_main_theme_sting", 0.45, {})
BGM = 0.32  # music bed gain under dialogue

EP = {}
EP[1] = [
    (0.0, "sfx:night_ambience_wind_crickets_loop", 0.5, {"dur": 20.3, "fout": 0.3}),
    (0.0, "sfx:tick_tock_60bpm_loop", 0.55, {"dur": 56.0}),
    (4.0, "sfx:clunk_gear_engage", 0.8, {}),
    TITLE(),
    (12.0, "v:e01_meera_01", 1.0, {}),
    (20.0, "bgm:M02_dread_drone_loop", BGM, {"dur": 55.0, "fin": 2.0, "fout": 1.0}),
    *chimes(24.0, 51.8, 10, gain=0.75, last_close=True),
    (27.5, "v:e01_meera_02", 1.0, {}),
    (38.3, "v:e01_meera_03", 1.0, {}),
    (41.2, "v:e01_mom_01", 0.9, {}),
    (45.2, "v:e01_meera_04", 1.0, {}),
    (52.4, "v:e01_meera_05", 1.0, {}),
    (70.5, "v:e01_meera_06", 1.0, {}),
    (75.0, "sfx:violin_screech_stinger", 0.7, {}),
    (82.0, "v:e01_keeper_01", 1.0, {}),
    *endcard(10),
]
EP[2] = [
    *[(0.2 + k * 0.85, "sfx:chime_tower_bell_distant", 0.35, {"dur": 4.0, "fout": 2.0}) for k in range(9)],
    TITLE(),
    (13.0, "v:e02_arjun_01", 1.0, {}),
    (18.0, "v:e02_meera_01", 1.0, {}),
    (22.0, "v:e02_arjun_02", 1.0, {}),
    (24.0, "v:e02_meera_02", 1.0, {}),
    (31.0, "v:e02_teacher_01", 0.9, {}),
    (37.0, "bgm:M02_dread_drone_loop", BGM, {"dur": 30.0, "fin": 2.0, "fout": 2.0}),
    (37.0, "sfx:tick_tock_60bpm_loop", 0.3, {"dur": 9.0, "fout": 1.0}),
    (46.0, "v:e02_arjun_03", 1.0, {}),
    (56.0, "sfx:glass_creak", 0.6, {}),
    (62.0, "v:e02_meera_03", 1.0, {}),
    (64.2, "v:e02_arjun_04", 1.0, {}),
    *[(68.0 + k, "sfx:tick" if k % 2 == 0 else "sfx:tock", 0.7, {}) for k in range(7)],
    (75.0, "sfx:chime_tower_bell", 0.95, {"dur": 6.5, "fout": 1.0}),
    (82.0, "sfx:corridor_lights_clunk_x5", 0.8, {}),
    *endcard(9),
]
EP[3] = [
    (0.0, "sfx:water_drip_loop", 0.5, {"dur": 22.0, "fout": 2.0}),
    (0.0, "sfx:tick_tock_60bpm_loop", 0.3, {"dur": 54.0}),
    TITLE(),
    (12.0, "v:e03_meera_01", 1.0, {}),
    (20.0, "bgm:M03_neha_theme", BGM, {"fin": 3.0}),
    (26.0, "sfx:glass_creak", 0.5, {}),
    (40.0, "sfx:vhs_glitch_stutter", 0.45, {}),
    (42.5, "v:e03_meera_02", 1.0, {}),
    (46.8, "sfx:vhs_glitch_dropout", 0.3, {}),
    (47.0, "v:e03_neha_01", 1.0, {}),
    *chimes(54.0, 77.8, 8, gain=0.6),
    (58.0, "v:e03_neha_02", 1.0, {}),
    (61.0, "bgm:M02_dread_drone_loop", BGM, {"dur": 16.0, "fin": 1.0, "fout": 0.5}),
    (63.5, "v:e03_meera_03", 1.0, {}),
    (71.5, "v:e03_neha_03", 1.0, {}),
    (77.0, "sfx:keeper_footsteps_ticking", 0.8, {"dur": 6.0}),
    (83.0, "sfx:lights_snap_off", 0.9, {}),
    *endcard(8),
]
EP[4] = [
    (0.0, "bgm:M06_sepia_memories", 0.4, {"dur": 8.0, "fout": 1.5}),
    TITLE(),
    (12.0, "sfx:night_ambience_wind_crickets_loop", 0.3, {"dur": 16.0, "fout": 2.0}),
    (12.0, "sfx:rocking_chair_creak", 0.4, {"dur": 5.5}),
    (12.5, "v:e04_meera_01", 1.0, {}),
    (17.5, "v:e04_ammachi_01", 1.0, {}),
    (28.0, "bgm:M06_sepia_memories", 0.3, {"dur": 30.0, "fin": 1.0, "fout": 2.0}),
    (28.3, "v:e04_ammachi_02", 1.0, {}),
    (40.3, "v:e04_ammachi_03", 1.0, {}),
    (46.6, "v:e04_ammachi_04", 1.0, {}),
    (52.0, "sfx:impact_metal", 0.35, {}),
    (57.0, "v:e04_ammachi_05", 1.0, {}),
    (58.0, "bgm:M02_dread_drone_loop", 0.25, {"dur": 22.0, "fin": 2.0, "fout": 1.0}),
    (68.6, "v:e04_meera_02", 1.0, {}),
    (71.2, "v:e04_ammachi_06", 1.0, {}),
    (76.0, "sfx:tick_tock_60bpm_loop", 0.6, {"dur": 9.0}),
    (78.5, "v:e04_ammachi_07", 1.0, {}),
    *endcard(7),
]
EP[5] = [
    (0.0, "sfx:phone_rec_beep", 0.6, {}),
    (0.0, "sfx:night_ambience_wind_crickets_loop", 0.35, {"dur": 20.0}),
    (20.0, "sfx:night_ambience_crickets_stop_at_8s", 0.35, {"dur": 12.0}),
    (0.3, "v:e05_arjun_01", 1.0, {}),
    TITLE(10.2), (10.2, "sfx:vhs_glitch_crunchy", 0.3, {}),
    (14.0, "v:e05_meera_01", 1.0, {}),
    (17.0, "v:e05_arjun_02", 1.0, {}),
    (28.0, "sfx:chime_tower_bell_distant", 0.8, {}),
    (30.5, "v:e05_arjun_03", 1.0, {}),
    *[(t, "sfx:chime_tower_bell_distant", 0.8, {}) for t in (36.0, 41.0, 46.0, 50.5)],
    (45.0, "bgm:M04_keepers_approach", 0.4, {}),
    (47.5, "v:e05_arjun_04", 1.0, {}),
    (51.0, "v:e05_meera_02", 1.0, {}),
    (55.0, "sfx:chime_tower_bell", 1.0, {}),
    (62.0, "sfx:phone_drop_clatter", 0.8, {}),
    (68.0, "sfx:keeper_footsteps_ticking", 0.6, {"dur": 6.0}),
    (74.0, "sfx:impact_metal", 0.5, {}),
    (76.0, "sfx:tape_stop_down", 0.6, {}),
    (78.0, "sfx:vhs_glitch_dropout", 0.6, {}),
    *endcard(6),
]
EP[6] = [
    (0.0, "sfx:night_ambience_wind_crickets_loop", 0.4, {"dur": 19.0, "fout": 2.0}),
    (0.5, "sfx:rocking_chair_creak", 0.3, {}),
    TITLE(),
    (12.0, "v:e06_arjun_01", 1.0, {}),
    (19.0, "bgm:M05_clockwork_room_loop", 0.4, {"dur": 38.0, "fin": 1.0, "fout": 1.0}),
    (27.5, "v:e06_meera_01", 1.0, {}),
    (34.0, "v:e06_arjun_02", 1.0, {}),
    *[(41.0 + k * 0.4, "sfx:tick", 0.6, {}) for k in range(18)],
    *[(41.2 + k * 1.0, "sfx:tock", 0.6, {}) for k in range(8)],
    (50.5, "v:e06_meera_02", 1.0, {}),
    (54.0, "sfx:clocks_snap_into_sync", 0.8, {}),
    (60.0, "bgm:M04_keepers_approach", 0.4, {"dur": 18.0}),
    (68.0, "sfx:phone_drop_clatter", 0.7, {}),
    (75.0, "sfx:phone_ringtone", 0.6, {}),
    (79.2, "sfx:tick", 1.0, {}),
    *endcard(5),
]
EP[7] = [
    (1.5, "sfx:vhs_glitch_stutter", 0.5, {}), (4.0, "sfx:vhs_glitch_stutter", 0.5, {}),
    (6.5, "sfx:tape_stop_down", 0.5, {}),
    TITLE(),
    (12.0, "v:e07_meera_01", 1.0, {}),
    *[(t, "sfx:phone_message_ping", 0.4, {}) for t in (20.0, 22.0, 24.5)],
    (26.0, "sfx:vhs_glitch_crunchy", 0.3, {}),
    (28.0, "bgm:M02_dread_drone_loop", BGM, {"dur": 34.0, "fin": 2.0, "fout": 2.0}),
    (34.0, "sfx:tick_tock_60bpm_loop", 0.25, {"dur": 8.0, "fout": 1.0}),
    (42.0, "sfx:phone_ringtone", 0.5, {"dur": 2.0}),
    (44.0, "v:e07_meera_02", 1.0, {}),
    (46.5, "sfx:tick_tock_60bpm_loop", 0.35, {"dur": 3.0}),
    (49.0, "v:e07_meeravoice_03", 1.0, {}),
    (55.5, "sfx:phone_drop_clatter", 0.6, {}),
    (57.0, "v:e07_meera_04", 1.0, {}),
    *chimes(62.0, 69.5, 4, gain=0.7),
    (62.5, "end:4", 0.35, {"dur": 8.0, "fout": 2.0}),
    (77.0, "v:e07_reflection_05", 1.0, {}),
    *endcard(4),
]
EP[8] = [
    (0.0, "bgm:M07_run_cue", 0.5, {}),
    TITLE(),
    (15.0, "sfx:rocking_chair_creak", 0.6, {}), (20.0, "sfx:rocking_chair_creak", 0.5, {}),
    (19.0, "v:e08_meera_01", 1.0, {}),
    (23.0, "sfx:tick_tock_60bpm_loop", 0.25, {"dur": 29.0}),
    (29.0, "bgm:M03b_neha_theme_sad", BGM, {"fin": 2.0}),
    (37.5, "v:e08_mom_01", 1.0, {}),
    (44.5, "v:e08_meera_02", 1.0, {}),
    (48.2, "v:e08_mom_02", 1.0, {}),
    *[(52.0 + k, "sfx:tick", 0.6, {}) for k in range(6)],
    (58.5, "v:e08_ammachi_03", 1.0, {}),
    (67.5, "v:e08_meera_03", 1.0, {}),
    (72.0, "sfx:phone_vibrate", 0.6, {}),
    (77.0, "sfx:whisper_chorus_distant", 0.7, {"dur": 8.0, "fout": 1.5}),
    (77.5, "sfx:chime_tower_bell_distant", 0.6, {}),
    *endcard(3),
]
EP[9] = [
    (0.0, "sfx:night_ambience_wind_crickets_loop", 0.3, {"dur": 12.0, "fout": 2.0}),
    (1.0, "v:e09_arjun_01", 1.0, {}),
    (6.5, "sfx:chain_snap", 0.8, {}),
    TITLE(),
    (12.5, "v:e09_meera_01", 1.0, {}),
    (20.0, "bgm:M08_gear_room", 0.45, {"dur": 30.0, "fout": 4.0}),
    (30.0, "v:e09_meera_02", 1.0, {}),
    (37.0, "sfx:vhs_glitch_stutter", 0.4, {}),
    (37.5, "v:e09_neha_03", 1.0, {}),
    (44.0, "sfx:keeper_footsteps_ticking", 0.6, {}),
    (44.0, "bgm:M04_keepers_approach", 0.35, {"dur": 18.0}),
    (50.0, "sfx:gear_grind_loop", 0.6, {"dur": 8.0, "fout": 1.0}),
    (58.0, "v:e09_arjun_02", 1.0, {}),
    (63.0, "v:e09_arjun_03", 1.0, {}),
    (70.0, "v:e09_meera_04", 1.0, {}),
    (70.5, "sfx:chime_tower_bell", 0.9, {}),
    (75.0, "sfx:chime_tower_bell", 1.0, {"dur": 9.0, "fout": 1.5}),
    (85.0, "sfx:chime_tower_bell", 0.65, {"dur": 5.0, "fout": 1.0}),
    (85.6, "end:2", 0.8, {"dur": 2.0, "fout": 0.05}),  # hum cut short
]
EP[10] = [
    (0.0, "sfx:heartbeat_60bpm", 0.7, {}),
    (0.0, "sfx:tick_tock_60bpm_loop", 0.5, {"dur": 8.0}),
    TITLE(6.0),
    (10.0, "bgm:M09_final_confrontation", 0.45, {}),
    (18.0, "v:e10_meera_01", 1.0, {}),
    (26.0, "v:e10_keeper_01", 1.0, {}),
    (34.0, "sfx:bell_swing_up", 0.7, {}),
    (37.0, "sfx:gears_reverse_rewind", 0.5, {}),
    (52.5, "v:e10_elias_02", 1.0, {}),
    (64.0, "bgm:M10_resolution", 0.35, {"dur": 21.0, "fin": 2.0, "fout": 3.0}),
    (65.5, "v:e10_arjun_03", 1.0, {}),
    (72.0, "v:e10_ammachi_01", 1.0, {}),
    (78.0, "sfx:chime_tower_bell_distant", 0.6, {}),
    (79.5, "v:e10_keeper_04", 1.0, {}),
    *endcard(1),
]


def master(path_wav, buf):
    tmp = path_wav + ".raw.wav"
    sf.write(tmp, buf, SR, subtype="FLOAT")
    mp3 = path_wav[:-4] + ".mp3"
    # two-stage: loudness-normalize to -14 LUFS, true peak -1 dBTP
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=14",
                    "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "256k", mp3], check=True)
    os.remove(tmp)
    return mp3


if __name__ == "__main__":
    only = [int(a) for a in sys.argv[1:]] or list(EP)
    for ep in only:
        buf = np.zeros((int(DUR * SR), 2))
        for at, src, gain, opts in EP[ep]:
            cue(buf, at, src, gain, **opts)
        k = int(0.5 * SR); buf[-k:] *= np.linspace(1, 0, k)[:, None]
        mp3 = master(os.path.join(OUT, f"COUNTDOWN_ep{ep:02d}_soundtrack_ml.wav"), buf)
        print("wrote", os.path.relpath(mp3, A))
