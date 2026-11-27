"""ഒരു റിപ്ലൈ · Episode 3 "കൊളാബ് പേജ്" (The Collab Page) — anime, vertical, ~82 s.
Based on the creator's real message to a collab page (name/college/place changed). Reuses ep01/ep02 helpers.
Usage: python3 ep03_anime.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2

W, H, FPS, DUR = E.W, E.H, E.FPS, 82.0
R = '/home/user/Countdown-/love-story/ep03'
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
PAGE = E2.PAGE

# the message, line by line (emoji written as text faces, the way they look typed)
MSG = ['Hai', 'I am Aadhi', 'Shorts oke kollaam chechi :)', 'Chechi aano atho same age aano ennu ariyilla',
       'Instagramil aayalum YouTubeil aayalum njan message um comment um ittu, onnum kandilla',
       'Enthenkilum kaanum ennu vishwasathode...', 'A good friend, Aadhi', 'An anonymous person', 'A big fan',
       'Meet cheyyan thaalparyam und', 'You treat me :D :D', 'I want appreciate you. If you see message plz reply me']
TYPE_T0, TYPE_T1 = 8.0, 31.5


def wrap(d, text, f, maxw):
    out = []
    for para in text.split('\n'):
        words, line = para.split(' '), ''
        for w_ in words:
            t = (line + ' ' + w_).strip()
            if d.textlength(t, font=f) <= maxw: line = t
            else: out.append(line); line = w_
        out.append(line)
    return out


@functools.lru_cache(maxsize=None)
def compose_ui(text, cursor, state):
    """the page's DM screen. state: 'typing' | 'sent' | 'delivered'"""
    im = E2.page_dm_ui(False).copy(); d = ImageDraw.Draw(im)
    f = font('Regular', 34)
    if state == 'typing':
        d.rectangle([0, 250, W, 1125], fill=(12, 12, 14, 255))   # hide the empty-chat header art while composing
        lines = wrap(d, text, f, W - 230)[-15:] if text else []
        top = max(300, 1110 - len(lines) * 50 - 40)
        d.rounded_rectangle([40, top, W - 40, 1230], 36, fill=(38, 38, 42, 255))
        d.ellipse([56, 1144, 128, 1216], fill=(56, 151, 240, 255)); d.rectangle([80, 1168, 104, 1192], outline=(255, 255, 255, 255), width=4)
        y = top + 30
        for ln in lines:
            d.text((150, y), ln, font=f, fill=(255, 255, 255, 255)); y += 50
        if cursor:
            lx = 150 + (d.textlength(lines[-1], font=f) if lines else 0); ly = y - 50 if lines else top + 30
            d.line([(lx + 4, ly + 4), (lx + 4, ly + 44)], fill=(56, 151, 240, 255), width=4)
        if text: d.text((W - 80, 1180), 'Send', font=font('SemiBold', 36), fill=(56, 151, 240, 255), anchor='rm')
        d.rectangle([0, 1240, W, 1270], fill=(12, 12, 14, 255))
    else:
        d.rectangle([0, 250, W, 1125], fill=(12, 12, 14, 255))
        lines = wrap(d, text, font('Regular', 30), W - 330)
        bh = len(lines) * 42 + 50; top = 1080 - bh
        d.rounded_rectangle([200, top, W - 50, 1080], 40, fill=(120, 60, 230, 255))
        y = top + 26
        for ln in lines: d.text((230, y), ln, font=font('Regular', 30), fill=(255, 255, 255, 255)); y += 42
        if state == 'delivered': d.text((W - 60, 1100), 'Delivered', font=font('Regular', 28), fill=(150, 150, 155, 255), anchor='ra')
    return im


@functools.lru_cache(maxsize=None)
def lock_notif():
    """lock screen with the page's notification."""
    bg = cv2.imread(os.path.join(E2.AN, 'aadhi_214am.jpg')); bg = cv2.resize(bg, (W, H)); bg = cv2.GaussianBlur(bg, (0, 0), 28)
    bg = (bg.astype(np.float32) * .45).astype(np.uint8)
    im = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert('RGBA'); d = ImageDraw.Draw(im)
    d.text((540, 300), '2:16', font=font('Bold', 190), fill=(235, 238, 245, 255), anchor='mm')
    d.text((540, 430), 'Wednesday', font=font('Medium', 44), fill=(220, 224, 232, 255), anchor='mm')
    d.rounded_rectangle([50, 760, W - 50, 1000], 40, fill=(245, 245, 248, 235))
    im.alpha_composite(E2.page_logo(90), (80, 790)); d = ImageDraw.Draw(im)
    d.text((196, 800), 'Instagram · now', font=font('Regular', 28), fill=(90, 90, 96, 255))
    d.text((196, 842), PAGE, font=font('Bold', 34), fill=(20, 20, 24, 255))
    d.text((196, 892), 'We showed her your message :)', font=font('Regular', 34), fill=(30, 30, 36, 255))
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 3', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'കൊളാബ് പേജ്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


FULL = '\n'.join(MSG)
N = len(FULL)


def typed_text(t):
    if t < TYPE_T0: return ''
    k = seg(t, TYPE_T0, TYPE_T1)
    return FULL[:int(N * k)]


def blank(): return np.zeros((H, W, 3), np.float32)


def frame(t):
    cur = int(t * 2) % 2 == 0
    if t < 2.0:          # HOOK: the whole message, thumb over Send
        fr = over(blank(), compose_ui(FULL, False, 'typing'))
        fr = tap(fr, W - 140, 1180, seg(t, 1.2, 1.8))
    elif t < 8.0:
        fr = still('aadhi_hesitant', t, 2.0, 8.0, 1.0, 1.15, .5, .5, .55, .45)
    elif t < 26.5:
        fr = over(blank(), compose_ui(typed_text(t), cur, 'typing'))
    elif t < 32.0:
        fr = still('e3_laughself', t, 26.5, 32.0, 1.05, 1.2, .55, .6)
    elif t < 34.5:       # "but this is me": the full message, about to send
        fr = over(blank(), compose_ui(FULL, cur, 'typing'))
        fr = tap(fr, W - 140, 1180, seg(t, 34.0, 34.5))
    elif t < 37.0:
        fr = over(blank(), compose_ui(FULL.replace('\n', ' · '), False, 'delivered' if t > 35.4 else 'sent'))
    elif t < 44.0:
        fr = still('e3_pillow', t, 37.0, 44.0, 1.0, 1.1, .5, .55, .45, .6, rain=True)
    elif t < 48.0:
        fr = still('e3_class_hope', t, 44.0, 48.0, 1.0, 1.08, .5, .5)
    elif t < 52.0:
        fr = still('e3_class_sad', t, 48.0, 52.0, 1.0, 1.08, .5, .5)
    elif t < 56.0:
        fr = still('aadhi_back', t, 52.0, 56.0, 1.05, 1.18, .6, .6, rain=True)
    elif t < 64.0:
        fr = still('e3_kiranlaugh', t, 56.0, 64.0, 1.0, 1.1, .45, .45, .55, .5)
    elif t < 70.0:
        sh = 6 * math.sin(t * 90) if 66.0 < t < 67.6 else 0
        fr = still('e3_buzz', t, 64.0, 70.0, 1.0, 1.12, .5, .65)
        if sh: fr = cv2.warpAffine(fr, np.float32([[1, 0, sh], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    elif t < 73.0:
        fr = over(blank(), lock_notif()) * ease(seg(t, 70.0, 70.4))
    elif t < 76.0:
        fr = still('aadhi_wonder', t, 73.0, 76.0, 1.1, 1.3, .55, .45)
        fr = fr * (1 - seg(t, 75.5, 76.0))
    else:
        lt = t - 76.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 2.4 else 0)) * seg(lt, 0, .8) * (1 - seg(lt, 5.4, 6.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .2: fr = fr * seg(t, 0, .2)
    return np.clip(fr, 0, 1)


CUTS = [2.0, 8.0, 26.5, 32.0, 34.5, 37.0, 44.0, 48.0, 52.0, 56.0, 64.0, 70.0, 73.0]
VO = [('a1', 2.5), ('a2', 27.0), ('a3', 32.2), ('k1', 56.6), ('a4', 61.8), ('a5', 73.4)]


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
    for a, b in [(2.0, 8.0), (37.0, 44.0), (52.0, 56.0), (64.0, 70.0)]:
        seg_ = np.tile(rn, (int((b - a) / (len(rn) / SR)) + 2, 1))[:int((b - a + .4) * SR)]
        place(buf, seg_, a - .2, db(-16), fin=.4, fout=.5)
    key = S('key.wav')
    n_keys = 70
    for i in range(n_keys):
        tt = TYPE_T0 + (26.5 - TYPE_T0) * i / n_keys
        place(buf, key, tt, db(-22 + (i % 3)))
    place(buf, S('tap.wav'), 1.25, db(-14)); place(buf, S('tap.wav'), 34.05, db(-13)); place(buf, S('send.wav'), 34.5, db(-11))
    hum = S('err.wav')
    for tt in (66.0, 66.5, 67.0): place(buf, S('tap2.wav'), tt, db(-8))      # phone buzz knocks
    place(buf, S('pop.wav'), 70.0, db(-12))
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep03_anime_ml_9x16.mp4')
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
