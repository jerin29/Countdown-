"""Render the COUNTDOWN score (BGM cues M1-M10) to audio/bgm/*.mp3. Key D minor, built on one lullaby."""
import os, sys
import numpy as np
import soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from dsp import *

OUT = os.path.join(os.path.dirname(__file__), "..", "bgm")
SFX = os.path.join(os.path.dirname(__file__), "..", "sfx")
os.makedirs(OUT, exist_ok=True)
P = lambda name: os.path.join(OUT, name)


def load_sfx(name):
    x, _ = sf.read(os.path.join(SFX, name))
    return to_stereo(x)


def shift(note, semis):
    return note_hz(note) * 2 ** (semis / 12)


# "Ten Little Chimes" in D minor, 3/4. (note, beats). None = rest.
MELODY = [
    ("D5", 1), ("F5", 1), ("A5", 1), ("G5", 1), ("F5", 1), ("E5", 1), ("D5", 3), ("A4", 3),
    ("D5", 1), ("F5", 1), ("A5", 1), ("Bb5", 1), ("A5", 1), ("G5", 1), ("A5", 3), (None, 3),
    ("F5", 1), ("E5", 1), ("D5", 1), ("C#5", 1), ("D5", 1), ("E5", 1), ("D5", 3), ("A4", 3),
    ("D5", 1), ("F5", 1), ("E5", 1), ("D5", 1), ("C#5", 1), ("E5", 1), ("D5", 6),
]
# One chord per bar (16 bars).
CHORDS = [["D3", "F3", "A3"], ["G2", "Bb3", "D4"], ["D3", "F3", "A3"], ["A2", "C#4", "E4"],
          ["D3", "F3", "A3"], ["Bb2", "D4", "F4"], ["A2", "C#4", "E4"], ["A2", "C#4", "E4"],
          ["D3", "F3", "A3"], ["A2", "C#4", "E4"], ["D3", "F3", "A3"], ["A2", "C#4", "E4"],
          ["D3", "F3", "A3"], ["A2", "C#4", "G4"], ["D3", "F3", "A3"], ["D3", "F3", "A3"]]
MAJOR = {"F": "F#", "C": "C#", "Bb": "B"}  # D minor -> D major for the resolution


def to_major(n):
    if n is None:
        return None
    pitch, octv = (n[:-1], n[-1])
    return MAJOR.get(pitch, pitch) + octv


def lullaby(bpm=60, semis=0, inst="musicbox", detune=0.0, accomp=True, major=False, bars=16, vel=0.8):
    beat = 60 / bpm
    total = bars * 3 * beat + 4
    buf = silence(total)
    tt = 0.0
    for note, beats in MELODY:
        if tt >= bars * 3 * beat:
            break
        if major:
            note = to_major(note)
        if note:
            f = shift(note, semis + (12 if inst == "musicbox" else 0))
            if inst == "musicbox":
                x = music_box_note(f, 3.0, detune_cents=rng.uniform(-detune, detune))
            else:
                x = piano_note(f, 3.0, vel)
            place(buf, x, tt + rng.uniform(0, 0.012), 0.9, rng.uniform(-0.15, 0.15))
        tt += beats * beat
    if accomp:
        for b in range(bars):
            ch = CHORDS[b]
            if major:
                ch = [to_major(c) for c in ch]
            t0 = b * 3 * beat
            if inst == "musicbox":
                place(buf, music_box_note(shift(ch[0], semis + 12), 3, rng.uniform(-detune, detune), 0.5), t0, 0.45, -0.3)
                place(buf, music_box_note(shift(ch[1], semis + 12), 2, rng.uniform(-detune, detune), 0.5), t0 + beat, 0.3, 0.3)
                place(buf, music_box_note(shift(ch[2], semis + 12), 2, rng.uniform(-detune, detune), 0.5), t0 + 2 * beat, 0.3, 0.3)
            else:  # waltz "oom-pah-pah"
                place(buf, piano_note(shift(ch[0], semis - 12), 2.5, 0.7), t0, 0.6, -0.2)
                for k in (1, 2):
                    for c in ch[1:]:
                        place(buf, piano_note(shift(c, semis), 1.0, 0.5), t0 + k * beat, 0.25, 0.2)
    return buf


def ticks_bed(dur, period=1.0, gain=0.5, start=0.0):
    b = silence(dur)
    s, k = start, 0
    while s < dur:
        place(b, tick(0.12, pitch=1.0 if k % 2 == 0 else 0.78), s, gain)
        s += period; k += 1
    return b


def hiss(dur, level=0.01):
    return to_stereo(highpass(noise(int(dur * SR)), 2500) * level)


# ---------------- M1 Main Theme Sting (4.5 s) ----------------
def m1():
    b = silence(6.0)
    place(b, load_sfx("reverse_cymbal_swell.wav")[-int(1.5 * SR):], 0.0, 0.5)
    for k, n in enumerate(["D6", "F6", "A6", "C#6"]):
        place(b, music_box_note(note_hz(n), 3.0, detune_cents=-18 if k == 3 else 0), 1.5 + k * 0.32, 0.8, (k - 1.5) * 0.2)
    place(b, load_sfx("chime_tower_bell.wav"), 1.5 + 3 * 0.32, 0.7)
    out = reverb(b, 3.0, 0.3)[: int(6.0 * SR)]
    return fade(out, 0.0, 1.0)


# ---------------- M2 Dread Drone (30 s loop) ----------------
def m2():
    d = 32.0
    b = to_stereo(string_pad(note_hz("D2"), d, voices=4, vib=0.05, attack=3, release=3, bright=900)) * 0.9
    b += to_stereo(string_pad(note_hz("A2"), d, voices=3, vib=0.05, attack=6, release=3, bright=700), 0.3) * 0.4
    t = t_axis(d)
    whine = np.sin(2 * np.pi * 3520 * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)) * 0.012
    b += to_stereo(whine, -0.4)
    b += to_stereo(lowpass(brown(len(t)), 80) * 0.25)
    b += ticks_bed(d, 1.0, 0.18)
    b += hiss(d, 0.006)
    b = reverb(b, 4.0, 0.35, damp=2500)[: len(t)]
    return loop_crossfade(b, 2.0)


# ---------------- M3 Neha's Theme (40 s) and sad variation ----------------
def m3(sad=False):
    bpm = 48 if sad else 58
    x = lullaby(bpm=bpm, semis=-2 if sad else 0, inst="musicbox", detune=35 if not sad else 25,
                bars=12 if not sad else 8)
    x = tape_wobble(x, 0.5, 4.0)
    x = bandpass(x, 250, 6500)
    n = len(x)
    x += to_stereo(crackle(n, 10, 0.25))
    if sad:
        x += to_stereo(string_pad(note_hz("C3"), n / SR, 3, 0.05, 4, 4, 900)) * 0.15
    x = reverb(x, 3.5, 0.4, damp=4500)[:n]
    return fade(x, 0.3, 3.0)


# ---------------- M4 Keeper's Approach (20 s) ----------------
def m4():
    d = 20.0
    b = silence(d)
    s = 0.0
    while s < 17.8:  # ticks accelerate from 1/s to ~9/s
        frac = s / 17.8
        place(b, tick(0.1, pitch=0.7 + 0.3 * frac), s, 0.4 + 0.5 * frac)
        s += 1.0 * (1 - frac) ** 1.6 + 0.11
    # rising string cluster
    clust = np.zeros(int(17.8 * SR)); t = t_axis(17.8)
    for n in ["D4", "Eb4", "E4", "F4", "Gb4", "G4"]:
        f = note_hz(n) * 2 ** (t / 17.8 * 5 / 12)
        ph = 2 * np.pi * np.cumsum(f) / SR
        clust += sum(np.sin(h * ph) / h for h in range(1, 8))
    clust = lowpass(clust, 3500) * (t / 17.8) ** 2.2 * 0.25
    place(b, clust, 0.0, 1.0)
    # brass stabs: dissonant low cluster with filter sweep
    for at, g in [(3.0, 0.5), (7.0, 0.6), (10.5, 0.7), (13.0, 0.8), (15.0, 0.9), (16.5, 1.0)]:
        st = sum(saw(note_hz(n), 1.2) for n in ["D2", "Eb2", "A2"])
        st = sweep_lowpass(st, 2500, 200) * env_exp(len(st), 0.35)
        place(b, st, at, g * 0.6)
    scrape = load_sfx("gear_grind_loop.wav")[: int(8 * SR)] * np.linspace(0, 1, int(8 * SR))[:, None]
    place(b, scrape, 9.8, 0.4)
    b = reverb(b, 2.5, 0.3, damp=3000)[: int(d * SR)]
    b[int(17.8 * SR):] = 0.0  # hard cut to silence
    b[int(17.78 * SR): int(17.8 * SR)] *= np.linspace(1, 0, int(0.02 * SR))[:, None]
    return b


# ---------------- M5 Clockwork Room (40 s loop) ----------------
def m5():
    d = 41.0
    b = load_sfx("clocks_many_out_of_sync_loop.wav")
    b = np.concatenate([b, b])[: int(d * SR)] * 0.45
    # prepared-piano ostinato in 5/8: inharmonic plucks
    pattern = ["D4", "F4", "E4", "A3", "C#4"]
    eighth = 0.24
    s, k = 0.5, 0
    while s < d - 2:
        n = pattern[k % 5]
        x = modal_hit([note_hz(n), note_hz(n) * 2.73, note_hz(n) * 4.11], [0.6, 0.25, 0.1], [1, 0.4, 0.2], 1.0, 0.002, 0.25)
        place(b, lowpass(x, 3500), s, 0.35 if k % 5 == 0 else 0.22, rng.uniform(-0.3, 0.3))
        s += eighth; k += 1
    b += to_stereo(string_pad(note_hz("D2"), d, 2, 0.04, 3, 3, 500)) * 0.25
    b = reverb(b, 2.0, 0.25)[: int(d * SR)]
    return loop_crossfade(b, 1.0)


# ---------------- M6 Sepia Memories (35 s) ----------------
def m6():
    x = lullaby(bpm=84, semis=-12, inst="piano", bars=16, vel=0.6)
    x = x[: int(36 * SR)]
    x = bandpass(x, 300, 3800)  # gramophone band
    x = tape_wobble(x, 0.8, 2.0)
    n = len(x)
    x += to_stereo(crackle(n, 14, 0.45))
    x = reverb(x, 1.5, 0.25, damp=3000)[:n]
    return fade(x, 0.5, 3.0)


# ---------------- M7 Run Cue (15 s) ----------------
def m7():
    d = 15.0
    b = silence(d)
    sixteenth = 60 / 140 / 4
    s, k = 0.0, 0
    while s < 14.0:
        n = "D2" if (k // 16) % 2 == 0 else "Eb2"
        x = saw(note_hz(n), sixteenth * 0.9) * adsr(int(sixteenth * 0.9 * SR), 0.003, 0.03, 0.6, 0.02)
        place(b, lowpass(x, 900 + 600 * (s / 14)), s, 0.5 if k % 4 == 0 else 0.3)
        place(b, lowpass(saw(note_hz(n) * 2, sixteenth * 0.9), 1200) * adsr(int(sixteenth * 0.9 * SR), 0.003, 0.03, 0.5, 0.02), s, 0.15, 0.3)
        s += sixteenth; k += 1
    hb = load_sfx("heartbeat_60bpm.wav")
    beat = 60 / 140
    s = 0.0
    while s < 14.0:
        place(b, hb[: int(0.3 * SR)], s, 0.9); s += beat
    place(b, choir([note_hz("D5"), note_hz("Eb5"), note_hz("A5")], 14.0, 'a', 6.0, 0.5, 0.5), 0.0, 0.35)
    place(b, load_sfx("impact_deep_boom.wav")[: int(1.0 * SR)], 14.0, 0.8)
    b = reverb(b, 1.8, 0.25)[: int(d * SR)]
    return fade(b, 0.0, 0.8)


# ---------------- M8 Gear Room (40 s) ----------------
def m8():
    d = 41.0
    b = load_sfx("gear_grind_loop.wav")
    b = np.concatenate([b, b, b, b])[: int(d * SR)] * 0.3
    beat = 60 / 80
    clunk = load_sfx("clunk_gear_engage.wav")[: int(1.2 * SR)]
    anvil = modal_hit([620, 1710, 2930, 4180], [0.6, 0.35, 0.2, 0.12], [1, 0.6, 0.4, 0.2], 1.5, 0.002, 0.5)
    s, k = 0.0, 0
    while s < d - 1:
        if k % 4 == 0:
            place(b, clunk, s, 0.7)
        if k % 4 == 2:
            place(b, anvil, s, 0.25, 0.3)
        place(b, tick(0.08, pitch=0.6), s + beat / 2, 0.3, -0.3)
        s += beat; k += 1
    prog = [["D4", "F4", "A4"], ["Bb3", "D4", "F4"], ["G3", "Bb3", "D4"], ["A3", "C#4", "E4"]]
    for i, ch in enumerate(prog * 2):
        place(b, choir([note_hz(n) for n in ch], 6.0, 'a', 1.5, 1.5, 0.1), 1.0 + i * 4.8, 0.45)
    b = reverb(b, 5.0, 0.4, damp=3500)[: int(d * SR)]
    return fade(b, 1.0, 3.0)


# ---------------- M9 Final Confrontation (55 s) ----------------
def m9():
    d = 56.0
    b = silence(d)
    # 0-20: drone + ticks accelerating + choir swelling
    place(b, m2()[: int(20 * SR)], 0.0, 0.8)
    s = 0.0
    while s < 20:
        place(b, tick(0.1), s, 0.5); s += max(0.25, 1.0 - s / 26)
    place(b, choir([note_hz(n) for n in ["D4", "F4", "A4", "D5"]], 22.0, 'o', 10, 1, 0.1), 0.0, 0.4)
    # 20-33: full - lullaby on music box over strings, choir, gears, bell on each bar
    lb = lullaby(bpm=72, semis=0, inst="musicbox", detune=10, bars=6)
    place(b, lb[: int(13 * SR)], 20.0, 0.9)
    for n, g in [("D3", 0.5), ("A3", 0.35), ("F4", 0.25)]:
        place(b, string_pad(note_hz(n), 13.5, 3, 0.08, 1.0, 1.0, 3000), 20.0, g)
    place(b, choir([note_hz(n) for n in ["D4", "F4", "A4", "D5"]], 13.5, 'a', 1.0, 0.5, 0.1), 20.0, 0.5)
    place(b, load_sfx("gear_grind_loop.wav")[: int(13 * SR)], 20.0, 0.35)
    for k in range(5):
        place(b, load_sfx("chime_tower_bell.wav"), 20.0 + k * 2.5, 0.35)
    # 33-45: everything rewinds (section 21-33 reversed)
    seg = b[int(21 * SR): int(33 * SR)][::-1].copy()
    seg = tape_wobble(seg, 0.3, 6.0)
    place(b, seg, 33.0, 0.9)
    place(b, load_sfx("gears_reverse_rewind.wav"), 33.0, 0.5)
    place(b, load_sfx("reverse_bell_swell.wav"), 41.0, 0.8)
    # 45-55: resolution to D major
    place(b, lullaby(bpm=60, inst="musicbox", major=True, bars=3, detune=0), 45.0, 0.7)
    for n, g in [("D3", 0.4), ("F#3", 0.3), ("A3", 0.3), ("D4", 0.2)]:
        place(b, string_pad(note_hz(n), 10.5, 3, 0.05, 1.5, 4.0, 2500), 45.0, g)
    out = reverb(b, 3.5, 0.3)[: int(d * SR)]
    return fade(out, 0.5, 3.0)


# ---------------- M10 Resolution, D major (30 s) ----------------
def m10():
    x = lullaby(bpm=72, semis=0, inst="musicbox", major=True, bars=12, detune=0)
    pia = lullaby(bpm=72, semis=-12, inst="piano", major=True, bars=12, vel=0.5)
    n = int(31 * SR)
    x = x[:n] * 0.6 + pia[:n] * 0.5
    for nn, g in [("D3", 0.25), ("A3", 0.2), ("F#4", 0.15)]:
        x += to_stereo(string_pad(note_hz(nn), n / SR, 3, 0.05, 3, 4, 2500)) * g
    x = reverb(x, 3.0, 0.3)[:n]
    return fade(x, 1.0, 4.0)


CUES = {
    "M01_main_theme_sting.mp3": m1,
    "M02_dread_drone_loop.mp3": m2,
    "M03_neha_theme.mp3": lambda: m3(False),
    "M03b_neha_theme_sad.mp3": lambda: m3(True),
    "M04_keepers_approach.mp3": m4,
    "M05_clockwork_room_loop.mp3": m5,
    "M06_sepia_memories.mp3": m6,
    "M07_run_cue.mp3": m7,
    "M08_gear_room.mp3": m8,
    "M09_final_confrontation.mp3": m9,
    "M10_resolution.mp3": m10,
}
only = sys.argv[1:]
for name, fn in CUES.items():
    if only and not any(o in name for o in only):
        continue
    x = fn()
    write(P(name), x, -1.0, mp3=True)
    print(f"{name}: {len(x) / SR:.1f}s")
