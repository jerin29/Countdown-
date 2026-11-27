"""ഒരു റിപ്ലൈ · Episode 6 "സമ്മാനം" (The Gift) — told from HER side. anime, vertical, ~84 s.
The same "romantic" act seen as frightening by the person who receives it. No love theme in this episode.
Usage: python3 ep06_anime.py [--sheet t,..] [--out f.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2

W, H, FPS, DUR = E.W, E.H, E.FPS, 84.0
R = '/home/user/Countdown-/love-story/ep06'
AN = E2.AN
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
SEARCH = 'aadhi'


@functools.lru_cache(maxsize=None)
def face(name, box, size):
    im = cv2.imread(os.path.join(AN, name + '.jpg'))
    x0, y0, x1, y1 = box; im = cv2.resize(im[y0:y1, x0:x1], (size, size), interpolation=cv2.INTER_AREA)
    p = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).convert('RGBA')
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    p.putalpha(m); return p


@functools.lru_cache(maxsize=None)
def inbox_ui(n_typed, found):
    """her message search: she types his name and finds the chat."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '11:48', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    d.text((120, 160), 'manjusha.dances', font=font('Bold', 42), fill=(255, 255, 255, 255), anchor='lm')
    d.rounded_rectangle([40, 240, W - 40, 330], 22, fill=(38, 38, 42, 255))
    d.ellipse([70, 266, 110, 306], outline=(160, 160, 165, 255), width=4); d.line([(104, 300), (122, 318)], fill=(160, 160, 165, 255), width=5)
    txt = SEARCH[:n_typed]
    d.text((140, 285), txt if txt else 'Search', font=font('Regular', 38), fill=(255, 255, 255, 255) if txt else (150, 150, 155, 255), anchor='lm')
    if txt and not found:
        tw = d.textlength(txt, font=font('Regular', 38)); d.line([(144 + tw, 262), (144 + tw, 308)], fill=(56, 151, 240, 255), width=4)
    if not txt:      # ordinary inbox before she searches
        rows = [('Messages', None), ('kochi.dance.collective', 'Thank you for the collab! See you…'), ('anju_r', 'Ufff that reel 🔥'.replace('🔥', ':)')),
                ('meera.k', 'Sent a reel'), ('dance.class.kochi', 'Saturday practice at 5?'), ('_arun.v', 'Congrats chechi!')]
    else:
        rows = [('Accounts', None), ('aadhi_', "Thank you for replying! You don't kn…")]
        if n_typed < len(SEARCH): rows += [('aadhira.s', 'aadhira · 2 mutual'), ('aadhil_photography', 'aadhil · Photographer')]
    y = 380
    for i, (name, prev) in enumerate(rows):
        if prev is None:
            d.text((60, y + 10), name, font=font('Bold', 36), fill=(255, 255, 255, 255)); y += 80; continue
        if found and name == 'aadhi_': d.rectangle([0, y - 14, W, y + 120], fill=(40, 40, 48, 255))
        if name == 'aadhi_': im.alpha_composite(face('aadhi_smile', (300, 500, 900, 1100), 104), (50, y)); d = ImageDraw.Draw(im)
        elif name == 'kochi.dance.collective': im.alpha_composite(E2.page_logo(104), (50, y)); d = ImageDraw.Draw(im)
        else:
            col = [(120, 90, 160), (90, 140, 120), (170, 110, 80), (80, 120, 170), (150, 80, 110)][i % 5]
            d.ellipse([50, y, 154, y + 104], fill=col + (255,)); d.text((102, y + 52), name.strip('_.')[0].upper(), font=font('Bold', 44), fill=(255, 255, 255, 255), anchor='mm')
        d.text((180, y + 14), name, font=font('SemiBold', 36), fill=(255, 255, 255, 255))
        d.text((180, y + 62), prev, font=font('Regular', 30), fill=(160, 160, 165, 255))
        y += 150
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 6', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'സമ്മാനം', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank(): return np.zeros((H, W, 3), np.float32)


def cold(fr, k):
    """drain warmth: pull towards a cool desaturated grade."""
    g = fr.mean(axis=2, keepdims=True)
    c = fr * (1 - .5 * k) + g * .5 * k
    return c * np.array([1 + .08 * k, 1, 1 - .1 * k], np.float32)    # BGR: more blue, less red


def frame(t):
    if t < 2.5:
        fr = still('e6_letter', t, 0, 2.5, 1.35, 1.12, .5, .55)
    elif t < 11.0:
        fr = still('e6_courier', t, 2.5, 11.0, 1.0, 1.12, .55, .5, .6, .45)
    elif t < 19.0:
        fr = still('e6_opening', t, 11.0, 19.0, 1.0, 1.15, .45, .6, .4, .62)
    elif t < 27.0:
        fr = cold(still('e6_letter', t, 19.0, 27.0, 1.0, 1.25, .45, .55), seg(t, 21, 27))
    elif t < 35.0:
        fr = still('e6_fade', t, 27.0, 35.0, 1.05, 1.3, .5, .4)
    elif t < 49.0:
        fr = still('e6_amma_reads', t, 35.0, 49.0, 1.0, 1.15, .5, .4, .5, .35)
    elif t < 60.0:
        fr = still('e6_gate_night', t, 49.0, 60.0, 1.0, 1.18, .55, .5, .7, .62, rain=True)
        for c in (52.0, 53.3):       # the padlock: a tiny jolt each time
            if c <= t < c + .12: fr = cv2.warpAffine(fr, np.float32([[1, 0, 5], [0, 1, 3]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    elif t < 65.0:
        fr = still('e6_phone', t, 60.0, 65.0, 1.05, 1.25, .55, .45, rain=True)
    elif t < 72.0:
        n = int(seg(t, 65.8, 67.8) * len(SEARCH) + .999) if t > 65.8 else 0
        fr = over(blank(), inbox_ui(n, t > 68.6))
        fr = tap(fr, 540, 470, seg(t, 68.4, 69.0))
    elif t < 79.0:
        fr = still('e6_amma_phone', t, 72.0, 79.0, 1.0, 1.2, .5, .38)
        fr = fr * (1 - seg(t, 77.6, 79.0))
    else:
        lt = t - 79.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, 0, .6) * (1 - seg(lt, 4.4, 5.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .15: fr = fr * seg(t, 0, .15)
    return np.clip(fr, 0, 1)


CUTS = [2.5, 11.0, 19.0, 27.0, 35.0, 49.0, 60.0, 65.0, 72.0]
VO = [('am1', 4.6), ('m1', 28.6), ('am2', 36.4), ('m2', 40.4), ('am3', 74.0)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-6))
    env = np.convolve(env, np.ones(int(.3 * SR)) / int(.3 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.0), fin=.2, fout=.4)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    place(buf, load(A + '/afternoon.mp3'), 2.5, db(-14), fin=.4, fout=1.5)
    place(buf, S('tap.wav'), 11.3, db(-16))                                       # tape tearing (soft)
    place(buf, load(A + '/padlock.mp3'), 51.7, db(-6))
    place(buf, S('heartbeat.mp3')[:int(10.5 * SR)], 49.3, db(-11), fin=.5, fout=1.0)
    for i in range(len(SEARCH)): place(buf, S('key.wav'), 65.9 + i * .38, db(-20))
    place(buf, S('tap.wav'), 68.45, db(-12))
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_ in [(49.0, 65.0), (72.0, 79.0)]:
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(-14), fin=.4, fout=.6)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep06_anime_ml_9x16.mp4')
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
