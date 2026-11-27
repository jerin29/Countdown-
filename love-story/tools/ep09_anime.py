"""ഒരു റിപ്ലൈ · Episode 9 "ഇഷ്ടം കൊണ്ട്" (What He Does With the Love) — anime, vertical, ~84 s.
He turns the feeling into reels: 23 views, every night, comments, one reel takes off — 1M.
Usage: python3 ep09_anime.py [--sheet t,..] [--out f.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2
import ep06_anime as E6
import ep08_anime as E8

W, H, FPS, DUR = E.W, E.H, E.FPS, 84.0
R = '/home/user/Countdown-/love-story/ep09'
AN = E2.AN
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
ME = 'aadhi.2am'


def fmt(n):
    if n >= 995_000: n = max(n, 1_000_000)
    if n >= 1_000_000: return f'{n / 1e6:.1f}M'.replace('.0M', 'M')
    if n >= 100_000: return f'{n // 1000}K'
    if n >= 1000: return f'{n / 1000:.1f}K'.replace('.0K', 'K')
    return str(n)


@functools.lru_cache(maxsize=None)
def my_reel_ui(likes, title):
    im = E.reel_ui(ME, None, False, '2:14 AM thoughts', likes, '0' if likes == '4' else fmt(int(float(likes.rstrip('KM')) * (1000 if 'K' in likes else 1e6 if 'M' in likes else 1)) // 40), None).copy()
    im.alpha_composite(E6.face('aadhi_smile', (300, 500, 900, 1100), 84), (50, 1636))
    if title:
        d = ImageDraw.Draw(im)
        for dx, dy, c in [(3, 4, (0, 0, 0, 170)), (0, 0, (255, 240, 220, 255))]:
            d.text((540 + dx, 760 + dy), 'ചില ഇഷ്ടങ്ങൾ', font=mlfont('Bold', 110), fill=c, anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def views_ui(n):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = fmt(n) + ' views'; f = font('Bold', 64); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([540 - tw / 2 - 110, 240, 540 + tw / 2 + 50, 360], 60, fill=(15, 15, 20, 210))
    x = 540 - tw / 2 - 60
    d.polygon([(x - 18, 275), (x - 18, 325), (x + 22, 300)], fill=(255, 255, 255, 255))
    d.text((540 + 30, 300), txt, font=f, fill=(255, 255, 255, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def day_ui(n):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = f'ദിവസം {n}'; f = mlfont('Bold', 56); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([540 - tw / 2 - 40, 210, 540 + tw / 2 + 40, 310], 50, fill=(15, 15, 20, 200))
    d.text((540, 260), txt, font=f, fill=(255, 225, 170, 255), anchor='mm')
    return im


COMMENTS = [('meera_k', 'This is me at 2 AM :(', 'l'), ('_arjun.r', 'എനിക്കും ഇങ്ങനെ ഒരാൾ ഉണ്ടായിരുന്നു', 'm'),
            ('anju.p', 'Ee feel... ufff', 'l'), ('night.owl.kochi', '2:14 AM gang', 'l'),
            ('rahul_s', 'ഇത് ഞാൻ തന്നെ ആണ്', 'm'), ('devika', 'Who hurt you bro :)', 'l'), ('aswin.k', 'ചില ഇഷ്ടങ്ങൾ… sathyam', 'm')]


@functools.lru_cache(maxsize=None)
def comments_ui(n):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 520, W, H + 40], 40, fill=(24, 24, 28, 250))
    d.rounded_rectangle([490, 545, 590, 555], 5, fill=(90, 90, 96, 255))
    d.text((540, 600), 'Comments', font=font('Bold', 38), fill=(255, 255, 255, 255), anchor='mm')
    y = 680
    for i, (u, c, s) in enumerate(COMMENTS[:n]):
        col = [(120, 90, 160), (90, 140, 120), (170, 110, 80), (80, 120, 170), (150, 80, 110)][i % 5]
        d.ellipse([50, y, 130, y + 80], fill=col + (255,)); d.text((90, y + 40), u.strip('_.')[0].upper(), font=font('Bold', 38), fill=(255, 255, 255, 255), anchor='mm')
        d.text((156, y + 2), u, font=font('SemiBold', 30), fill=(200, 200, 205, 255))
        d.text((156, y + 42), c, font=mlfont('Regular', 36) if s == 'm' else font('Regular', 36), fill=(255, 255, 255, 255))
        heart(d, W - 80, y + 40, 18, fill=None, outline=(170, 170, 175, 255), w=3)
        y += 150
    return im


@functools.lru_cache(maxsize=None)
def notif_ui():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 40, W - 40, 220], 36, fill=(245, 245, 248, 240))
    d.ellipse([70, 80, 166, 176], fill=(200, 200, 206, 255))
    d.text((190, 86), 'Instagram · now', font=font('Regular', 28), fill=(90, 90, 96, 255))
    d.rounded_rectangle([190, 128, 700, 152], 12, fill=(170, 170, 176, 255))
    d.rounded_rectangle([190, 166, 560, 186], 10, fill=(200, 200, 206, 255))
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 9', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'ഇഷ്ടം കൊണ്ട്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank(): return np.zeros((H, W, 3), np.float32)


def city(t, t0, t1, z0=1.0, z1=1.12):
    return still('city_night', t, t0, t1, z0, z1, .5, .5, rain=True)


def climb(t, t0, t1, a, b):
    k = ease(seg(t, t0, t1)); return int(a * (b / a) ** k) if a > 0 else int(b * k)


def frame(t):
    if t < 2.5:          # HOOK: his own reel, the count racing 1 → 100K
        fr = over(city(t, 0, 2.5, 1.1, 1.2), my_reel_ui('12K', True))
        fr = over(fr, views_ui(climb(t, .1, 2.3, 1, 100_000)))
    elif t < 12.0:
        fr = still('e9_filming', t, 2.5, 12.0, 1.0, 1.15, .45, .45, .4, .4, rain=True)
    elif t < 16.0:
        fr = over(city(t, 12, 16), my_reel_ui('4', False)); fr = over(fr, views_ui(climb(t, 12.2, 13.5, 1, 23)))
    elif t < 22.0:
        fr = still('e3_kiranlaugh', t, 16.0, 22.0, 1.0, 1.12, .45, .45)
    elif t < 40.0:       # montage: every night he creates
        if t < 28: fr = still('e9_editing', t, 22, 28, 1.0, 1.12, .4, .6); n = 1
        elif t < 32: fr = still('e8_record', t, 28, 32, 1.05, 1.2, .45, .5); n = 12
        elif t < 36: fr = still('e9_filming', t, 32, 36, 1.3, 1.45, .3, .45, rain=True); n = 30
        else: fr = still('e9_editing', t, 36, 40, 1.35, 1.5, .25, .62); n = 47
        fr = over(fr, day_ui(n))
    elif t < 54.0:       # comments start coming
        base = over(city(t, 40, 54, 1.0, 1.05), my_reel_ui('2.4K', False))
        fr = over(base, comments_ui(min(len(COMMENTS), 1 + int((t - 40.6) / 1.7)) if t > 40.6 else 0))
    elif t < 66.0:       # "ചില ഇഷ്ടങ്ങൾ" takes off
        lk = climb(t, 54.5, 65.5, 1200, 870_000)
        fr = over(city(t, 54, 66, 1.0, 1.15), my_reel_ui(fmt(max(1000, lk // 9)), True))
        fr = over(fr, views_ui(lk))
    elif t < 70.0:
        fr = still('e9_proud', t, 66.0, 70.0, 1.05, 1.2, .5, .5)
    elif t < 72.5:       # the one screenshot he kept
        th = cv2.cvtColor(np.asarray(E8.thumb(0).resize((560, 995))), cv2.COLOR_RGB2BGR).astype(np.float32) / 255
        fr = blank(); fr[460:1455, 260:820] = th
    elif t < 75.0:
        fr = still('e9_proud', t, 72.5, 75.0, 1.3, 1.45, .48, .45)
    elif t < 79.0:       # 1M — and a notification he can't see yet
        n = climb(t, 75.0, 77.0, 870_000, 1_000_000)
        fr = over(city(t, 75, 79, 1.15, 1.25), my_reel_ui('94K', True)); fr = over(fr, views_ui(n))
        if t > 77.4:
            k = ease(seg(t, 77.4, 77.9)); o = over(blank(), notif_ui())
            M = np.float32([[1, 0, 0], [0, 1, -260 * (1 - k)]]); o = cv2.warpAffine(o, M, (W, H))
            mask = (o.sum(axis=2, keepdims=True) > 0).astype(np.float32); fr = fr * (1 - mask) + o * mask
        fr = fr * (1 - seg(t, 78.6, 79.0))
    else:
        lt = t - 79.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, .2, .8) * (1 - seg(lt, 4.4, 5.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .15: fr = fr * seg(t, 0, .15)
    return np.clip(fr, 0, 1)


CUTS = [2.5, 12.0, 16.0, 22.0, 28.0, 32.0, 36.0, 40.0, 54.0, 66.0, 70.0, 72.5, 75.0]
VO = [('a1', 4.0), ('k1', 16.4), ('a_poda', 21.1), ('a2', 67.2)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-6))
    a_, b_ = int(78.95 * SR), int(79.3 * SR); env[a_:b_] = 0.0       # the cut on the notification
    env = np.convolve(env, np.ones(int(.05 * SR)) / int(.05 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.5), fin=.1, fout=1.0)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    for i in range(7): place(buf, S('pop.wav'), 40.7 + i * 1.7, db(-16))
    place(buf, S('pop.wav'), 77.45, db(-8))
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_ in [(2.5, 16.0)]:
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(-17), fin=.4, fout=.6)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep09_anime_ml_9x16.mp4')
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
