"""Shared horror effects for COUNTDOWN Season 2 (applied to each composited frame before the grade).
EV = {
  'flash':   [(t0, frames, 'cu'|'far'), ...],   subliminal 1–3 frame flashes of the girl
  'glitch':  [(t0, dur), ...],                  RGB split + torn scanlines + green static
  'red':     [t0, ...],                         blood-red pulse
  'chroma':  [t0, ...],                         chromatic-aberration kick
  'flicker': [(t0, t1), ...],                   lights dropping out at random frames
  'heart':   [beat times],                      the frame's edges close in on every heartbeat
}"""
import math, os
import numpy as np, cv2

W, H = 1920, 1080
_rng_cache = {}
_yy, _xx = np.mgrid[0:H, 0:W]
EDGE = np.clip(((_xx - W / 2) / (W * .55)) ** 2 + ((_yy - H / 2) / (H * .55)) ** 2, 0, 1).astype(np.float32)[..., None]


def load_scares(plates_dir):
    out = {}
    for k, d in (("cu", "s2_clara_cu"), ("far", "s2_clara_far")):
        p = os.path.join(plates_dir, d, "t0_00.png")
        if os.path.exists(p): out[k] = cv2.imread(p).astype(np.float32) / 255
    return out


def hb(t):  # deterministic hash
    return (math.sin(t * 127.1 + 311.7) * 43758.5453) % 1


def heartbeats(t0, t1, bpm0, bpm1):
    """beat times from t0 to t1, tempo ramping bpm0 → bpm1 (two thumps per beat: lub-dub)"""
    out, t = [], t0
    while t < t1:
        bpm = bpm0 + (bpm1 - bpm0) * (t - t0) / max(t1 - t0, 1e-6)
        out += [t, t + .16]; t += 60 / bpm
    return out


def apply(fr, t, EV, scares, fps=24):
    f = int(round(t * fps))
    # heartbeat: edges darken on each thump
    hk = sum(math.exp(-(t - b) * 9) for b in EV.get('heart', []) if 0 <= t - b < .6)
    if hk > .01: fr = fr * (1 - .45 * min(hk, 1.2) * EDGE)
    # flicker
    for a, b in EV.get('flicker', []):
        if a <= t < b and hb(f * .37) > .72: fr = fr * (.25 + .3 * hb(f * .11))
    # red pulse
    rk = sum(math.exp(-(t - r) * 5) for r in EV.get('red', []) if 0 <= t - r < 1.2)
    if rk > .01:
        k = min(rk, 1) * .55
        red = fr.copy(); red[..., 0] *= .25; red[..., 1] *= .25; red[..., 2] = np.minimum(1, red[..., 2] * 1.25 + .08)
        fr = fr * (1 - k) + red * k
    # chromatic aberration
    ck = sum(math.exp(-(t - c) * 7) for c in EV.get('chroma', []) if 0 <= t - c < .8)
    if ck > .02:
        s = int(18 * min(ck, 1))
        fr = fr.copy(); fr[..., 2] = np.roll(fr[..., 2], s, 1); fr[..., 0] = np.roll(fr[..., 0], -s, 1)
    # glitch
    for a, d in EV.get('glitch', []):
        if a <= t < a + d:
            fr = fr.copy(); s = int(10 + 30 * hb(f))
            fr[..., 2] = np.roll(fr[..., 2], s, 1); fr[..., 0] = np.roll(fr[..., 0], -s // 2, 0)
            for i in range(7):
                y0 = int(hb(f * 3.1 + i) * H); hgt = int(8 + 60 * hb(f * 7.7 + i)); off = int((hb(f * 1.3 + i) - .5) * 260)
                fr[y0:y0 + hgt] = np.roll(fr[y0:y0 + hgt], off, 1)
            noise = (np.random.default_rng(f).random((H // 4, W // 4)) > .82).astype(np.float32)
            fr += cv2.resize(noise, (W, H), interpolation=cv2.INTER_NEAREST)[..., None] * np.array([.12, .2, .12], np.float32)
            fr[::3] *= .7
    # subliminal flash of the girl
    for a, n, which in EV.get('flash', []):
        if a <= t < a + n / fps and which in scares:
            img = scares[which]
            if hb(f) > .5: img = (1 - img * .9) * .7     # every other frame inverted (dimmed)
            z = 1.0 + .08 * hb(f * 2)
            M = np.float32([[z, 0, W / 2 * (1 - z) + (hb(f) - .5) * 40], [0, z, H / 2 * (1 - z)]])
            fr = cv2.warpAffine(img, M, (W, H)) * .9 + fr * .1
    return np.clip(fr, 0, 1.4)
