"""ഒരു റിപ്ലൈ (One Reply) · trial Episode 1 "2:14 AM" — compositor + mixer (vertical 1080x1920, 24 fps).
Painted plates: animation-base/src/onereply/ep01.js (rendered into love-story/trial/plates/<loop>/t0_XX.png).
Usage: python3 ep01.py [--sheet 0,2,5,...] [--out file.mp4] [--audio-only]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

R = '/home/user/Countdown-/love-story/trial'
P = R + '/plates'
A = R + '/audio'
SONG = '/home/user/Countdown-/love-story/song/oru-reply-ml-v1v3_combo.mp3'
W, H, FPS, DUR = 1080, 1920, 24, 83.0
SR = 48000
F_INTER = '/usr/share/fonts/opentype/inter/Inter-{}.otf'
F_ML = '/usr/share/fonts/truetype/noto/NotoSansMalayalam-{}.ttf'


def font(w, s):
    return ImageFont.truetype(F_INTER.format(w), s)


def mlfont(w, s):
    return ImageFont.truetype(F_ML.format(w), s, layout_engine=ImageFont.Layout.RAQM)


seg = lambda t, a, b: min(1.0, max(0.0, (t - a) / (b - a)))
ease = lambda x: x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


# ---------------------------------------------------------------- plates
@functools.lru_cache(maxsize=None)
def plate(name):
    d = os.path.join(P, name)
    fs = sorted(f for f in os.listdir(d) if f.endswith('.png'))
    tiles = [cv2.imread(os.path.join(d, f)) for f in fs]
    rows = [np.concatenate(tiles[i:i + 2], 1) for i in range(0, 8, 2)]
    return np.ascontiguousarray(np.concatenate(rows, 0)[:3840, :2160])


def view(name, cx, cy, z):
    """camera on a plate: world point (cx, cy) at screen centre, z = zoom (1 = whole 1080x1920 world)."""
    M = np.float32([[z / 2, 0, W / 2 - cx * z], [0, z / 2, H / 2 - cy * z]])
    return cv2.warpAffine(plate(name), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def to_screen(wx, wy, cx, cy, z):
    return W / 2 + (wx - cx) * z, H / 2 + (wy - cy) * z


@functools.lru_cache(maxsize=None)
def feedimg(k):
    return cv2.resize(cv2.imread(os.path.join(P, 'feed', k + '.png')), (W, H))


VIGN = None


def vign():
    global VIGN
    if VIGN is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H / 2) / (H * .7)) ** 2)
        VIGN = np.clip(1.08 - .45 * r ** 2, .55, 1)[..., None].astype(np.float32)
    return VIGN


# ---------------------------------------------------------------- phone UI (PIL)
def rgba():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def heart(d, cx, cy, s, fill=None, outline=(255, 255, 255, 255), w=6):
    pts = []
    for i in range(60):
        a = i / 60 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * s / 17, cy + y * s / 17))
    d.polygon(pts, fill=fill, outline=None)
    d.line(pts + [pts[0]], fill=outline, width=w, joint='curve')


def shadow_text(d, xy, txt, f, fill=(255, 255, 255, 255), anchor='la'):
    x, y = xy
    d.text((x + 2, y + 2), txt, font=f, fill=(0, 0, 0, 140), anchor=anchor)
    d.text((x, y), txt, font=f, fill=fill, anchor=anchor)


@functools.lru_cache(maxsize=None)
def reel_ui(user, follow, liked, caption, likes, comments, ava_key=None):
    im = rgba(); d = ImageDraw.Draw(im)
    # top and bottom darkening for legibility
    g = np.zeros((H, W, 4), np.uint8)
    for y in range(0, 260): g[y, :, 3] = int(110 * (1 - y / 260))
    for y in range(H - 620, H): g[y, :, 3] = int(170 * ((y - (H - 620)) / 620) ** 1.4)
    im = Image.alpha_composite(im, Image.fromarray(g, 'RGBA')); d = ImageDraw.Draw(im)
    # status bar
    shadow_text(d, (60, 38), '2:14', font('SemiBold', 34))
    for i in range(4): d.rectangle([900 + i * 14, 58 - i * 6, 908 + i * 14, 64], fill=(255, 255, 255, 230))
    d.rounded_rectangle([968, 40, 1022, 64], 6, outline=(255, 255, 255, 230), width=3); d.rectangle([972, 44, 1000, 60], fill=(255, 255, 255, 230))
    shadow_text(d, (60, 112), 'Reels', font('Bold', 52))
    d.ellipse([968, 118, 1016, 166], outline=(255, 255, 255, 255), width=5); d.ellipse([984, 134, 1000, 150], fill=(255, 255, 255, 255))
    # right rail
    x = 990
    heart(d, x, 1150, 40, fill=(237, 73, 86, 255) if liked else None, outline=(237, 73, 86, 255) if liked else (255, 255, 255, 255))
    shadow_text(d, (x, 1200), likes, font('SemiBold', 28), anchor='ma')
    d.ellipse([x - 36, 1282, x + 36, 1350], outline=(255, 255, 255, 255), width=6); d.polygon([(x - 30, 1336), (x - 40, 1362), (x - 14, 1346)], fill=(255, 255, 255, 255))
    shadow_text(d, (x, 1370), comments, font('SemiBold', 28), anchor='ma')
    d.line([(x - 34, 1470), (x + 34, 1440), (x + 6, 1510), (x - 4, 1478), (x - 34, 1470)], fill=(255, 255, 255, 255), width=6, joint='curve')
    shadow_text(d, (x, 1530), '312', font('SemiBold', 28), anchor='ma')
    for i in range(3): d.ellipse([x - 26 + i * 22, 1606, x - 16 + i * 22, 1616], fill=(255, 255, 255, 255))
    # user row
    if ava_key:
        av = avatar(ava_key, 84)
        im.alpha_composite(av, (50, 1636)); d = ImageDraw.Draw(im)
    d.ellipse([50, 1636, 134, 1720], outline=(255, 255, 255, 255), width=3)
    shadow_text(d, (156, 1660), user, font('SemiBold', 36))
    tw = d.textlength(user, font=font('SemiBold', 36))
    if follow is not None:
        bx = 156 + tw + 26
        lab = 'Following' if follow else 'Follow'
        bw = d.textlength(lab, font=font('SemiBold', 30)) + 44
        d.rounded_rectangle([bx, 1652, bx + bw, 1710], 14, outline=(255, 255, 255, 255), width=3)
        d.text((bx + bw / 2, 1681), lab, font=font('SemiBold', 30), fill=(255, 255, 255, 255), anchor='mm')
    shadow_text(d, (56, 1746), caption, font('Regular', 32))
    shadow_text(d, (56, 1800), 'Original audio', font('Regular', 28), fill=(235, 235, 235, 255))
    return im


@functools.lru_cache(maxsize=None)
def avatar(key, size):
    if key == 'nila':
        img = view('or_nila_1', 540, 930, 4.2)[960 - 330:960 + 330, 540 - 330:540 + 330]
    else:
        img = feedimg(key)[700:1300, 240:840]
    img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
    rgbim = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert('RGBA')
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    rgbim.putalpha(m); return rgbim


@functools.lru_cache(maxsize=None)
def profile_ui(following):
    im = Image.new('RGBA', (W, H), (12, 12, 14, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:16', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 150), (84, 126), (60, 150), (84, 174)], fill=(255, 255, 255, 255), width=6)
    d.text((120, 150), 'nila.dances', font=font('Bold', 46), fill=(255, 255, 255, 255), anchor='lm')
    tw = d.textlength('nila.dances', font=font('Bold', 46))
    d.ellipse([120 + tw + 16, 134, 120 + tw + 50, 168], fill=(56, 151, 240, 255))
    d.line([(120 + tw + 24, 151), (120 + tw + 31, 159), (120 + tw + 43, 143)], fill=(255, 255, 255, 255), width=4)
    # avatar with story ring
    d.ellipse([52, 232, 292, 472], outline=(220, 60, 120, 255), width=8)
    im.alpha_composite(avatar('nila', 216), (64, 244)); d = ImageDraw.Draw(im)
    for i, (n, lab) in enumerate([('312', 'posts'), ('500K', 'followers'), ('248', 'following')]):
        cx = 470 + i * 210
        d.text((cx, 322), n, font=font('Bold', 46), fill=(255, 255, 255, 255), anchor='mm')
        d.text((cx, 380), lab, font=font('Regular', 30), fill=(220, 220, 220, 255), anchor='mm')
    d.text((60, 520), 'Nila', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((60, 574), 'Dancer', font=font('Regular', 32), fill=(160, 160, 165, 255))
    d.text((60, 622), 'Classical x contemporary  ·  Kochi', font=font('Regular', 34), fill=(255, 255, 255, 255))
    d.text((60, 670), 'collabs: mail in bio', font=font('Regular', 34), fill=(255, 255, 255, 255))
    # buttons
    if following:
        d.rounded_rectangle([60, 760, 520, 850], 18, fill=(54, 54, 58, 255))
        d.text((290, 805), 'Following  ⌄', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    else:
        d.rounded_rectangle([60, 760, 520, 850], 18, fill=(0, 149, 246, 255))
        d.text((290, 805), 'Follow', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle([540, 760, 1020, 850], 18, fill=(54, 54, 58, 255))
    d.text((780, 805), 'Message', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    # grid tabs
    d.line([(0, 900), (W, 900)], fill=(40, 40, 44, 255), width=2)
    for i in range(3):
        x = 180 + i * 360
        d.rectangle([x - 22, 940, x + 22, 984], outline=(255, 255, 255, 255) if i == 1 else (120, 120, 125, 255), width=4)
    # reels grid (portrait thumbnails of her dances)
    keys = ['or_nila_0', 'or_nila_2', 'or_nila_3', 'or_nila_1', 'or_nila_3', 'or_nila_0']
    for i, k in enumerate(keys):
        c, r = i % 3, i // 3
        x0, y0, tw_, th = c * 361, 1020 + r * 482, 358, 478
        z = [1.0, 1.3, 1.15, 1.25, 1.05, 1.4][i]
        im_ = view(k, 540, 1150, z)
        im_ = cv2.resize(im_[160:1760, 90:990], (tw_, th), interpolation=cv2.INTER_AREA)
        if i % 2: im_ = cv2.convertScaleAbs(im_, alpha=1.08, beta=6)
        im.paste(Image.fromarray(cv2.cvtColor(im_, cv2.COLOR_BGR2RGB)), (x0, y0)); d = ImageDraw.Draw(im)
        d.polygon([(x0 + tw_ - 52, y0 + 18), (x0 + tw_ - 52, y0 + 50), (x0 + tw_ - 22, y0 + 34)], fill=(255, 255, 255, 230))
        d.text((x0 + 16, y0 + th - 48), ['1.2M', '640K', '2.1M', '880K', '1.5M', '410K'][i], font=font('SemiBold', 30), fill=(255, 255, 255, 255))
    return im


@functools.lru_cache(maxsize=None)
def dm_ui(text, cursor, bubble, failed, toast):
    im = Image.new('RGBA', (W, H), (12, 12, 14, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:17' if not failed else '3:41', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    im.alpha_composite(avatar('nila', 80), (110, 120)); d = ImageDraw.Draw(im)
    d.text((210, 138), 'Nila', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((210, 186), 'nila.dances', font=font('Regular', 28), fill=(160, 160, 165, 255))
    d.line([(0, 240), (W, 240)], fill=(32, 32, 36, 255), width=2)
    if not bubble:
        im.alpha_composite(avatar('nila', 220), (430, 420)); d = ImageDraw.Draw(im)
        d.text((540, 690), 'Nila', font=font('Bold', 44), fill=(255, 255, 255, 255), anchor='mm')
        d.text((540, 744), 'nila.dances · Instagram', font=font('Regular', 30), fill=(160, 160, 165, 255), anchor='mm')
        d.text((540, 790), '500K followers · 312 posts', font=font('Regular', 30), fill=(160, 160, 165, 255), anchor='mm')
        d.rounded_rectangle([420, 840, 660, 910], 16, fill=(54, 54, 58, 255))
        d.text((540, 875), 'View profile', font=font('SemiBold', 30), fill=(255, 255, 255, 255), anchor='mm')
    else:
        bw = d.textlength(bubble, font=font('Regular', 38)) + 64
        d.rounded_rectangle([W - 60 - bw, 1000, W - 60, 1090], 44, fill=(120, 60, 230, 255))
        d.text((W - 60 - bw / 2, 1045), bubble, font=font('Regular', 38), fill=(255, 255, 255, 255), anchor='mm')
        if failed:
            d.ellipse([W - 60 - bw - 70, 1020, W - 60 - bw - 20, 1070], fill=(237, 73, 86, 255))
            d.text((W - 60 - bw - 45, 1045), '!', font=font('Bold', 34), fill=(255, 255, 255, 255), anchor='mm')
            d.text((W - 60, 1120), 'Not delivered', font=font('Regular', 28), fill=(237, 73, 86, 255), anchor='ra')
    # input bar
    y = 1130 if not toast else 1130
    d.rounded_rectangle([40, y, W - 40, y + 100], 50, fill=(38, 38, 42, 255))
    d.ellipse([56, y + 14, 128, y + 86], fill=(56, 151, 240, 255))
    d.rectangle([80, y + 38, 104, y + 62], outline=(255, 255, 255, 255), width=4)
    if text:
        d.text((150, y + 50), text, font=font('Regular', 38), fill=(255, 255, 255, 255), anchor='lm')
        tw = d.textlength(text, font=font('Regular', 38))
        if cursor: d.line([(154 + tw, y + 26), (154 + tw, y + 74)], fill=(56, 151, 240, 255), width=4)
        d.text((W - 80, y + 50), 'Send', font=font('SemiBold', 36), fill=(56, 151, 240, 255), anchor='rm')
    else:
        d.text((150, y + 50), 'Message...', font=font('Regular', 38), fill=(150, 150, 155, 255), anchor='lm')
        if cursor: d.line([(150, y + 26), (150, y + 74)], fill=(56, 151, 240, 255), width=4)
    # keyboard
    d.rectangle([0, 1270, W, H], fill=(30, 30, 33, 255))
    rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
    for r, keys in enumerate(rows):
        n = len(keys); kw = 96; x0 = (W - n * (kw + 8)) / 2
        for i, k in enumerate(keys):
            x = x0 + i * (kw + 8); yy = 1300 + r * 140
            d.rounded_rectangle([x, yy, x + kw, yy + 120], 12, fill=(70, 70, 75, 255))
            d.text((x + kw / 2, yy + 60), k, font=font('Regular', 46), fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle([250, 1720, 830, 1840], 12, fill=(70, 70, 75, 255))
    d.text((540, 1780), 'space', font=font('Regular', 38), fill=(230, 230, 230, 255), anchor='mm')
    if toast:
        d.rounded_rectangle([90, 560, W - 90, 720], 30, fill=(48, 48, 52, 245))
        d.text((540, 610), "You can't message this account", font=font('SemiBold', 38), fill=(255, 255, 255, 255), anchor='mm')
        d.text((540, 668), 'Only people they follow can message them.', font=font('Regular', 29), fill=(190, 190, 195, 255), anchor='mm')
    return im


def over(base, ui):
    """alpha-composite a PIL RGBA layer onto a float32 BGR frame (0..1)."""
    a = np.asarray(ui, np.float32) / 255
    rgb = a[..., [2, 1, 0]]; al = a[..., 3:4]
    return base * (1 - al) + rgb * al


def tap(fr, x, y, k):
    """touch indicator: ring that grows and fades, k in 0..1"""
    if not 0 < k < 1: return fr
    o = fr.copy(); r = int(30 + 60 * k)
    cv2.circle(o, (int(x), int(y)), r, (1, 1, 1), -1, cv2.LINE_AA)
    return fr + (o - fr) * .28 * (1 - k)


# ---------------------------------------------------------------- scene renderers
DANCE_PER = .42   # seconds per dance pose (≈ the score's groove)


def nila_content(t, zoom=1.0):
    i = int(t / DANCE_PER) % 4
    k = (t / DANCE_PER) % 1
    bob = math.sin(t * 2 * math.pi / (DANCE_PER * 2)) * 10
    img = view(f'or_nila_{i}', 540, 1000 - bob / zoom, 1.06 * zoom).astype(np.float32) / 255
    if k < .18:   # quick crossfade between poses so it reads as motion, not a cut
        j = (i - 1) % 4
        prev = view(f'or_nila_{j}', 540, 1000 - bob / zoom, 1.06 * zoom).astype(np.float32) / 255
        img = prev * (1 - k / .18) + img * (k / .18)
    return img


def reel(t, lt, progress, follow=False, liked=False, zoom=1.0):
    fr = nila_content(t, zoom)
    fr = over(fr, reel_ui('nila.dances', follow, liked, 'terrace nights & old songs', '48.2K' if not liked else '48.2K', '1,204', 'nila'))
    return progbar(fr, progress)


def progbar(fr, p):
    fr[H - 8:H, :, :] = fr[H - 8:H, :, :] * .4 + .25
    x = int(W * (p % 1))
    fr[H - 8:H, :x, :] = 1
    return fr


def other_reel(k, user, likes):
    fr = feedimg(k).astype(np.float32) / 255
    return over(fr, reel_ui(user, False, False, 'watch till the end', likes, '96', k))


FEED = [('a', 'kili_poyi_ai', '3,118'), ('b', 'kili_poyi_ai', '1,902'), ('c', 'kili_poyi_ai', '2,477')]


def feed(t):
    # reels swiped every ~1.6 s, then a slow swipe into Nila's reel at 14.4-15.2
    sw = [(10.0, .35), (11.6, .35), (13.2, .35), (14.4, .8)]
    pages = [other_reel(*FEED[0]), other_reel(*FEED[1]), other_reel(*FEED[2])]
    idx, off = 0, 0.0
    for i, (ts, d) in enumerate(sw):
        if t >= ts + d: idx = i + 1
        elif t >= ts: idx = i; off = ease(seg(t, ts, ts + d))
    def page(i):
        return pages[i] if i < 3 else reel(t, 0, .02 * (t - 14.4))
    cur = page(idx)
    if off <= 0: return cur, None
    nxt = page(idx + 1)
    dy = int(H * off)
    out = np.empty_like(cur); out[:H - dy] = cur[dy:]; out[H - dy:] = nxt[:dy]
    return out, (540, 1500 - 900 * off)


def clock_hands(fr, cx, cy, z, hm):
    h, m = hm
    x, y = to_screen(250, 430, cx, cy, z); r = 92 * z
    am = m / 60 * 2 * math.pi; ah = (h % 12 + m / 60) / 12 * 2 * math.pi
    for a, L, w in [(ah, .5, 7), (am, .78, 5)]:
        cv2.line(fr, (int(x), int(y)), (int(x + math.sin(a) * r * L), int(y - math.cos(a) * r * L)), (.12, .1, .11), max(2, int(w * z * .7)), cv2.LINE_AA)
    cv2.circle(fr, (int(x), int(y)), max(3, int(6 * z)), (.12, .1, .11), -1, cv2.LINE_AA)
    return fr


RNG = np.random.default_rng(7)
DROPS = [(RNG.random(), RNG.random(), 18 + RNG.random() * 30) for _ in range(90)]


def rain(fr, t, cx, cy, z):
    x0, y0 = to_screen(560, 210, cx, cy, z); x1, y1 = to_screen(980, 770, cx, cy, z)
    for i, (rx, ry, l) in enumerate(DROPS):
        x = x0 + rx * (x1 - x0); y = y0 + ((ry + t * .9) % 1) * (y1 - y0)
        cv2.line(fr, (int(x), int(y)), (int(x - 3 * z), int(y + l * z)), (.78, .78, .72), 1, cv2.LINE_AA)
    return fr


def room(name, t, keys, hm):
    k = ease(seg(t, keys[0], keys[1]))
    cx, cy, z = [lerp(a, b, k) for a, b in zip(keys[2], keys[3])]
    cx += math.sin(t * .4) * 4; cy += math.sin(t * .3 + 1) * 3
    fr = view(name, cx, cy, z).astype(np.float32) / 255
    fr = rain(fr, t, cx, cy, z)
    fr = clock_hands(fr, cx, cy, z, hm)
    # phone screen flicker light
    return fr * (1 + .02 * math.sin(t * 9))


def face(name, t, t0, t1, z0, z1, cy=900, shake=0.0):
    k = ease(seg(t, t0, t1)); z = lerp(z0, z1, k)
    sx = math.sin(t * 61) * shake; sy = math.cos(t * 47) * shake
    fr = view(name, 540 + sx + math.sin(t * .5) * 3, cy + sy, z).astype(np.float32) / 255
    return fr * (1 + .03 * math.sin(t * 7.3))      # phone light flicker


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    if stage >= 0:
        d.text((540, 820), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
        heart(d, 540, 990, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
        d.text((540, 1100), 'എപ്പിസോഡ് 1', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
        d.text((540, 1180), '2:14 AM', font=font('Medium', 44), fill=(170, 160, 146, 255), anchor='mm')
    if stage >= 1:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def endcard(t):
    lt = t - 76.6
    fr = np.zeros((H, W, 3), np.float32) + np.array([16, 10, 10], np.float32) / 255
    fr = over(fr, endcard_ui(1 if lt > 2.6 else 0))
    return fr * seg(lt, 0, .8) * (1 - seg(lt, 5.8, 6.4))


# ---------------------------------------------------------------- timeline
def frame(t):
    if t < 1.8:   # HOOK: her reel
        fr = reel(t, t, .30 + t * .03)
    elif t < 3.2:
        fr = face('or_face_wonder' if t < 2.55 else 'or_face_smile', t, 1.8, 3.2, 1.15, 1.3)
    elif t < 8.5:
        fr = room('or_room_lie', t, (3.2, 8.5, (540, 1000, 1.0), (430, 1090, 1.25)), (2, 14))
    elif t < 15.0:
        fr, tp = feed(t)
        if tp: fr = tap(fr, *tp, .3)
    elif t < 21.0:
        fr = reel(t, t - 15, .02 * (t - 14.4))
    elif t < 23.6:
        fr = face('or_face_wonder', t, 21.0, 23.6, 1.1, 1.35)
    elif t < 27.0:
        fr = reel(t, t - 23.6, .20 + .028 * (t - 23.6), zoom=1.18)
    elif t < 29.5:
        p = .55 + .25 * (t - 27.0)   # runs to the end at 28.8 and loops (replay)
        fr = reel(t, t - 27, p if p < 1 else (p - 1) * .3)
        if 28.8 <= t < 29.4:
            fr = fr * (1 - .25 * (1 - seg(t, 28.8, 29.4)))
    elif t < 32.0:
        fr = face('or_face_smile', t, 29.5, 32.0, 1.0, 1.2)
    elif t < 35.5:
        fr = room('or_room_sit', t, (32.0, 35.5, (540, 1100, 1.1), (520, 1060, 1.3)), (2, 40))
    elif t < 37.5:
        fr = reel(t, t - 35.5, .35 + .03 * (t - 35.5), liked=True)
    elif t < 40.0:
        fr = room('or_room_smile', t, (37.5, 40.0, (480, 1080, 1.2), (440, 1110, 1.35)), (3, 5))
    elif t < 51.0:
        following = t >= 48.6
        fr = over(np.zeros((H, W, 3), np.float32), profile_ui(following))
        y = int(260 * ease(seg(t, 44.8, 46.6)) * (1 - ease(seg(t, 47.4, 48.1))))   # scroll down to her grid, back up to Follow
        if y > 0: fr = np.concatenate([fr[y:], np.repeat(fr[-1:], y, 0)], 0)
        fr = tap(fr, 290, 805, seg(t, 48.4, 48.9))
        fr = tap(fr, 780, 805, seg(t, 50.6, 51.0))
    elif t < 60.0:
        txt, cur = dm_text(t)
        fr = over(np.zeros((H, W, 3), np.float32), dm_ui(txt, cur, None, False, False))
    elif t < 62.5:
        fr = face('or_face_sad', t, 60.0, 62.5, 1.15, 1.3)
    elif t < 70.0:
        fr = room('or_room_back', t, (62.5, 70.0, (540, 1060, 1.0), (470, 1180, 1.3)), (3, 40))
    elif t < 74.6:
        txt, cur = dm_text2(t)
        sent = t >= 71.8; failed = t >= 72.6
        fr = over(np.zeros((H, W, 3), np.float32), dm_ui('' if sent else txt, cur and not sent, 'Hi' if sent else None, failed, failed))
        fr = tap(fr, W - 140, 1180, seg(t, 71.6, 72.0))
    elif t < 76.6:
        fr = face('or_face_shock', t, 74.6, 76.6, 1.25, 1.45, shake=6 * math.exp(-(t - 74.6) * 3))
        fr = fr * (1 - seg(t, 76.1, 76.6))
    else:
        fr = endcard(t)
    # cut softening: 0.12 s dip at every scene change
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * vign()
    if t < .25: fr = fr * seg(t, 0, .25)
    return np.clip(fr, 0, 1)


CUTS = [1.8, 3.2, 8.5, 21.0, 23.6, 27.0, 29.5, 32.0, 35.5, 37.5, 40.0, 51.0, 60.0, 62.5, 70.0, 74.6]


def typed(t, t0, t1, s):
    n = int(len(s) * seg(t, t0, t1)); return s[:n]


def dm_text(t):
    cur = int(t * 2) % 2 == 0
    if t < 52.4: return '', cur
    if t < 54.0: return typed(t, 52.4, 52.8, 'Hi'), cur
    if t < 54.3: return 'Hi'[:max(0, 2 - int((t - 54.0) / .15))], cur
    if t < 55.2: return '', cur
    if t < 58.4: return typed(t, 55.2, 57.4, 'Your dance was so'), cur
    if t < 59.2: s = 'Your dance was so'; return s[:max(0, len(s) - int(len(s) * seg(t, 58.4, 59.2)))], cur
    return '', cur


def dm_text2(t):
    cur = int(t * 2) % 2 == 0
    if t < 70.6: return '', cur
    return typed(t, 70.6, 71.0, 'Hi'), cur


# ---------------------------------------------------------------- audio
def load(path, sr=SR):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()


def place(buf, x, at, gain=1.0, fin=0.0, fout=0.0):
    i = int(at * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i].copy() * gain
    n = len(x)
    if fin: k = min(n, int(fin * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fout: k = min(n, int(fout * SR)); x[n - k:] *= np.linspace(1, 0, k)[:, None]
    buf[i:i + n] += x


def db(x): return 10 ** (x / 20)


SCORE, SCORE_DB = os.environ.get('OR_SCORE', 'score_v5a.mp3'), -4   # v5: one romantic melody piece (v5a violin+piano, v5b flute+santoor); v4: score_v4.mp3
VO = [('v01', .25), ('v02', 4.0), ('v03', 9.0), ('v04', 21.6), ('v05', 29.6), ('v06', 41.2), ('v07', 44.6), ('v08', 55.9), ('v09', 64.0)]


def mix(out):
    N = int(DUR * SR); buf = np.zeros((N, 2), np.float32)
    # score (skip its 1.9 s silent intro), ducked under the voice
    full = load(A + '/' + SCORE)
    sc = np.zeros((int(DUR * SR), 2), np.float32)
    _o = float(os.environ.get('OR_OFF', '0'))
    place(sc, full[int(_o * SR):int((_o + 72.2) * SR)], 0, 1.0, fin=.3, fout=1.2)                 # fades out as he taps Send
    _e = float(os.environ.get('OR_END', '18.0'))
    place(sc, full[int(_e * SR):int((_e + 7.4) * SR)], 76.4, 1.0, fin=.5, fout=2.0)  # the love theme returns on the title card
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR
        a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-5))
    env = np.convolve(env, np.ones(int(.25 * SR)) / int(.25 * SR), mode='same').astype(np.float32)
    sc = sc * env[:, None]
    place(buf, sc, 0, db(SCORE_DB))
    # voice
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    # rain under the room shots
    rn = load(A + '/sfx/rain.mp3')
    for a, b in [(3.2, 8.5), (32.0, 35.5), (37.5, 40.0), (62.5, 70.0)]:
        seg_ = np.tile(rn, (int((b - a) / (len(rn) / SR)) + 2, 1))[:int((b - a + .4) * SR)]
        place(buf, seg_, a - .2, db(-14), fin=.4, fout=.5)
    S = lambda n: load(f'{A}/sfx/{n}')
    for ts in [10.0, 11.6, 13.2]: place(buf, S('swipe.wav'), ts - .05, db(-16))
    place(buf, S('swipe.wav'), 14.4, db(-18))
    place(buf, S('pop.wav'), 28.8, db(-20))                       # replay
    place(buf, S('tap.wav'), 39.9, db(-16)); place(buf, S('tap.wav'), 48.45, db(-14)); place(buf, S('pop.wav'), 48.6, db(-18))
    place(buf, S('tap.wav'), 50.65, db(-14))
    key = S('key.wav')
    for t0, t1, n in [(52.4, 52.8, 2), (55.2, 57.4, 17), (70.6, 71.0, 2)]:
        for i in range(n): place(buf, key, t0 + (t1 - t0) * i / max(1, n - 1), db(-20 + (i % 3)))
    for t0, t1, n in [(54.0, 54.3, 2), (58.4, 59.2, 8)]:
        for i in range(n): place(buf, key, t0 + (t1 - t0) * i / max(1, n - 1), db(-23))
    place(buf, S('tap.wav'), 71.65, db(-14)); place(buf, S('send.wav'), 71.8, db(-12)); place(buf, S('err.wav'), 72.6, db(-10))
    hb = S('heartbeat.mp3'); place(buf, hb[:int(4.0 * SR)], 72.8, db(-6), fin=.3, fout=.8)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), wav],
                   input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_trial_ep01_ml_9x16.mp4')
    ap.add_argument('--audio-only', action='store_true')
    a = ap.parse_args()
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((frame(t) * 255).astype(np.uint8), (270, 480)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f'{t:.1f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 1)
        cols = 8; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)); print('sheet', a.out); return
    wav = mix(a.out)
    if a.audio_only: print('audio', wav); return
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                           '-level', '4.0', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write((frame(i / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', a.out)


if __name__ == '__main__':
    main()
