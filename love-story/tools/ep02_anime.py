"""ഒരു റിപ്ലൈ · Episode 2 "ചുവര്" (The Wall) — anime, vertical 1080x1920, 24 fps, ~85 s.
Reuses Episode 1's phone UI and helpers (ep01.py + ep01_anime.py) and adds: the comment sheet, the collab reel,
the dance page profile and its DM box. Story: love-story/02-scripts.md (Episode 2).
Usage: python3 ep02_anime.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep01_anime as EA   # installs the anime plates / dance clip / avatar into E

W, H, FPS, DUR = E.W, E.H, E.FPS, 85.0
R = '/home/user/Countdown-/love-story/ep02'
AN = EA.AN
font, mlfont, heart, over, tap, ease, seg = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg
PAGE = 'kochi.dance.collective'


# ------------------------------------------------------------------ pictures
@functools.lru_cache(maxsize=None)
def pic(name):
    im = cv2.imread(os.path.join(AN, name + '.jpg'))
    return cv2.resize(im, (int(W * 1.15), int(H * 1.15)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def still(name, t, t0, t1, z0=1.0, z1=1.1, cx=.5, cy=.5, cx1=None, cy1=None, rain=False):
    k = ease(seg(t, t0, t1)); z = z0 + (z1 - z0) * k
    cx1 = cx if cx1 is None else cx1; cy1 = cy if cy1 is None else cy1
    im = pic(name); ih, iw = im.shape[:2]; sc = z / 1.15
    px = (cx + (cx1 - cx) * k) * iw; py = (cy + (cy1 - cy) * k) * ih
    px = min(max(px, W / sc / 2), iw - W / sc / 2); py = min(max(py, H / sc / 2), ih - H / sc / 2)
    M = np.float32([[sc, 0, W / 2 - px * sc], [0, sc, H / 2 - py * sc]])
    fr = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return EA.rain_layer(fr, t, .14) if rain else fr


# ------------------------------------------------------------------ new phone screens
COMMENTS = [('arjun.k_', 'marry me 😍', (200, 90, 90)), ('_meenu', 'ufff that expression!!', (90, 140, 210)),
            ('rahul.r', 'Kochi represent ❤', (90, 170, 110)), ('dance.with.diya', 'teach me this step pls', (200, 150, 60)),
            ('s_n_e_h_a', 'queen 👑', (160, 100, 200)), ('vishnu__', 'goosebumps', (110, 110, 120)),
            ('amalaaa', 'the jasmine 🤍', (220, 120, 160))]


def strip_emoji(s):
    return ''.join(ch for ch in s if ord(ch) < 0x2000).strip()


@functools.lru_cache(maxsize=None)
def comments_ui(typed, cursor, posted):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = 700
    d.rectangle([0, 0, W, top], fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, top, W, H + 40], 40, fill=(28, 28, 31, 255))
    d.rounded_rectangle([490, top + 22, 590, top + 32], 5, fill=(90, 90, 95, 255))
    d.text((540, top + 80), 'Comments', font=font('Bold', 38), fill=(255, 255, 255, 255), anchor='mm')
    d.line([(0, top + 130), (W, top + 130)], fill=(45, 45, 50, 255), width=2)
    rows = ([('aadhi_', '♥', (120, 160, 230))] if posted else []) + COMMENTS
    y = top + 170
    for u, txt, col in rows[:7]:
        d.ellipse([50, y, 130, y + 80], fill=col + (255,))
        d.text((90, y + 40), u[0].upper(), font=font('Bold', 36), fill=(255, 255, 255, 255), anchor='mm')
        d.text((160, y + 6), u, font=font('SemiBold', 30), fill=(230, 230, 235, 255))
        d.text((160 + d.textlength(u, font=font('SemiBold', 30)) + 16, y + 6), 'now' if u == 'aadhi_' else '2h', font=font('Regular', 28), fill=(140, 140, 145, 255))
        if txt == '♥':
            heart(d, 182, y + 62, 18, fill=(245, 245, 250, 255), outline=(245, 245, 250, 255), w=2)
        else:
            d.text((160, y + 44), strip_emoji(txt), font=font('Regular', 32), fill=(245, 245, 250, 255))
        heart(d, W - 80, y + 40, 18)
        y += 128
    # input bar
    yb = 1700
    d.rectangle([0, yb - 30, W, H], fill=(28, 28, 31, 255))
    d.ellipse([40, yb, 120, yb + 80], fill=(120, 160, 230, 255)); d.text((80, yb + 40), 'A', font=font('Bold', 34), fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle([140, yb, W - 40, yb + 80], 40, outline=(70, 70, 75, 255), width=2)
    if typed == '♥':
        heart(d, 190, yb + 40, 18, fill=(245, 245, 250, 255), outline=(245, 245, 250, 255), w=2); tw = 40
    elif typed:
        f = font('Regular', 32); s = typed
        while d.textlength(s, font=f) > W - 330: s = s[1:]
        d.text((170, yb + 40), s, font=f, fill=(245, 245, 250, 255), anchor='lm'); tw = d.textlength(s, font=f)
    else:
        d.text((170, yb + 40), 'Add a comment for manjusha.dances…', font=font('Regular', 30), fill=(130, 130, 135, 255), anchor='lm'); tw = 0
    if cursor: d.line([(174 + tw, yb + 18), (174 + tw, yb + 62)], fill=(56, 151, 240, 255), width=4)
    if typed: d.text((W - 80, yb + 40), 'Post', font=font('SemiBold', 32), fill=(56, 151, 240, 255), anchor='rm')
    return im


@functools.lru_cache(maxsize=None)
def page_logo(size):
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=(214, 120, 60, 255))
    d.ellipse([size * .1, size * .1, size * .9, size * .9], outline=(255, 236, 200, 255), width=max(2, size // 30))
    d.text((size / 2, size / 2), 'KDC', font=font('Bold', int(size * .3)), fill=(255, 246, 228, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def collab_ui():
    """reel UI with the collab header: two avatars + 'manjusha.dances and kochi.dance.collective'."""
    im = E.reel_ui('manjusha.dances', None, False, 'rooftop night with @' + PAGE, '61.4K', '1,822', 'nila').copy()
    d = ImageDraw.Draw(im)
    d.rectangle([150, 1640, W, 1730], fill=(0, 0, 0, 0))
    g = np.asarray(im).copy(); g[1640:1730, 140:W] = 0; im = Image.fromarray(g, 'RGBA'); d = ImageDraw.Draw(im)
    im.alpha_composite(page_logo(70), (110, 1650)); d = ImageDraw.Draw(im)
    E.shadow_text(d, (196, 1662), 'manjusha.dances', font('SemiBold', 32))
    tw = d.textlength('manjusha.dances', font=font('SemiBold', 32))
    E.shadow_text(d, (196 + tw + 12, 1664), 'and', font('Regular', 30))
    E.shadow_text(d, (196, 1700), PAGE, font('SemiBold', 32))
    return im


@functools.lru_cache(maxsize=None)
def page_ui(hl):
    im = Image.new('RGBA', (W, H), (12, 12, 14, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:31', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 150), (84, 126), (60, 150), (84, 174)], fill=(255, 255, 255, 255), width=6)
    d.text((120, 150), PAGE, font=font('Bold', 42), fill=(255, 255, 255, 255), anchor='lm')
    im.alpha_composite(page_logo(216), (64, 244)); d = ImageDraw.Draw(im)
    for i, (n, lab) in enumerate([('186', 'posts'), ('40.2K', 'followers'), ('312', 'following')]):
        cx = 470 + i * 210
        d.text((cx, 322), n, font=font('Bold', 46), fill=(255, 255, 255, 255), anchor='mm')
        d.text((cx, 380), lab, font=font('Regular', 30), fill=(220, 220, 220, 255), anchor='mm')
    d.text((60, 520), 'Kochi Dance Collective', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((60, 574), 'Community', font=font('Regular', 32), fill=(160, 160, 165, 255))
    d.text((60, 622), "Kochi's dancers · collabs & features", font=font('Regular', 34), fill=(255, 255, 255, 255))
    d.text((60, 670), 'DM to collab', font=font('Regular', 34), fill=(255, 255, 255, 255))
    d.rounded_rectangle([60, 760, 520, 850], 18, fill=(0, 149, 246, 255))
    d.text((290, 805), 'Follow', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    col = (80, 80, 88, 255) if hl else (54, 54, 58, 255)
    d.rounded_rectangle([540, 760, 1020, 850], 18, fill=col)
    if hl: d.rounded_rectangle([540, 760, 1020, 850], 18, outline=(120, 190, 255, 255), width=4)
    d.text((780, 805), 'Message', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    d.line([(0, 900), (W, 900)], fill=(40, 40, 44, 255), width=2)
    keys = ['manjusha_dance', 'manjusha_portrait', 'manjusha_reading', 'manjusha_sunrise', 'manjusha_dance', 'manjusha_portrait']
    for i, k in enumerate(keys):
        c, r = i % 3, i // 3
        x0, y0, tw_, th = c * 361, 1020 + r * 482, 358, 478
        src = cv2.imread(os.path.join(AN, k + '.jpg'))
        h_, w_ = src.shape[:2]; crop = src[int(h_ * .1):int(h_ * .1) + int(w_ * th / tw_), :]
        crop = cv2.resize(crop, (tw_, th), interpolation=cv2.INTER_AREA)
        if i % 2: crop = cv2.convertScaleAbs(crop, alpha=.9, beta=-8)
        im.paste(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)), (x0, y0)); d = ImageDraw.Draw(im)
    return im


@functools.lru_cache(maxsize=None)
def page_dm_ui(cursor):
    im = Image.new('RGBA', (W, H), (12, 12, 14, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:32', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    im.alpha_composite(page_logo(80), (110, 120)); d = ImageDraw.Draw(im)
    d.text((210, 138), 'Kochi Dance Collective', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((210, 186), PAGE, font=font('Regular', 28), fill=(160, 160, 165, 255))
    d.line([(0, 240), (W, 240)], fill=(32, 32, 36, 255), width=2)
    im.alpha_composite(page_logo(220), (430, 420)); d = ImageDraw.Draw(im)
    d.text((540, 690), 'Kochi Dance Collective', font=font('Bold', 44), fill=(255, 255, 255, 255), anchor='mm')
    d.text((540, 744), PAGE + ' · Instagram', font=font('Regular', 30), fill=(160, 160, 165, 255), anchor='mm')
    d.text((540, 790), '40.2K followers · 186 posts', font=font('Regular', 30), fill=(160, 160, 165, 255), anchor='mm')
    y = 1130
    d.rounded_rectangle([40, y, W - 40, y + 100], 50, fill=(38, 38, 42, 255))
    d.ellipse([56, y + 14, 128, y + 86], fill=(56, 151, 240, 255)); d.rectangle([80, y + 38, 104, y + 62], outline=(255, 255, 255, 255), width=4)
    d.text((150, y + 50), 'Message...', font=font('Regular', 38), fill=(150, 150, 155, 255), anchor='lm')
    if cursor: d.line([(150, y + 26), (150, y + 74)], fill=(56, 151, 240, 255), width=5)
    d.rectangle([0, 1270, W, H], fill=(30, 30, 33, 255))
    for r, keys in enumerate(['qwertyuiop', 'asdfghjkl', 'zxcvbnm']):
        n = len(keys); kw = 96; x0 = (W - n * (kw + 8)) / 2
        for i, k in enumerate(keys):
            x = x0 + i * (kw + 8); yy = 1300 + r * 140
            d.rounded_rectangle([x, yy, x + kw, yy + 120], 12, fill=(70, 70, 75, 255))
            d.text((x + kw / 2, yy + 60), k, font=font('Regular', 46), fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle([250, 1720, 830, 1840], 12, fill=(70, 70, 75, 255))
    d.text((540, 1780), 'space', font=font('Regular', 38), fill=(230, 230, 230, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 2', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'ചുവര്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank():
    return np.zeros((H, W, 3), np.float32)


def typed(t, t0, t1, s):
    return s[:int(len(s) * seg(t, t0, t1))]


LONG = 'Your dance was so beautiful, I watched it at 2 am like 20 times and'


def other_reel_img(k):
    im = cv2.imread(os.path.join(AN, k + '.jpg'))
    return cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


def frame(t):
    if t < 2.2:      # HOOK: the wall
        fr = over(blank(), E.dm_ui('', False, 'Hi', True, True))
        for tt in (.3, .8, 1.3, 1.8): fr = tap(fr, W - 140, 1180, seg(t, tt, tt + .35))
    elif t < 6.5:
        fr = still('e2_busstop', t, 2.2, 6.5, 1.0, 1.1, .55, .5, .6, .45, rain=True)
    elif t < 10.0:
        fr = still('e2_busstop_cu', t, 6.5, 10.0, 1.0, 1.12, .5, .5, rain=True)
    elif t < 15.0:   # her new reel
        fr = E.reel(t, t - 10, .1 + .03 * (t - 10))
        if t > 14.4: fr = tap(fr, 990, 1325, seg(t, 14.4, 14.8))
    elif t < 24.0:   # comments
        fr = E.nila_content(t) ; fr = over(fr, E.reel_ui('manjusha.dances', False, False, 'terrace nights & old songs', '61.4K', '1,822', 'nila'))
        cur = int(t * 2) % 2 == 0
        if t < 18.4: txt, posted = '', False
        elif t < 21.0: txt, posted = typed(t, 18.4, 20.9, LONG), False
        elif t < 22.0: txt, posted = LONG[:max(0, len(LONG) - int(len(LONG) * seg(t, 21.0, 21.9)))], False
        elif t < 23.2: txt, posted = ('♥' if t > 22.4 else ''), False
        else: txt, posted = '', True
        k = ease(seg(t, 15.0, 15.5))
        sheet = np.asarray(comments_ui(txt, cur and t < 23.2, posted), np.float32) / 255
        if k < 1:
            dy = int((1 - k) * 1300); sheet = np.concatenate([np.zeros((dy, W, 4), np.float32), sheet[:H - dy]], 0)
        a = sheet[..., 3:4]; fr = fr * (1 - a) + sheet[..., [2, 1, 0]] * a
        if 22.9 < t < 23.4: fr = tap(fr, W - 120, 1740, seg(t, 22.9, 23.3))
    elif t < 28.0:
        fr = still('e2_busstop_cu', t, 24.0, 28.0, 1.15, 1.25, .5, .42, rain=True)
    elif t < 33.5:
        fr = still('e2_teashop', t, 28.0, 33.5, 1.0, 1.08, .5, .45)
    elif t < 38.0:
        fr = still('e2_kiran_cu', t, 33.5, 38.0, 1.0, 1.1, .5, .4)
    elif t < 46.0:
        fr = still('e2_aadhi_tea', t, 38.0, 46.0, 1.0, 1.12, .55, .45, .6, .4)
    elif t < 52.0:
        fr = still('aadhi_214am', t, 46.0, 52.0, 1.0, 1.15, .5, .5, .6, .58, rain=True)
    elif t < 58.0:   # scrolling her older reels
        keys = ['manjusha_portrait', 'manjusha_reading', 'manjusha_sunrise']
        i = min(2, int((t - 52.0) / 2.0)); lt = (t - 52.0) - i * 2.0
        fr = other_reel_img(keys[i])
        if lt > 1.65 and i < 2:
            k = ease(seg(lt, 1.65, 2.0)); dy = int(H * k)
            nx = other_reel_img(keys[i + 1]); fr = np.concatenate([fr[dy:], nx[:dy]], 0)
        fr = over(fr, E.reel_ui('manjusha.dances', None, False, 'old reels · 2025', '88K', '2,140', 'nila'))
    elif t < 63.0:   # the collab reel
        fr = over(E.nila_content(t), collab_ui())
        p = .5 + .5 * math.sin((t - 58) * 5)
        if t > 59.5:
            hl = np.zeros((H, W, 3), np.float32); cv2.rectangle(hl, (186, 1690), (190 + 470, 1742), (1, .85, .5), 4); fr = np.clip(fr + hl * .6 * p, 0, 1)
    elif t < 66.0:
        fr = still('e2_curious', t, 63.0, 66.0, 1.05, 1.2, .5, .5)
    elif t < 71.0:
        fr = over(blank(), page_ui(t > 69.8))
        fr = tap(fr, 780, 805, seg(t, 70.2, 70.7))
    elif t < 74.0:
        fr = over(blank(), page_dm_ui(int(t * 2) % 2 == 0))
    elif t < 79.0:
        fr = still('e2_hopeful', t, 74.0, 79.0, 1.0, 1.15, .5, .55, .55, .6, rain=True)
        fr = fr * (1 - seg(t, 78.4, 79.0))
    else:
        lt = t - 79.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 2.4 else 0)) * seg(lt, 0, .8) * (1 - seg(lt, 5.4, 6.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .2: fr = fr * seg(t, 0, .2)
    return np.clip(fr, 0, 1)


CUTS = [2.2, 6.5, 10.0, 24.0, 28.0, 33.5, 38.0, 46.0, 52.0, 58.0, 63.0, 66.0, 71.0, 74.0]

VO = [('a1', 2.6), ('a2', 15.6), ('k1', 28.6), ('a3', 38.9), ('a4', 63.4), ('a5', 74.6)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-5))
    env = np.convolve(env, np.ones(int(.25 * SR)) / int(.25 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.5), fin=.3, fout=2.0)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    rn = load(E.A + '/sfx/rain.mp3')
    for a, b in [(2.2, 10.0), (24.0, 28.0), (46.0, 52.0), (74.0, 79.0)]:
        seg_ = np.tile(rn, (int((b - a) / (len(rn) / SR)) + 2, 1))[:int((b - a + .4) * SR)]
        place(buf, seg_, a - .2, db(-15), fin=.4, fout=.5)
    for tt in (.3, .8, 1.3, 1.8): place(buf, S('tap.wav'), tt, db(-13))
    place(buf, S('err.wav'), 1.9, db(-11))
    place(buf, S('tap.wav'), 14.45, db(-15)); place(buf, S('swipe.wav'), 15.0, db(-20))
    key = S('key.wav')
    for i in range(24): place(buf, key, 18.4 + 2.5 * i / 23, db(-21 + (i % 3)))
    for i in range(8): place(buf, key, 21.0 + .9 * i / 7, db(-24))
    place(buf, key, 22.4, db(-20)); place(buf, S('tap.wav'), 22.95, db(-14)); place(buf, S('pop.wav'), 23.2, db(-17))
    for ts in (53.65, 55.65): place(buf, S('swipe.wav'), ts, db(-20))
    place(buf, S('tap.wav'), 70.25, db(-14)); place(buf, S('pop.wav'), 71.0, db(-19))
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep02_anime_ml_9x16.mp4')
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
