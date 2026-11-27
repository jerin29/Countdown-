"""AGAIN — title song video (song v1, 2:55), no lyrics. Vertical 1080x1920, 24 fps.
Five pictures (two posters + new boy / bench / mirror) cut to the song: each shot is a camera move between two
framings (cx, cy, zoom) of one picture, with flashes on the chorus hits, a heartbeat pulse in the bench verse,
stadium-light flicker, dust/rain particles, title card at the start and the AGAIN · #23 card at the end.
Usage: python3 again_song_video.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, '/home/user/Countdown-/love-story/tools')
import ep01 as E

P = '/home/user/Countdown-/next-series/poster'
SONG = '/home/user/Countdown-/next-series/song/again-ml-v1_master.mp3'
OUT = '/home/user/Countdown-/next-series/out/AGAIN_title_song_v1_ml_9x16.mp4'
W, H, FPS = 1080, 1920, 24
DUR = 175.3
XF = .35
font, mlfont = E.font, E.mlfont
SRC = {'A': 'art_jump', 'B': 'art_dawn', 'edge': 'g_edge', 'bench': 'g_bench', 'mirror': 'g_mirror'}

# (t0, t1, pic, (cx, cy, z) start, (cx, cy, z) end, fx)   fx: '' | 'flash' | 'beat' | 'lights' | 'rain'
SHOTS = [
    (0.0, 6.0, 'A', (.5, .12, 2.2), (.5, .2, 1.6), 'lights'),          # stadium lights
    (6.0, 11.9, 'A', (.42, .34, 2.4), (.42, .3, 1.9), 'lights'),       # jersey 23 (title card over it)
    (11.9, 17.0, 'edge', (.5, .55, 1.0), (.5, .5, 1.15), 'rain'),      # ഒരു പന്തും ഒരു സ്വപ്നവും
    (17.0, 21.9, 'edge', (.78, .55, 1.8), (.72, .52, 2.1), 'rain'),     # കയ്യിൽ മുറുകെ… (his face)
    (21.9, 25.5, 'B', (.5, .7, 1.6), (.6, .65, 1.8), ''),              # പുലരിയിൽ കോർട്ടിൽ
    (25.5, 29.0, 'B', (.5, .5, 1.0), (.5, .45, 1.12), ''),             # എൻ ലക്ഷ്യം ഞാൻ കുറിച്ചു
    (29.0, 32.5, 'A', (.24, .1, 3.0), (.24, .1, 2.4), ''),             # വിസിൽ മുഴങ്ങും (the ball)
    (32.5, 35.8, 'B', (.55, .42, 2.4), (.55, .42, 2.0), ''),           # ഹൃദയം തുടി കൊട്ടുന്നു (23 from behind)
    (35.8, 44.5, 'B', (.5, .35, 1.3), (.5, .5, 1.0), ''),              # ഇനിയും നീ വരുമോ…
    (44.5, 51.2, 'A', (.45, .45, 1.35), (.45, .5, 1.0), 'flash'),      # വീണ്ടും… ഞാൻ വീഴും
    (51.2, 55.5, 'A', (.74, .9, 2.6), (.7, .88, 2.2), 'flash'),        # ഈ കോർട്ടിൽ എൻ പേര് മുഴങ്ങും (goal)
    (55.5, 61.3, 'A', (.42, .3, 2.2), (.42, .32, 1.6), 'flash'),       # Again, again
    (61.3, 64.6, 'A', (.5, .5, 1.0), (.5, .5, 1.1), 'flash'),          # ഇത് എന്റെ മടക്കം
    (64.6, 67.9, 'bench', (.5, .5, 1.0), (.5, .48, 1.12), 'beat'),     # ജേഴ്സി അണിഞ്ഞു ഞാൻ നിന്നു
    (67.9, 74.7, 'bench', (.85, .45, 2.2), (.8, .45, 2.5), 'beat'),     # കളത്തിൽ ഇറങ്ങിയില്ല (the court behind)
    (74.7, 82.9, 'bench', (.45, .82, 1.8), (.45, .8, 2.1), 'beat'),       # ആരുടെയോ വാശിക്കുള്ളിൽ (hands)
    (82.9, 85.9, 'bench', (.92, .79, 3.6), (.92, .79, 3.9), 'beat'),     # ബെഞ്ചിലിരുന്ന് ഞാൻ കണ്ടു (food packet)
    (85.9, 96.0, 'bench', (.55, .3, 2.0), (.53, .26, 3.0), 'beat'),     # എൻ കണ്ണുകൾ മാത്രം നനഞ്ഞു (eyes)
    (96.0, 102.3, 'mirror', (.5, .5, 1.0), (.5, .45, 1.2), ''),        # കണ്ണാടിയിൽ ഞാൻ നോക്കി
    (102.3, 109.5, 'mirror', (.58, .38, 2.0), (.58, .34, 2.6), ''),    # ഇത് ഒന്നിന്റെയും അവസാനമല്ല
    (109.5, 116.6, 'mirror', (.85, .47, 2.6), (.8, .47, 2.0), ''),      # ചെറുത് പോയാൽ പോകട്ടെ (jersey on the chair)
    (116.6, 123.7, 'B', (.5, .3, 1.5), (.5, .45, 1.1), ''),            # വർഷങ്ങൾ പിന്നെയും പോയി
    (123.7, 129.9, 'B', (.55, .42, 2.2), (.55, .42, 1.7), ''),         # ജില്ലയുടെ ജേഴ്സി അണിഞ്ഞു
    (129.9, 140.3, 'B', (.85, .72, 2.0), (.6, .6, 1.2), ''),           # ഞാൻ തുടങ്ങിയ ടീമിൽ…
    (140.3, 147.0, 'A', (.45, .45, 1.35), (.45, .5, 1.0), 'flash'),    # final chorus
    (147.0, 151.2, 'edge', (.5, .5, 1.2), (.5, .5, 1.0), 'flash'),
    (151.2, 157.0, 'bench', (.55, .3, 2.2), (.5, .5, 1.1), 'flash'),
    (157.0, 160.4, 'mirror', (.58, .36, 2.2), (.5, .5, 1.1), 'flash'),
    (160.4, 168.6, 'A', (.5, .5, 1.25), (.5, .5, 1.0), 'lights'),      # Again! Again!
    (168.6, 175.3, 'B', (.5, .5, 1.0), (.5, .5, 1.06), ''),            # വീണ്ടും… (end card over it)
]
HITS = [44.5, 51.2, 55.5, 57.9, 61.3, 140.3, 147.0, 151.2, 153.7, 157.0, 160.4]
RNG = np.random.default_rng(23)
DUST = [(RNG.random(), RNG.random(), 1 + RNG.random() * 2.5, .02 + RNG.random() * .05) for _ in range(90)]


@functools.lru_cache(maxsize=None)
def pic(k):
    im = cv2.imread(os.path.join(P, SRC[k] + '.jpg'))
    return cv2.resize(im, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255


def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def view(k, cx, cy, z):
    src = pic(k); sw, sh = W / z, H / z
    x0 = np.clip(cx * W - sw / 2, 0, W - sw); y0 = np.clip(cy * H - sh / 2, 0, H - sh)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def shot(i, t):
    t0, t1, k, a, b, fx = SHOTS[i]
    e = ease((t - t0) / (t1 - t0))
    cx, cy, z = [p + (q - p) * e for p, q in zip(a, b)]
    if fx == 'beat':                       # heartbeat pulse, about 70 bpm
        ph = (t * 70 / 60) % 1; z *= 1 + .012 * math.exp(-ph * 9)
    fr = view(k, cx, cy, z)
    if fx == 'lights': fr = fr * (1 + .06 * math.sin(t * 13) * math.sin(t * 3.1))
    if fx == 'rain':
        o = fr.copy()
        for rx, ry, l, sp in DUST:
            x = int(rx * W); y = int(((ry + t * sp * 9) % 1) * H)
            cv2.line(o, (x, y), (x - 3, y + int(l * 14)), (.85, .85, .9), 1, cv2.LINE_AA)
        fr = fr + (o - fr) * .25
    if fx in ('lights', 'flash'):          # floating dust in the light
        o = fr.copy()
        for rx, ry, s, sp in DUST[:50]:
            x = int(rx * W); y = int(((ry - t * sp) % 1) * H); cv2.circle(o, (x, y), int(s), (1, 1, 1), -1, cv2.LINE_AA)
        fr = fr + (o - fr) * .18
    return fr


@functools.lru_cache(maxsize=None)
def card(kind):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new('RGBA', (W, H)); sd = ImageDraw.Draw(sh)
    if kind == 'title':
        items = [((540, 1380), 'AGAIN', font('Bold', 230), (250, 244, 232)), ((540, 1550), 'വീണ്ടും', mlfont('Bold', 74), (246, 196, 92)),
                 ((540, 1660), 'Title Song', font('SemiBold', 42), (235, 228, 214))]
    else:
        items = [((540, 300), 'AGAIN', font('Bold', 230), (250, 244, 232)), ((540, 470), 'വീണ്ടും', mlfont('Bold', 74), (246, 196, 92)),
                 ((540, 1560), 'A TRUE STORY  ·  #23', font('SemiBold', 44), (255, 255, 255)),
                 ((540, 1650), 'ഉടൻ വരുന്നു', mlfont('Bold', 50), (246, 196, 92)),
                 ((540, 1840), 'Story: Jerin Joseph Sebastian  ·  @kili_poyi_ai', font('Regular', 30), (210, 205, 195))]
    for xy, t, f, c in items: sd.text((xy[0] + 4, xy[1] + 6), t, font=f, fill=(0, 0, 0, 220), anchor='mm')
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
    for xy, t, f, c in items: d.text(xy, t, font=f, fill=c + (255,), anchor='mm')
    if kind == 'end': d.rectangle([370, 1500, 710, 1506], fill=(214, 40, 52, 255))
    return im


def over(fr, layer, a):
    L = np.asarray(layer).astype(np.float32) / 255
    al = L[..., 3:4] * a
    return fr * (1 - al) + L[..., [2, 1, 0]] * al


def frame(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t)
    fr = shot(i, t)
    t1 = SHOTS[i][1]
    if i + 1 < len(SHOTS) and t > t1 - XF:            # crossfade into the next shot
        k = ease((t - (t1 - XF)) / XF); fr = fr * (1 - k) + shot(i + 1, t) * k
    for h in HITS:                                    # white flash on the hits
        if h - .02 <= t < h + .35: fr = fr + (1 - fr) * .55 * (1 - (t - h) / .35)
    if 7.0 <= t < 11.9: fr = over(fr, card('title'), ease((t - 7.0) / .8) * (1 - ease((t - 11.2) / .7)))
    if t >= 168.6: fr = over(fr * (1 - .45 * ease((t - 168.6) / 1.5)), card('end'), ease((t - 169.0) / 1.2))
    fr = fr * E.vign()
    if t < .6: fr = fr * (t / .6)
    if t > DUR - 1.2: fr = fr * max(0, (DUR - t) / 1.2)
    return np.clip(fr, 0, 1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=OUT)
    a = ap.parse_args()
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((frame(t) * 255).astype(np.uint8), (216, 384)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f'{t:.1f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 1)
        cols = 8; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)); print('sheet', a.out); return
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', SONG,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                           '-level', '4.0', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write((frame(i / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', a.out)


if __name__ == '__main__':
    main()
