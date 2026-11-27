"""ഒരു റിപ്ലൈ · Episode 5 "അടുത്തേക്ക്" (Getting Closer) — anime, vertical, ~84 s.
The story's turn: he wants to send a birthday gift and works out where she lives from a reel. Shown as a mistake,
not romance; no real place or readable address anywhere. Usage: python3 ep05_anime.py [--sheet t,..] [--out f.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2

W, H, FPS, DUR = E.W, E.H, E.FPS, 84.0
R = '/home/user/Countdown-/love-story/ep05'
AN = E2.AN
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
BOARD = (.917, .396)     # the blank name board on her gate pillar (e5_gate)
TEMPLE = (.84, .14)


@functools.lru_cache(maxsize=None)
def gate_reel_ui(paused):
    im = E.reel_ui('manjusha.dances', None, False, 'evening practice at home', '52.7K', '1,390', 'nila').copy()
    if paused:
        d = ImageDraw.Draw(im)
        d.ellipse([460, 880, 620, 1040], fill=(0, 0, 0, 110))
        d.rectangle([510, 918, 530, 1002], fill=(255, 255, 255, 235)); d.rectangle([550, 918, 570, 1002], fill=(255, 255, 255, 235))
    return im


def gate(t, t0, t1, z0, z1, c0, c1):
    """the paused gate reel, pinch-zoomed from c0 to c1."""
    k = ease(seg(t, t0, t1)); z = z0 + (z1 - z0) * k
    cx = c0[0] + (c1[0] - c0[0]) * k; cy = c0[1] + (c1[1] - c0[1]) * k
    src = cv2.resize(E2.pic('e5_gate'), (W, H), interpolation=cv2.INTER_AREA)
    sw, sh = W / z, H / z
    x0 = np.clip(cx * W - sw / 2, 0, W - sw); y0 = np.clip(cy * H - sh / 2, 0, H - sh)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    fr = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if z > 1.6: fr = cv2.GaussianBlur(fr, (0, 0), (z - 1.6) * 1.6)     # zoomed video goes soft — nothing readable
    return fr


def pinch(fr, t, t0, t1):
    """two fingertips spreading apart."""
    if not (t0 <= t < t1): return fr
    k = ease(seg(t, t0, t1)); o = fr.copy()
    for s in (-1, 1):
        x, y = int(540 + s * (60 + 160 * k)), int(980 + s * (60 + 160 * k))
        cv2.circle(o, (x, y), 46, (1, 1, 1), -1, cv2.LINE_AA)
    return fr * .82 + o * .18


@functools.lru_cache(maxsize=None)
def map_ui(stage):
    """a made-up map: no real roads, names or places. stage 0 = search, 1 = pin dropped."""
    im = Image.new('RGBA', (W, H), (232, 229, 220, 255)); d = ImageDraw.Draw(im)
    rng = np.random.default_rng(7)
    for _ in range(9):
        x = rng.integers(0, W); d.polygon([(x, 0), (x + 40, 0), (x + 40 + rng.integers(-300, 300), H), (x + rng.integers(-300, 300), H)], fill=(222, 218, 208, 255))
    d.ellipse([-200, 1300, 500, 1900], fill=(196, 226, 186, 255)); d.ellipse([700, 300, 1300, 800], fill=(196, 226, 186, 255))
    pts = [(-50, 700 + 80 * math.sin(i / 3)) for i in range(1)] + [(i * 60, 700 + 90 * math.sin(i / 3)) for i in range(20)]
    d.line(pts, fill=(164, 204, 236, 255), width=60)
    for y in (420, 1050, 1500):
        d.line([(0, y), (W, y + 120)], fill=(255, 255, 255, 255), width=26)
    for x in (260, 640, 900):
        d.line([(x, 0), (x - 140, H)], fill=(255, 255, 255, 255), width=22)
    d.line([(0, 1250), (W, 980)], fill=(250, 214, 120, 255), width=34)
    d.rounded_rectangle([40, 110, W - 40, 210], 50, fill=(255, 255, 255, 255))
    d.ellipse([70, 130, 130, 190], outline=(120, 120, 128, 255), width=5); d.line([(122, 182), (146, 206)], fill=(120, 120, 128, 255), width=6)
    d.text((170, 160), 'Search here', font=font('Regular', 38), fill=(120, 120, 128, 255), anchor='lm')
    if stage:
        d.rounded_rectangle([0, 1560, W, H], 40, fill=(255, 255, 255, 255))
        d.rounded_rectangle([490, 1580, 590, 1590], 5, fill=(210, 210, 214, 255))
        d.text((60, 1640), 'Dropped pin', font=font('SemiBold', 46), fill=(30, 30, 36, 255))
        for i, (lab, x) in enumerate([('Directions', 60), ('Save', 380), ('Share', 640)]):
            d.rounded_rectangle([x, 1740, x + (290 if i == 0 else 230), 1830], 45, fill=(26, 115, 232, 255) if i == 0 else (234, 240, 250, 255))
            d.text((x + (145 if i == 0 else 115), 1785), lab, font=font('SemiBold', 34), fill=(255, 255, 255, 255) if i == 0 else (26, 115, 232, 255), anchor='mm')
    return im


def pin(fr, t, t0):
    if t < t0: return fr
    k = min(1, (t - t0) / .35); y = int(860 * ease(k) + 500 * (1 - ease(k)))
    o = fr.copy()
    cv2.ellipse(o, (540, 900), (30, 10), 0, 0, 360, (.4, .4, .45), -1, cv2.LINE_AA)
    cv2.circle(o, (540, y - 60), 46, (.2, .25, .92), -1, cv2.LINE_AA)
    pts = np.array([[500, y - 40], [580, y - 40], [540, y + 30]], np.int32); cv2.fillPoly(o, [pts], (.2, .25, .92), cv2.LINE_AA)
    cv2.circle(o, (540, y - 60), 16, (1, 1, 1), -1, cv2.LINE_AA)
    return o


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 5', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'അടുത്തേക്ക്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank(): return np.zeros((H, W, 3), np.float32)


def frame(t):
    if t < 2.5:          # HOOK: her paused reel, two fingers zooming into the background
        fr = over(gate(t, 0, 2.5, 1.0, 1.7, (.5, .5), BOARD), gate_reel_ui(True))
        fr = pinch(fr, t, .2, 2.0)
    elif t < 10.0:
        fr = still('e5_kiran_story', t, 2.5, 10.0, 1.0, 1.12, .45, .4, .4, .35)
    elif t < 20.0:
        fr = still('e5_shrug', t, 10.0, 20.0, 1.0, 1.1, .6, .4, .65, .35)
    elif t < 24.0:
        fr = still('aadhi_sit', t, 20.0, 24.0, 1.0, 1.15, .5, .55, rain=True)
    elif t < 32.0:       # her reels, frame by frame
        lt = t - 24.0; tt = 24.0 + (lt * .35 if lt > 3.5 else lt)    # slows down: he's scrubbing
        fr = E.reel(tt, lt, lt / 8)
        if lt > 3.5: fr = tap(fr, 540, 1880, min(1, (lt - 3.5) / .4) * .5)
    elif t < 42.0:
        fr = still('e5_gift', t, 32.0, 42.0, 1.0, 1.14, .4, .6, .35, .55, rain=True)
    elif t < 48.0:       # the reel at her gate — paused
        fr = over(gate(t, 42.0, 48.0, 1.0, 1.0, (.5, .5), (.5, .5)), gate_reel_ui(t > 43.2))
        fr = tap(fr, 540, 960, seg(t, 42.8, 43.4))
    elif t < 54.0:
        fr = gate(t, 48.0, 53.5, 1.0, 2.4, (.5, .5), BOARD if t < 51 else TEMPLE)
        if t >= 51: fr = gate(t, 51.0, 54.0, 2.4, 2.0, BOARD, TEMPLE)
        fr = pinch(fr, t, 48.2, 49.6)
    elif t < 62.0:
        fr = over(blank(), map_ui(1 if t > 58.6 else 0))
        fr = pin(fr, t, 58.2)
    elif t < 66.0:
        fr = still('aadhi_back', t, 62.0, 66.0, 1.1, 1.3, .55, .5)
    elif t < 70.0:
        fr = still('e5_kiran_worried', t, 66.0, 70.0, 1.0, 1.1, .5, .42)
    elif t < 74.0:
        fr = still('aadhi_hesitant', t, 70.0, 74.0, 1.7, 1.9, .55, .3)
    elif t < 79.0:
        fr = still('e5_paper', t, 74.0, 79.0, 1.0, 1.25, .5, .62)
        fr = fr * (1 - .6 * seg(t, 78.3, 79.0))
    else:
        lt = t - 79.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, 0, .6) * (1 - seg(lt, 4.4, 5.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .15: fr = fr * seg(t, 0, .15)
    return np.clip(fr, 0, 1)


def zoomed(fr, z, cx=.5, cy=.5):
    M = np.float32([[z, 0, W * cx * (1 - z)], [0, z, H * cy * (1 - z)]])
    return cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REPLICATE)


CUTS = [2.5, 10.0, 20.0, 24.0, 32.0, 42.0, 48.0, 54.0, 62.0, 66.0, 70.0, 74.0]
VO = [('k1', 3.0), ('a1', 10.8), ('a2', 13.2), ('a3', 33.2), ('k2', 66.5)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-5))
    # the turn: the score thins from the gate onward, and almost stops at the paper
    for a_, b_, g in [(42, 54, -6), (54, 74, -9), (74, 79, -18)]:
        env[int(a_ * SR):int(b_ * SR)] = np.minimum(env[int(a_ * SR):int(b_ * SR)], db(g))
    env = np.convolve(env, np.ones(int(.5 * SR)) / int(.5 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.5), fin=.2, fout=1.0)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    place(buf, S('tap.wav'), 42.85, db(-12))
    for tt in np.arange(54.5, 62.0, .5): place(buf, S('tap2.wav'), tt, db(-26))        # quiet clock tick under the map
    place(buf, S('pop.wav'), 58.2, db(-12))
    place(buf, load(A + '/pen.mp3'), 74.3, db(-6), fin=.1, fout=.4)
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_ in [(20.0, 24.0), (32.0, 42.0), (62.0, 79.0)]:
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(-18), fin=.4, fout=.5)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep05_anime_ml_9x16.mp4')
    a = ap.parse_args()
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((frame(t) * 255).astype(np.uint8), (216, 384)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f'{t:.1f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 1)
        cols = 8; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)); print('sheet', a.out); return
    wav = mix(a.out)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                           '-level', '4.0', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write((frame(i / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', a.out)


if __name__ == '__main__':
    main()
