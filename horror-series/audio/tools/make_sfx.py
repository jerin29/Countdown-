"""Render the COUNTDOWN sound-effects library to audio/sfx/*.wav."""
import os, sys, subprocess, glob
import numpy as np
import soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from dsp import *

OUT = os.path.join(os.path.dirname(__file__), "..", "sfx")
os.makedirs(OUT, exist_ok=True)
P = lambda name: os.path.join(OUT, name)

# 1. THE CHIME: one deep, slightly out-of-tune tower bell (the brand sound). Dry + distant versions.
bell = tower_bell(fund=98.0, dur=9.0)
write(P("chime_tower_bell.wav"), reverb(bell, 3.5, 0.35, damp=3500), -1)
far = lowpass(bell, 2200)
write(P("chime_tower_bell_distant.wav"), reverb(far, 5.0, 0.6, damp=2000, predelay=0.08), -1)

# 2. Ticks: tick, tock (lower), and a 60-bpm tick-tock bed (30 s, loops cleanly on the beat).
write(P("tick.wav"), reverb(tick(0.15), 0.4, 0.15), -3)
write(P("tock.wav"), reverb(tick(0.15, bright=0.6, pitch=0.78), 0.4, 0.15), -3)
bed = silence(30.0)
for s in range(30):
    place(bed, tick(0.15, pitch=1.0 if s % 2 == 0 else 0.78, bright=1.0 if s % 2 == 0 else 0.6), s)
write(P("tick_tock_60bpm_loop.wav"), reverb(bed, 0.5, 0.15)[: len(bed)], -6)

# 3. Wall of clocks (Ep6): 40 clocks at slightly different rates, panned around the room.
wall = silence(30.0)
for c in range(40):
    period = rng.uniform(0.45, 1.25)
    start = rng.uniform(0, period)
    pitch = rng.uniform(0.6, 1.5)
    pan = rng.uniform(-0.9, 0.9)
    g = rng.uniform(0.15, 0.6)
    tt = start
    while tt < 30:
        place(wall, tick(0.1, pitch=pitch, bright=rng.uniform(0.3, 1.0)), tt, g, pan)
        tt += period
write(P("clocks_many_out_of_sync_loop.wav"), reverb(wall, 1.2, 0.25)[: len(wall)], -3)

# Clocks all snapping into sync (Ep6 0:57): out of sync for 3 s, then all together, loud.
sync = silence(10.0)
for c in range(40):
    period = rng.uniform(0.5, 1.2); tt = rng.uniform(0, period); pan = rng.uniform(-0.9, 0.9)
    while tt < 3.0:
        place(sync, tick(0.1, pitch=rng.uniform(0.6, 1.5)), tt, 0.3, pan); tt += period
for s in np.arange(3.0, 10.0, 0.5):
    for c in range(12):
        place(sync, tick(0.12, pitch=rng.uniform(0.6, 1.4)), s + rng.uniform(0, 0.004), 0.35, rng.uniform(-1, 1))
write(P("clocks_snap_into_sync.wav"), reverb(sync, 1.0, 0.2)[: len(sync)], -1)

# 4. Clunk: a heavy gear engaging (something wakes up).
cl = modal_hit([55, 131, 247, 389, 612], [0.9, 0.5, 0.3, 0.18, 0.1], [1, 0.7, 0.5, 0.35, 0.2], 3.0, 0.01, 1.2)
cl = lowpass(cl, 3000)
write(P("clunk_gear_engage.wav"), reverb(cl, 2.5, 0.35, damp=2500), -1)

# 5. Gear grind loop (Ep9-10): ratchet clicks + scraping metal + low rumble, 12 s.
n = int(12 * SR)
t = np.arange(n) / SR
grind = brown(n) * 0.6
scrape = bandpass(noise(n), 1800, 4200) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 0.37 * t))) ** 3
for f in (2310, 3180, 4470):
    scrape += resonator(noise(n) * 0.05, f, 60) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.1, 0.3) * t))
g = to_stereo(grind * 0.7 + scrape * 0.5)
tt = 0.0
while tt < 12:
    place(g, modal_hit([1900, 3100], [0.02, 0.012], [1, 0.6], 0.08, 0.001, 0.8) * 0.5, tt, 1.0, rng.uniform(-0.5, 0.5))
    tt += 0.18 + rng.uniform(-0.01, 0.01)
write(P("gear_grind_loop.wav"), loop_crossfade(reverb(g, 2.0, 0.3, damp=3000)[:n], 1.0), -2)

# Gears reversing (Ep10 time rewinds): grind pitched up and reversed with a rising swell.
rev = g[::-1].copy()
rev *= np.linspace(0.2, 1.0, len(rev))[:, None]
write(P("gears_reverse_rewind.wav"), reverb(rev, 2.0, 0.35)[: len(rev)], -1)

# 6. Keeper footstep: a slow heavy tick + metal creak, 4 steps.
steps = silence(6.0)
for i, s in enumerate([0.2, 1.6, 3.0, 4.4]):
    place(steps, tick(0.2, pitch=0.5, bright=0.8) * 2.0, s)
    creak = resonator(noise(int(0.5 * SR)) * 0.2, 310 + 40 * i, 40) * np.hanning(int(0.5 * SR))
    place(steps, creak, s + 0.05, 0.4)
    place(steps, lowpass(noise(int(0.3 * SR)), 180) * np.exp(-np.arange(int(0.3 * SR)) / (0.05 * SR)), s, 0.6)
write(P("keeper_footsteps_ticking.wav"), reverb(steps, 2.5, 0.4, damp=2500)[: len(steps)], -2)

# 7. Rocking chair creak (Ep8): stick-slip friction pulses through wood resonances, 2 rocks.
def creak(dur, f0=55, f1=95):
    nn = int(dur * SR)
    rate = np.linspace(f0, f1, nn) * (1 + 0.15 * np.sin(np.linspace(0, 9, nn)))
    ph = np.cumsum(rate) / SR
    pulses = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
    pulses *= rng.uniform(0.5, 1, nn)
    w = sum(resonator(pulses, f, 25) * a for f, a in [(420, 1), (760, 0.6), (1350, 0.35), (2600, 0.15)])
    return w * np.hanning(nn)
rock = silence(5.0)
place(rock, creak(1.1), 0.1); place(rock, creak(1.0, 70, 50), 2.4, 0.8)
write(P("rocking_chair_creak.wav"), reverb(rock, 0.8, 0.2)[: len(rock)], -3)

# 8. Water drip (Ep3): a drop into a basin.
def drip():
    d = 0.4; tt = t_axis(d)
    f = 900 * (1 + 1.2 * (1 - np.exp(-tt / 0.02)))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.05) * 0.6 + \
        highpass(noise(len(tt)), 2000) * np.exp(-tt / 0.002) * 0.2
dr = silence(8.0)
for s in np.arange(0.2, 8, 1.0):
    place(dr, drip(), s + rng.uniform(-0.02, 0.02), rng.uniform(0.7, 1.0))
write(P("water_drip_loop.wav"), reverb(dr, 1.0, 0.35)[: len(dr)], -3)

# 9. Heartbeat (Ep10 cold open): lub-dub at 60 bpm, 8 s.
def thump(f=50, d=0.25):
    tt = t_axis(d)
    return np.sin(2 * np.pi * f * tt * (1 - 0.3 * tt / d)) * np.exp(-tt / 0.06)
hb = silence(8.0)
for s in range(8):
    place(hb, thump(), s + 0.05); place(hb, thump(42), s + 0.33, 0.6)
write(P("heartbeat_60bpm.wav"), lowpass(hb, 400), -2)

# 10. Violin screech stinger: detuned high string cluster sliding up with fast tremolo, then cut.
d = 2.2; tt = t_axis(d)
scr = np.zeros(len(tt))
for k in range(6):
    f0 = note_hz('E6') * 2 ** (rng.uniform(-1, 1) / 12)
    f = f0 * 2 ** (tt * 0.9 / 12 * rng.uniform(0.5, 2))
    ph = 2 * np.pi * np.cumsum(f) / SR
    scr += sum(np.sin(h * ph) / h for h in range(1, 6))
scr *= (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * tt))) * np.minimum(1, tt / 0.04)
scr = bandpass(scr, 900, 9000) + bandpass(noise(len(tt)), 3000, 8000) * 0.4
scr[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
write(P("violin_screech_stinger.wav"), scr, -1)

# 11. Reverse swell / whoosh into a hit (time rewinding, title cards).
rw = reverb(bell * 0.8, 4.0, 0.8, damp=4000)[::-1]
rw = rw[-int(4.0 * SR):]
write(P("reverse_bell_swell.wav"), fade(rw, 0.5, 0.01), -1)
nn = int(3 * SR); tt = np.arange(nn) / SR
cym = highpass(noise(nn), 4000) * np.exp(-(3 - tt) / 0.6)
write(P("reverse_cymbal_swell.wav"), to_stereo(fade(cym, 0.1, 0.005)), -2)

# 12. Light snap-off (Ep3 lights go out): click + mains hum dying.
d = 1.5; tt = t_axis(d)
hum = (np.sin(2 * np.pi * 50 * tt) + 0.5 * np.sin(2 * np.pi * 150 * tt)) * np.exp(-tt / 0.2) * 0.4
snap = highpass(noise(len(tt)), 2000) * np.exp(-tt / 0.004)
write(P("lights_snap_off.wav"), reverb(hum + snap, 0.6, 0.2)[: len(tt)], -2)

# Corridor lights going off one by one (Ep2): five heavy relays approaching.
cor = silence(4.5)
for i in range(5):
    place(cor, lowpass(modal_hit([90, 180, 410], [0.25, 0.15, 0.08], [1, 0.6, 0.3], 0.8, 0.004, 0.8), 1500),
          0.2 + i * 0.75, 0.4 + i * 0.15)
write(P("corridor_lights_clunk_x5.wav"), reverb(cor, 2.0, 0.35)[: len(cor)], -1)

# 13. Night ambience loop: wind + crickets (crickets stop when the Keeper is near: use the cut version).
nn = int(40 * SR); tt = np.arange(nn) / SR
wind = bandpass(pink(nn), 150, 1200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt + 1) * np.sin(2 * np.pi * 0.13 * tt))
amb = to_stereo(wind * 0.5)
for c in range(5):
    fc = rng.uniform(4200, 5200); pan = rng.uniform(-0.8, 0.8); g = rng.uniform(0.04, 0.1)
    chirp_rate = rng.uniform(2.2, 3.5); s = rng.uniform(0, 1)
    while s < 40:
        L = int(0.12 * SR)
        ch = np.sin(2 * np.pi * fc * np.arange(L) / SR) * (np.sin(2 * np.pi * 45 * np.arange(L) / SR) > 0) * np.hanning(L)
        place(amb, ch, s, g, pan); s += 1 / chirp_rate * rng.uniform(0.9, 1.1)
write(P("night_ambience_wind_crickets_loop.wav"), loop_crossfade(amb, 2.0), -6)
cut = amb[: int(12 * SR)].copy()
cut[int(8 * SR):] = to_stereo(wind[int(8 * SR): int(12 * SR)] * 0.5)  # crickets stop dead at 8 s
write(P("night_ambience_crickets_stop_at_8s.wav"), cut, -6)

# 14. Phone sounds (Ep5-7): REC beep, ringtone, message ping, vibration.
d = 0.25; tt = t_axis(d)
write(P("phone_rec_beep.wav"), np.sin(2 * np.pi * 1760 * tt) * adsr(len(tt), 0.005, 0.02, 0.8, 0.05), -6)
ring = silence(4.0)
for s in (0.0, 2.0):
    for k, f in enumerate([1318.5, 1568, 1975.5, 1568]):
        tt = t_axis(0.18)
        place(ring, np.sin(2 * np.pi * f * tt) * adsr(len(tt), 0.005, 0.05, 0.6, 0.06) * 0.5, s + k * 0.2)
write(P("phone_ringtone.wav"), ring, -4)
tt = t_axis(0.5)
write(P("phone_message_ping.wav"), (np.sin(2 * np.pi * 1568 * tt) + 0.4 * np.sin(2 * np.pi * 3136 * tt)) * np.exp(-tt / 0.12), -6)
vb = silence(1.6)
for s in (0.0, 0.8):
    tt = t_axis(0.45)
    place(vb, lowpass(np.sign(np.sin(2 * np.pi * 160 * tt)) * 0.3 + noise(len(tt)) * 0.1, 900) * adsr(len(tt), 0.01, 0.05, 0.9, 0.05), s)
write(P("phone_vibrate.wav"), vb, -4)
tt = t_axis(0.35)
write(P("phone_drop_clatter.wav"), reverb(modal_hit([1200, 2650, 4100, 830], [0.04, 0.03, 0.02, 0.06], [1, 0.7, 0.4, 0.5], 0.35, 0.003, 1.0), 0.5, 0.15)[: len(tt)], -1)

# 15. Chain snap (Ep9).
cs = silence(2.0)
place(cs, modal_hit([2100, 3400, 5200, 1450], [0.15, 0.1, 0.06, 0.2], [1, 0.7, 0.5, 0.6], 1.2, 0.002, 1.5), 0.05)
for k in range(9):
    place(cs, modal_hit([rng.uniform(1800, 4000)], [0.05], [0.6], 0.15, 0.001, 0.6), 0.15 + k * 0.07 + rng.uniform(0, 0.03), 0.5)
write(P("chain_snap.wav"), reverb(cs, 1.2, 0.25)[: len(cs)], -1)

# 16. Glass creak (Ep2 photo): slow stressed-glass groan.
d = 1.8; tt = t_axis(d)
gc = sum(resonator(noise(len(tt)) * 0.03, f * (1 + 0.02 * np.sin(tt[0])), 80) for f in (1720, 2480, 3900))
gc *= np.hanning(len(tt)) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * tt) ** 2)
write(P("glass_creak.wav"), reverb(gc, 0.8, 0.25)[: len(tt)], -3)

# 17. Bell swing up (Ep10 0:34): the bell's slow upswing - creaking bearing + rope stretch.
sw = silence(3.0)
place(sw, creak(2.6, 25, 40) * 1.2, 0.1)
place(sw, lowpass(brown(int(2.8 * SR)), 200) * np.hanning(int(2.8 * SR)) * 0.5, 0.0)
write(P("bell_swing_up.wav"), reverb(sw, 3.0, 0.35, damp=2500)[: len(sw)], -2)

# 18. Distant whisper chorus (Ep8 stinger), built from the cast's own Malayalam lines, reversed and smeared.
vdir = os.path.join(os.path.dirname(__file__), "..", "voice", "processed")
lines = sorted(glob.glob(os.path.join(vdir, "*.wav")))
if lines:
    wc = silence(10.0)
    for k in range(18):
        v, sr_ = sf.read(lines[rng.integers(0, len(lines))])
        v = v[::-1] if k % 2 == 0 else v
        v = bandpass(v, 1500, 6000)
        place(wc, v, rng.uniform(0, 7.5), rng.uniform(0.15, 0.4), rng.uniform(-0.9, 0.9))
    wc = reverb(wc, 4.0, 0.75, damp=5000)[: len(wc)]
    write(P("whisper_chorus_distant.wav"), fade(wc, 1.5, 2.0), -3)

# 19. Bank sounds (earshot's computed bank): VHS glitches, impacts.
bank = {"vhs_glitch_stutter.wav": "glitch/stutter", "vhs_glitch_crunchy.wav": "pro_glitch/crunchy",
        "vhs_glitch_dropout.wav": "glitch/dropout", "impact_deep_boom.wav": "impact/deep",
        "impact_metal.wav": "impact/metal", "tape_stop_down.wav": "downlifter/tape",
        "sub_hit.wav": "cut_hit/sub"}
earshot = os.path.expanduser("~/.local/bin/earshot")
for fn, sid in bank.items():
    subprocess.run([earshot, "sfx", "render", sid, "-o", P(fn)], check=True, stdout=subprocess.DEVNULL)

print("\n".join(sorted(os.listdir(OUT))))
