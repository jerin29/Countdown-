"""COUNTDOWN S2 Ep 1 compositor: one continuous take from painted plates (Cinemagic-style smooth camera).
Plates come from animation-base/src/s2/ep01.js (rendered as 1920x1080 tiles). Usage:
  python3 ep01.py PLATES_DIR [--lang ml] [--from 0 --to 90] [--sheet 1,5,...]   (sheet = check frames, no video)
"""
import os, sys, json, math, subprocess, argparse
import numpy as np, cv2
import horrorfx as HFX

W, H, FPS, DUR = 1920, 1080, 24, 90.0
HERE = os.path.dirname(os.path.abspath(__file__))
S2 = os.path.dirname(os.path.dirname(HERE))
CHIMES = [36 + 28.5 * (1 - (1 - i / 39) ** 1.6) for i in range(40)]
T_X, T_C, T_CARD, T_CRED = 33.0, 70.0, 80.0, 85.0
WIN = dict(x=1180, y=170, w=520, h=470); WC = (WIN['x'] + WIN['w'] / 2, WIN['y'] + WIN['h'] / 2)
HW = dict(x=5220, y=1150, w=400, h=225); HWC = (HW['x'] + HW['w'] / 2, HW['y'] + HW['h'] / 2); SC = HW['w'] / W
EA, SE = (2600, 1150), .32
INK = (0x20, 0x18, 0x1C)                  # BGR of CP.ink
SICK = np.array([0x8A, 0xD4, 0x9F], np.float32) / 255   # BGR of the sick glow

clamp = lambda x, a=0., b=1.: max(a, min(b, x))
ease = lambda x: (lambda y: y * y * (3 - 2 * y))(clamp(x))
ease_in = lambda x: clamp(x) ** 3
seg = lambda t, a, b: clamp((t - a) / (b - a))
lerp = lambda a, b, k: a + (b - a) * k


def kf(t, keys, e=ease):
    if t <= keys[0][0]: return keys[0][1]
    for i in range(1, len(keys)):
        if t < keys[i][0]:
            (a, va), (b, vb) = keys[i - 1], keys[i]
            k = e((t - a) / (b - a)); return tuple(lerp(x, y, k) for x, y in zip(va, vb))
    return keys[-1][1]


ROOM_KEYS = [(0, (760, 300, 4.2)), (8, (760, 300, 4.2)), (14, (960, 540, 1.05)), (17.5, (360, 590, 2.1)), (21.5, (330, 585, 2.2)),
             (25.5, (560, 520, 1.3)), (30.0, (1300, 450, 1.6)), (T_X, (WC[0], WC[1], 4.8))]
room_cam = lambda t: kf(t, ROOM_KEYS)
def ex_origin(c): return (WC[0] - (c[0] - WC[0]) * .18, WC[1] - (c[1] - WC[1]) * .12)
def ex_from_room(t):
    c = room_cam(t); O = ex_origin(c); return (EA[0] + (c[0] - O[0]) / SE, EA[1] + (c[1] - O[1]) / SE, c[2] * SE)
EX_KEYS = [(T_X, ex_from_room(T_X)), (38, (3150, 1080, 1.05)), (46, (4150, 1010, .82)), (54, (4880, 1150, .95)),
           (60, (HWC[0] - 40, HWC[1] + 10, 1.9)), (66, (HWC[0], HWC[1], 3.0)), (T_C, (HWC[0], HWC[1], H / HW['h'] * 1.02))]
ex_cam = lambda t: kf(t, EX_KEYS)
close_from_ex = lambda e: ((e[0] - HW['x']) / SC, (e[1] - HW['y']) / SC, e[2] * SC)
SCARES = {}
EYE = (804, 528)
CLOSE_KEYS = [(T_C, close_from_ex(ex_cam(T_C))), (76, (900, 505, 1.45)), (78.4, (860, 520, 2.3)), (T_CARD, (EYE[0], EYE[1], 5.0))]
close_cam = lambda t: kf(t, CLOSE_KEYS, ease_in)

# ---- horror effects (times in seconds) ----
EV = {
    'flash': [(2.12, 2, 'cu'), (27.4, 2, 'far'), (50.3, 2, 'far'), (64.62, 3, 'cu'), (75.2, 2, 'cu'), (79.45, 3, 'cu')],
    'glitch': [(2.05, .25), (18.0, .3), (27.3, .35), (32.9, .45), (50.2, .3), (64.5, .45), (70.9, .5), (78.38, .6), (80.0, .3)],
    'red': [2.05, 64.5, 78.4, 80.35],
    'chroma': [2.05, 33.0, 71.0, 78.4],
    'flicker': [(19.0, 22.6), (68.0, 71.0)],
    'heart': HFX.heartbeats(12, 19.2, 62, 118) + HFX.heartbeats(36.5, 64.4, 84, 112) + HFX.heartbeats(70.5, 79.2, 120, 150),
}


def chime_k(t, k=4.0): return sum(math.exp(-(t - c) * k) for c in CHIMES if t >= c)


# ---------------- plates ----------------
class Plate:
    """a stitched plate: image (BGR float32 0..1), world origin (x0, y0), pixels per world unit z, optional alpha"""
    def __init__(self, img, x0, y0, z, alpha=None):
        self.img, self.x0, self.y0, self.z, self.alpha = img, x0, y0, z, alpha
        self.cache = {}

    def level(self, s):
        """a pre-shrunk copy when the plate is drawn small (avoids aliasing)"""
        f = 1
        while s * f * 2 <= .55 and f < 8: f *= 2
        if f == 1: return self.img, self.alpha, 1
        if f not in self.cache:
            sm = cv2.resize(self.img, None, fx=1 / f, fy=1 / f, interpolation=cv2.INTER_AREA)
            sa = None if self.alpha is None else cv2.resize(self.alpha, None, fx=1 / f, fy=1 / f, interpolation=cv2.INTER_AREA)
            self.cache[f] = (sm, sa)
        return (*self.cache[f], f)

    def view(self, cx, cy, zoom):
        """render the plate through a camera (world point (cx, cy) at screen centre). returns (rgb, alpha) for the screen"""
        s = zoom / self.z
        img, al, f = self.level(s)
        s2 = s * f
        M = np.float32([[s2, 0, (self.x0 - cx) * zoom + W / 2], [0, s2, (self.y0 - cy) * zoom + H / 2]])
        rgb = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        ones = al if al is not None else np.ones(img.shape[:2], np.float32)
        a = cv2.warpAffine(ones, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        return rgb, a


def stitch(d, nx, ny):
    rows = []
    for r in range(ny):
        rows.append(np.concatenate([cv2.imread(os.path.join(d, f"t{(r * nx + c) / 10:.2f}".replace('.', '_') + ".png")) for c in range(nx)], 1))
    return np.concatenate(rows, 0).astype(np.float32) / 255


def green_alpha(img):
    g = (img[..., 1] > .8) & (img[..., 0] < .3) & (img[..., 2] < .3)
    a = (~g).astype(np.float32)
    return cv2.GaussianBlur(cv2.erode(a, np.ones((3, 3), np.uint8)), (3, 3), 0)


def load_plates(P):
    pl = {}
    for v in ("sleep", "awake", "sit"):
        im = stitch(os.path.join(P, f"e1_room_{v}"), 3, 3); pl["room_" + v] = Plate(im, -200, -100, 2, green_alpha(im))
    im = stitch(os.path.join(P, "e1_clock"), 1, 1); pl["clock"] = Plate(im, 520, 165, 4, green_alpha(im))
    pl["city"] = Plate(stitch(os.path.join(P, "e1_city"), 3, 2), 1400, 250, 1)
    pl["cityglow"] = Plate(stitch(os.path.join(P, "e1_cityglow"), 3, 2), 1400, 250, 1)
    im = stitch(os.path.join(P, "e1_facade"), 3, 3)
    a = green_alpha(im)
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
    wx, wy = xx / 2 + 4100, yy / 2 + 700
    a *= ((wx >= HW['x'] - 1100) & (wx <= HW['x'] + HW['w'] + 1100)).astype(np.float32)   # the building's own walls only
    pl["facade"] = Plate(im, 4100, 700, 2, a)
    for v in "abcd": pl["win_" + v] = Plate(stitch(os.path.join(P, f"e1_win_{v}"), 2, 2), 0, 0, 2)
    for n in ("warn", "count", "credits"):
        d = os.path.join(P, "e1_" + n)
        pl[n] = [cv2.imread(os.path.join(d, f)).astype(np.float32) / 255 for f in sorted(os.listdir(d))]
    return pl


# ---------------- effects ----------------
rng = np.random.default_rng(7)
FOG = cv2.GaussianBlur(rng.random((540, 1920 * 2)).astype(np.float32), (0, 0), 40)
FOG = (FOG - FOG.min()) / (FOG.max() - FOG.min())
GRAIN = [cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), .7) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W]
VIGN = (1 - .55 * np.clip(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2, 0, 1) ** 1.3).astype(np.float32)[..., None]


def over(dst, rgb, a, k=1.0):
    a = (a * k)[..., None]; return dst * (1 - a) + rgb * a


def fog(frame, t, amt=.12, speed=18, tint=(0.62, 0.58, 0.55)):
    off = int(t * speed) % (FOG.shape[1] - W)
    f = cv2.resize(FOG[:, off:off + W], (W, H))[..., None] * amt
    return frame + f * np.array(tint, np.float32)


def radial_glow(frame, x, y, r, col, a):
    if a <= .005 or r < 2: return frame
    x0, x1, y0, y1 = int(max(0, x - r)), int(min(W, x + r)), int(max(0, y - r)), int(min(H, y + r))
    if x1 <= x0 or y1 <= y0: return frame
    gy, gx = np.mgrid[y0:y1, x0:x1]
    d = np.clip(1 - np.hypot(gx - x, gy - y) / r, 0, 1) ** 2
    frame[y0:y1, x0:x1] += d[..., None] * np.array(col, np.float32) * a
    return frame


def clock_hands(frame, cam, cx, cy, r, ha, ma):
    """draw clock hands (world clock at cx, cy, radius r) through the camera"""
    zx = lambda x, y: (int((x - cam[0]) * cam[2] + W / 2), int((y - cam[1]) * cam[2] + H / 2))
    c = zx(cx, cy)
    for ang, L, wdt in ((ha, .5, 2.4), (ma, .78, 1.6)):
        e = zx(cx + math.sin(ang) * r * L, cy - math.cos(ang) * r * L)
        cv2.line(frame, c, e, tuple(v / 255 for v in INK), max(1, int(wdt * cam[2] * r / 45)), cv2.LINE_AA)
    return frame


def shake(t, amt):
    f = math.floor(t * 24); h = lambda i: (math.sin(i * 127.1 + 311.7) * 43758.5453) % 1
    return ((h(f * 1.7) - .5) * 2 * amt, (h(f * 2.3 + 9) - .5) * 2 * amt)


# ---------------- the frame ----------------
def frame_at(t, pl):
    fr = np.zeros((H, W, 3), np.float32)
    ck = chime_k(t)
    if t < 3 or (8 <= t < T_X):
        c = room_cam(t)
        sx, sy = shake(t, 14 * math.exp(-(t - 2.05) * 5)) if 2.05 < t < 3 else (0, 0)
        drift = (math.sin(t * .37) * 6, math.sin(t * .29 + 1) * 4)
        c = (c[0] + (sx + drift[0]) / c[2], c[1] + (sy + drift[1]) / c[2], c[2])
        O = ex_origin(c)
        rgb, _ = pl["city"].view(EA[0] + (c[0] - O[0]) / SE, EA[1] + (c[1] - O[1]) / SE, c[2] * SE); fr = rgb
        g, _ = pl["cityglow"].view(EA[0] + (c[0] - O[0]) / SE, EA[1] + (c[1] - O[1]) / SE, c[2] * SE)
        fr += g * SICK * .25
        # room variant: asleep → awake (19) → sitting up (22.3)
        a_s, a_w, a_t = 1 - seg(t, 19, 19.35), seg(t, 19, 19.35) * (1 - seg(t, 22.3, 22.7)), seg(t, 22.3, 22.7)
        half = 960 / c[2]
        use_clock = c[0] - half >= 522 and c[0] + half <= 998 and c[1] - 540 / c[2] >= 167 and c[1] + 540 / c[2] <= 433
        for key, k in (("room_sleep", a_s), ("room_awake", a_w), ("room_sit", a_t)):
            if k <= 0: continue
            p = pl["clock"] if (use_clock and key == "room_sleep") else pl[key]
            rgb, al = p.view(*c); fr = over(fr, rgb, al, k)
        p = ease(seg(t, 0, 2.05))
        ha = lerp(math.pi / 2 + 2 * math.pi * .75, math.pi / 2, p)
        ma = lerp(2 * math.pi * 7, 0, p) + (math.sin(t * 40) * .03 * math.exp(-(t - 2.05) * 3) if t > 2.05 else 0)
        fr = clock_hands(fr, c, 760, 300, 60, ha, ma)
        z = lambda x, y: ((x - c[0]) * c[2] + W / 2, (y - c[1]) * c[2] + H / 2)
        cxs, cys = z(760, 300)
        hookg = .9 if t < 3 else (.55 * math.exp(-max(0, t - 2.05) * 2) if t > 2.05 else 0)
        fr = radial_glow(fr, cxs, cys, 150 * c[2], SICK, .25 + hookg * .6 + .3 * min(ck, 1))
        if 18 < t: px, py = z(1065, 688); fr = radial_glow(fr, px, py, 120 * c[2], (.9, .76, .62), .25 + .08 * math.sin(t * 9))
        fr = fog(fr, t, .05)
        dark = .92 if t < 8 else lerp(.92, .32, ease(seg(t, 8, 14)))
        if t < 3: dark = .55
        fr *= (1 - dark)
        if t < 3:
            fr = radial_glow(fr, cxs, cys, 380, SICK, .35)
            if t > 2.05: fr += .45 * math.exp(-(t - 2.05) * 9) * np.array([.82, .92, .87], np.float32)
            fr *= 1 - seg(t, 2.6, 3.0)
        if t < 8.6 and t >= 8: fr *= seg(t, 8, 8.6)
    elif t < 8:
        a = seg(t - 3, .25, .8) * (1 - seg(t - 3, 4.4, 5.0))
        fr = pl["warn"][0] * a
    elif t < T_C:
        e = ex_cam(t)
        sx, sy = shake(t, 5 * min(chime_k(t, 7), 1.5)); drift = (math.sin(t * .31) * 5, math.sin(t * .23 + 2) * 4)
        e = (e[0] + (sx + drift[0]) / e[2], e[1] + (sy + drift[1]) / e[2], e[2])
        fr, _ = pl["city"].view(*e)
        g, _ = pl["cityglow"].view(*e)
        fr += g * SICK * (.15 + .65 * min(ck, 1.6))
        fr = fog(fr, t, .06 + .02 * math.sin(t * .5))
        c = close_from_ex(e)
        rgb, al = pl["win_a"].view(*c); fr = over(fr, rgb, al)
        rgb, al = pl["facade"].view(*e); fr = over(fr, rgb, al)
        if 66 < t < 67.2: fr *= 1 - .35 * math.sin(seg(t, 66, 67.2) * math.pi)
        if t < T_X + .5: fr = fr * seg(t, T_X - .01, T_X + .5) + 0  # brief dip as we pass the glass
    elif t < T_CARD:
        c = close_cam(t)
        sx, sy = shake(t, 10) if t > 78.4 else (0, 0); drift = (math.sin(t * .4) * 4, math.sin(t * .33) * 3)
        c = (c[0] + (sx + drift[0]) / c[2], c[1] + (sy + drift[1]) / c[2], c[2])
        wa = 1 - seg(t, 70.8, 73.2); wb = seg(t, 70.8, 73.2) * (1 - seg(t, 74, 74.6)) + seg(t, 76.6, 77.0) * 0
        wc = seg(t, 74, 74.6) * (1 - seg(t, 76.8, 77.1)); wd = seg(t, 76.8, 77.1)
        for key, k in (("win_a", wa), ("win_b", wb), ("win_c", wc), ("win_d", wd)):
            if k > 0: rgb, al = pl[key].view(*c); fr = over(fr, rgb, al, k)
        fr = fog(fr, t, .04)
        if t > 78.4: fr += .3 * math.exp(-(t - 78.4) * 8) * np.array([.85, .85, .91], np.float32)
        fr *= 1 - seg(t, 78.7, 79.6)
    elif t < T_CRED:
        lt = t - T_CARD
        a, b = pl["count"]
        k = 1 - .15 * ease(seg(lt, 0, .4)) + .15
        sx, sy = shake(t, 10 * math.exp(-lt * 6))
        M = np.float32([[k, 0, W / 2 * (1 - k) + sx], [0, k, H / 2 * (1 - k) + sy]])
        img = a * (1 - seg(lt, .35, .7)) + b * seg(lt, .35, .7)
        fr = cv2.warpAffine(img, M, (W, H)) * seg(lt, 0, .25) * (1 - seg(lt, 4.6, 5))
    else:
        lt = t - T_CRED
        a, b, c3 = pl["credits"]
        img = a * (1 - seg(lt, .7, 1.4)) + b * seg(lt, .7, 1.4) * (1 - seg(lt, 1.6, 2.3)) + c3 * seg(lt, 1.6, 2.3)
        fr = img * seg(lt, .2, .9) * (1 - seg(lt, 4.4, 5))
    fr = HFX.apply(fr, t, EV, SCARES)
    # grade: cold, contrasty, grain, vignette
    fr = np.clip(fr, 0, 1)
    fr = fr * VIGN
    fr = fr + GRAIN[int(t * 24) % 6][..., None] * .022
    return np.clip(fr, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plates"); ap.add_argument("--lang", default="ml")
    ap.add_argument("--sheet"); ap.add_argument("--from", dest="t0", type=float, default=0); ap.add_argument("--to", dest="t1", type=float, default=DUR)
    ap.add_argument("--out")
    a = ap.parse_args()
    pl = load_plates(a.plates)
    global SCARES; SCARES = HFX.load_scares(a.plates)
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(",")]
        cells = [cv2.resize((frame_at(t, pl) * 255).astype(np.uint8), (480, 270)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f"{t:.1f}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 1)
        cols = 4; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        sheet = np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)
        cv2.imwrite(a.out or "sheet.jpg", sheet); print("sheet", a.out); return
    out = a.out or os.path.join(S2, "video", f"COUNTDOWN_S2_ep01_{a.lang}.mp4")
    audio = os.path.join(S2, "audio", "mix", f"ep01_{a.lang}.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n0, n1 = int(a.t0 * FPS), int(a.t1 * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-ss", str(a.t0), "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(n0, n1):
        ff.stdin.write((frame_at(i / FPS, pl) * 255).astype(np.uint8).tobytes())
        if i % 240 == 0: print(f"{i / FPS:.0f}s", flush=True)
    ff.stdin.close(); ff.wait(); print("wrote", out)


if __name__ == "__main__":
    main()
