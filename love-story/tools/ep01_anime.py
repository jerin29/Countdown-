"""ഒരു റിപ്ലൈ · Episode 1 "2:14 AM" — ANIME version.
Same timeline, phone UI, voices and approved v9 score as tools/ep01.py; the painted plates are replaced by
anime images (love-story/anime_test/*.jpg) and her reel plays the animated dance clip (manjusha_dance.mp4).
Usage: python3 ep01_anime.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, functools, subprocess
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E

AN = '/home/user/Countdown-/love-story/anime_test'
IMG = {
    'or_room_lie': 'aadhi_214am', 'or_room_smile': 'aadhi_214am', 'or_room_sit': 'aadhi_sit', 'or_room_back': 'aadhi_back',
    'or_face_wonder': 'aadhi_wonder', 'or_face_smile': 'aadhi_smile', 'or_face_sad': 'aadhi_hesitant', 'or_face_shock': 'aadhi_shock',
    'or_face_tired': 'aadhi_smile',
    'or_nila_0': 'manjusha_dance', 'or_nila_1': 'manjusha_portrait', 'or_nila_2': 'manjusha_dance', 'or_nila_3': 'manjusha_portrait',
}


@functools.lru_cache(maxsize=None)
def plate(name):
    """anime image scaled to the 1080x1920 world at 2x (2160x3840), like the painted plates."""
    im = cv2.imread(os.path.join(AN, IMG[name] + '.jpg'))
    return cv2.resize(im, (2160, 3840), interpolation=cv2.INTER_CUBIC)


E.plate = plate

# camera paths for the room shots, fitted to the anime compositions (start -> end: cx, cy, zoom)
CAM = {
    'or_room_lie':   ((540, 960, 1.0), (640, 1060, 1.22)),
    'or_room_smile': ((700, 1120, 1.35), (720, 1160, 1.5)),
    'or_room_sit':   ((560, 1000, 1.05), (640, 1080, 1.25)),
    'or_room_back':  ((540, 900, 1.0), (640, 1120, 1.3)),
}
RNG = np.random.default_rng(11)
DROPS = [(RNG.random(), RNG.random(), 26 + RNG.random() * 40, .35 + RNG.random() * .4) for _ in range(140)]


def rain_layer(fr, t, k=.18):
    """soft falling rain over the whole frame (the window light catches it)."""
    o = fr.copy()
    for rx, ry, l, sp in DROPS:
        x = int(rx * E.W); y = int(((ry + t * sp) % 1) * E.H)
        cv2.line(o, (x, y), (x - 4, y + int(l)), (.85, .85, .9), 1, cv2.LINE_AA)
    return fr + (o - fr) * k


def room(name, t, keys, hm):
    a, b = CAM[name]
    k = E.ease(E.seg(t, keys[0], keys[1]))
    cx, cy, z = [E.lerp(p, q, k) for p, q in zip(a, b)]
    cx += math.sin(t * .4) * 4; cy += math.sin(t * .3 + 1) * 3
    fr = E.view(name, cx, cy, z).astype(np.float32) / 255
    fr = rain_layer(fr, t)
    return fr * (1 + .015 * math.sin(t * 9))


E.room = room


@functools.lru_cache(maxsize=1)
def dance_frames():
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(AN, 'manjusha_dance.mp4'), '-vf', 'scale=1080:1890,pad=1080:1920:0:15',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 1920, 1080, 3)


def nila_content(t, zoom=1.0):
    """her reel: the animated dance clip, looping with a short crossfade at the seam."""
    F = dance_frames(); n = len(F); per = n / 24.0; xf = .4
    lt = t % (per - xf)
    i = min(n - 1, int(lt * 24))
    img = F[i].astype(np.float32) / 255
    if lt > per - 2 * xf:   # fade the end into the start
        j = int((lt - (per - 2 * xf)) * 24)
        k = (lt - (per - 2 * xf)) / xf
        img = img * (1 - k) + F[min(n - 1, j)].astype(np.float32) / 255 * k
    if zoom != 1.0:
        M = np.float32([[zoom, 0, E.W / 2 * (1 - zoom)], [0, zoom, E.H / 2 * (1 - zoom)]])
        img = cv2.warpAffine(img, M, (E.W, E.H), borderMode=cv2.BORDER_REPLICATE)
    return img


E.nila_content = nila_content


@functools.lru_cache(maxsize=None)
def avatar(key, size):
    from PIL import Image, ImageDraw
    if key == 'nila':
        im = cv2.imread(os.path.join(AN, 'manjusha_portrait.jpg'))[380:1080, 250:950]
    else:
        im = E.feedimg(key)[700:1300, 240:840]
    im = cv2.resize(im, (size, size), interpolation=cv2.INTER_AREA)
    p = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    p.putalpha(m); return p


E.avatar = avatar
# her name is now Manjusha: until the voice line can be re-recorded, drop the old "Nila…" line (the screen shows the name)
E.VO = [v for v in E.VO if v[0] != 'v06']

if __name__ == '__main__':
    if '--out' not in sys.argv: sys.argv += ['--out', E.R + '/out/ONE_REPLY_ep01_anime_ml_9x16.mp4']
    E.main()
