"""ഒരു റിപ്ലൈ · Episode 4 "ഒരു റിപ്ലൈ" (One Reply) — anime, vertical, ~86 s.
Based on the real reply: a 9-second voice message the next day (her voice is an AI voice, not the real one).
Usage: python3 ep04_anime.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2

W, H, FPS, DUR = E.W, E.H, E.FPS, 86.0
R = '/home/user/Countdown-/love-story/ep04'
AN = E2.AN
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
HIS = ['Instagramil aayalum YouTubeil aayalum njan', 'message um comment um ittu, onnum kandilla',
       'Enthenkilum kaanum ennu vishwasathode...', 'A good friend, Aadhi', 'An anonymous person', 'A big fan',
       'Meet cheyyan thaalparyam und', 'You treat me :D :D', 'I want appreciate you. If you see', 'message plz reply me']
REPLY = "Thank you for replying! You don't know what it means :)"
M1_T0, M1_LEN = 8.0, 9.33
RNG = np.random.default_rng(4)
BARS = [.25 + .75 * abs(math.sin(i * .7)) * RNG.random() ** .5 for i in range(34)]


def mic(d, cx, cy, s, col):
    d.rounded_rectangle([cx - s * .3, cy - s, cx + s * .3, cy + s * .2], s * .3, fill=col)
    d.arc([cx - s * .55, cy - s * .5, cx + s * .55, cy + s * .55], 0, 180, fill=col, width=max(2, int(s * .12)))
    d.line([(cx, cy + s * .55), (cx, cy + s * .85)], fill=col, width=max(2, int(s * .12)))


def chat_base():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:14', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    im.alpha_composite(E.avatar('nila', 80), (110, 120)); d = ImageDraw.Draw(im)
    d.text((210, 138), 'Manjusha', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((210, 186), 'manjusha.dances', font=font('Regular', 28), fill=(160, 160, 165, 255))
    d.line([(0, 240), (W, 240)], fill=(32, 32, 36, 255), width=2)
    # his long message, top cut off by the header
    f = font('Regular', 31); y1 = 760; y0 = y1 - len(HIS) * 44 - 40
    d.rounded_rectangle([200, y0, W - 40, y1], 40, fill=(140, 50, 230, 255))
    for i, ln in enumerate(HIS): d.text((230, y0 + 22 + i * 44), ln, font=f, fill=(255, 255, 255, 255))
    d.rectangle([0, 0, W, 242], fill=(0, 0, 0, 255))
    d.text((60, 38), '2:14', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    im.alpha_composite(E.avatar('nila', 80), (110, 120)); d = ImageDraw.Draw(im)
    d.text((210, 138), 'Manjusha', font=font('SemiBold', 38), fill=(255, 255, 255, 255))
    d.text((210, 186), 'manjusha.dances', font=font('Regular', 28), fill=(160, 160, 165, 255))
    d.line([(0, 240), (W, 240)], fill=(32, 32, 36, 255), width=2)
    d.text((540, 820), '15 JAN', font=font('Regular', 28), fill=(150, 150, 155, 255), anchor='mm')
    # input bar
    y = 1700
    d.rounded_rectangle([40, y, W - 40, y + 110], 55, fill=(38, 38, 42, 255))
    d.ellipse([56, y + 18, 130, y + 92], fill=(56, 151, 240, 255)); d.rectangle([81, y + 43, 105, y + 67], outline=(255, 255, 255, 255), width=4)
    d.text((152, y + 55), 'Message...', font=font('Regular', 38), fill=(150, 150, 155, 255), anchor='lm')
    mic(d, W - 120, y + 55, 26, (255, 255, 255, 255))
    return im


@functools.lru_cache(maxsize=None)
def chat_ui(prog_i, playing, replied, seen):
    """prog_i: 0..34 bars played."""
    im = chat_base().copy(); d = ImageDraw.Draw(im)
    im.alpha_composite(E.avatar('nila', 64), (40, 900)); d = ImageDraw.Draw(im)
    bx0, by0, bx1, by1 = 120, 870, 760, 990
    d.rounded_rectangle([bx0, by0, bx1, by1], 50, fill=(38, 38, 42, 255))
    cx, cy = bx0 + 62, (by0 + by1) / 2
    if playing:
        d.rectangle([cx - 16, cy - 22, cx - 5, cy + 22], fill=(255, 255, 255, 255)); d.rectangle([cx + 5, cy - 22, cx + 16, cy + 22], fill=(255, 255, 255, 255))
    else:
        d.polygon([(cx - 14, cy - 24), (cx - 14, cy + 24), (cx + 22, cy)], fill=(255, 255, 255, 255))
    for i, b in enumerate(BARS[:30]):
        x = bx0 + 120 + i * 13; hh = 8 + b * 34
        d.rounded_rectangle([x, cy - hh, x + 6, cy + hh], 3, fill=(255, 255, 255, 255) if i < prog_i else (120, 120, 128, 255))
    left = 9 - int(9 * prog_i / 30) if prog_i else 9
    d.text((bx1 - 30, cy), f'0:{left:02d}', font=font('Regular', 28), fill=(220, 220, 225, 255), anchor='rm')
    d.text((bx0 + 20, by1 + 24), 'View transcription', font=font('Regular', 26), fill=(150, 150, 155, 255))
    if replied:
        f = font('Regular', 34)
        lines = ['Thank you for replying!', "You don't know what it means :)"]
        y0 = 1150; bw = max(d.textlength(l, font=f) for l in lines) + 64
        d.rounded_rectangle([W - 40 - bw, y0, W - 40, y0 + 130], 40, fill=(140, 50, 230, 255))
        for i, l in enumerate(lines): d.text((W - 40 - bw + 32, y0 + 22 + i * 46), l, font=f, fill=(255, 255, 255, 255))
        if seen: d.text((W - 50, y0 + 150), 'Seen', font=font('Regular', 28), fill=(150, 150, 155, 255), anchor='ra')
    return im


@functools.lru_cache(maxsize=None)
def lock_ui():
    bg = cv2.imread(os.path.join(AN, 'aadhi_214am.jpg')); bg = cv2.resize(bg, (W, H)); bg = cv2.GaussianBlur(bg, (0, 0), 28)
    bg = (bg.astype(np.float32) * .45).astype(np.uint8)
    im = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert('RGBA'); d = ImageDraw.Draw(im)
    d.text((540, 300), '2:14', font=font('Bold', 190), fill=(235, 238, 245, 255), anchor='mm')
    d.text((540, 430), 'Thursday', font=font('Medium', 44), fill=(220, 224, 232, 255), anchor='mm')
    d.rounded_rectangle([50, 760, W - 50, 1000], 40, fill=(245, 245, 248, 235))
    im.alpha_composite(E.avatar('nila', 90), (80, 790)); d = ImageDraw.Draw(im)
    d.text((196, 800), 'Instagram · now', font=font('Regular', 28), fill=(90, 90, 96, 255))
    d.text((196, 842), 'manjusha.dances', font=font('Bold', 34), fill=(20, 20, 24, 255))
    d.text((236, 892), 'sent you a voice message', font=font('Regular', 34), fill=(30, 30, 36, 255))
    mic(d, 210, 912, 16, (30, 30, 36, 255))
    return im


@functools.lru_cache(maxsize=None)
def story_ui():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(3):
        x0 = 30 + i * 345; d.rounded_rectangle([x0, 40, x0 + 330, 46], 3, fill=(255, 255, 255, 255 if i == 0 else 110))
    im.alpha_composite(E.avatar('nila', 72), (36, 76)); d = ImageDraw.Draw(im)
    E.shadow_text(d, (124, 84), 'manjusha.dances', font('SemiBold', 32)); E.shadow_text(d, (124 + d.textlength('manjusha.dances', font=font('SemiBold', 32)) + 16, 86), '2h', font('Regular', 30), fill=(230, 230, 230, 255))
    for (txt, y, sz, bg) in [('Birthday week!', 560, 64, (255, 255, 255, 235)), ('25 on the 12th', 670, 52, (232, 70, 110, 235))]:
        f = font('Bold', sz); tw = d.textlength(txt, font=f)
        d.rounded_rectangle([540 - tw / 2 - 30, y - sz * .75, 540 + tw / 2 + 30, y + sz * .75], 18, fill=bg)
        d.text((540, y), txt, font=f, fill=(30, 20, 30, 255) if bg[0] == 255 else (255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle([40, 1760, W - 150, 1850], 45, outline=(255, 255, 255, 200), width=3)
    d.text((90, 1805), 'Send message', font=font('Regular', 34), fill=(255, 255, 255, 230), anchor='lm')
    heart(d, W - 90, 1805, 26, fill=None, outline=(255, 255, 255, 255), w=4)
    return im


@functools.lru_cache(maxsize=None)
def counter_ui(n):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = f'x {n}'; f = font('Bold', 60); tw = d.textlength(txt, font=f)
    d.rounded_rectangle([540 - tw / 2 - 100, 330, 540 + tw / 2 + 50, 440], 55, fill=(20, 20, 26, 200))
    x = 540 - tw / 2 - 50
    d.polygon([(x - 18, 360), (x - 18, 410), (x + 22, 385)], fill=(255, 255, 255, 255))
    d.text((540 + 25, 385), txt, font=f, fill=(255, 255, 255, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 4', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=1)
def dance():
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(AN, 'aadhi_dance.mp4'), '-vf', 'scale=1098:1920,crop=1080:1920',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, 1920, 1080, 3)


def blank(): return np.zeros((H, W, 3), np.float32)


def zoomed(fr, z, cx=.5, cy=.5):
    M = np.float32([[z, 0, W * cx * (1 - z)], [0, z, H * cy * (1 - z)]])
    return cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REPLICATE)


def frame(t):
    if t < 2.5:
        fr = over(blank(), lock_ui()) * (1 + .25 * math.exp(-((t - .3) * 3) ** 2))
    elif t < 7.0:
        fr = still('aadhi_shock', t, 2.5, 7.0, 1.0, 1.25, .5, .4, .62, .4)
    elif t < 20.0:
        p = seg(t, M1_T0, M1_T0 + M1_LEN)
        playing = M1_T0 <= t < M1_T0 + M1_LEN or t > 17.8
        fr = over(blank(), chat_ui(int(30 * p) if t < 17.8 else int(30 * seg(t, 17.8, 27.1)), playing, False, False))
        fr = zoomed(fr, 1 + .12 * ease(seg(t, 7, 20)), .4, .48)
        fr = tap(fr, 210, 930, seg(t, 7.5, 8.1)); fr = tap(fr, 210, 930, seg(t, 17.5, 18.1))
    elif t < 25.5:
        fr = still('aadhi_smile', t, 20.0, 25.5, 1.05, 1.25, .55, .5)
    elif t < 31.0:
        F = dance(); i = min(len(F) - 1, int((t - 25.5) * 24))
        fr = F[i].astype(np.float32) / 255
    elif t < 36.0:
        fr = still('aadhi_joy', t, 31.0, 36.0, 1.0, 1.12, .55, .45)
        n = [2, 5, 12, 27, 48, 73, 100][min(6, int((t - 31.2) / .62))] if t > 31.2 else 1
        fr = over(fr, counter_ui(n))
    elif t < 40.0:
        fr = still('e4_kiran_sleepy', t, 36.0, 40.0, 1.0, 1.1, .5, .4)
    elif t < 44.0:
        fr = still('e4_call', t, 40.0, 44.0, 1.0, 1.12, .5, .45)
    elif t < 47.5:
        fr = still('e4_kiran_sleepy', t, 44.0, 47.5, 1.3, 1.5, .55, .38)
        if t < 44.6: fr = zoomed(fr, 1 + .04 * math.sin((t - 44) * 40))
    elif t < 56.0:
        fr = still('e4_bus', t, 47.5, 56.0, 1.0, 1.15, .45, .55, .5, .45)
    elif t < 61.0:
        fr = still('aadhi_rainbow', t, 56.0, 61.0, 1.15, 1.0, .5, .4)
    elif t < 66.0:
        fr = still('e2_aadhi_tea', t, 61.0, 66.0, 1.0, 1.12, .6, .4)
    elif t < 72.0:
        fr = over(blank(), chat_ui(30, False, t > 66.6, t > 68.6))
        fr = tap(fr, W - 120, 1755, seg(t, 66.1, 66.6))
    elif t < 78.0:
        fr = still('aadhi_rooftop', t, 72.0, 78.0, 1.0, 1.15, .5, .4)
    elif t < 81.5:
        fr = still('e4_birthday', t, 78.0, 81.5, 1.0, 1.06, .5, .45)
        fr = over(fr, story_ui())
        if t > 79.6: fr = tap(fr, 540, 1120, min(1, (t - 79.6) / .5) * .5)   # his thumb stops and holds
    else:
        lt = t - 81.5
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, 0, .6) * (1 - seg(lt, 4.0, 4.5))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .15: fr = fr * seg(t, 0, .15)
    return np.clip(fr, 0, 1)


CUTS = [2.5, 7.0, 20.0, 25.5, 31.0, 36.0, 40.0, 44.0, 47.5, 56.0, 61.0, 66.0, 72.0, 78.0]
VO = [('a1', 3.6), ('m1', M1_T0), ('a2', 20.4), ('k1', 36.4), ('a3', 40.4), ('k2', 44.3), ('a4', 48.6), ('a5', 73.2)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-10 if k == 'm1' else -5))
    a, b = int(66 * SR), int(78 * SR); env[a:b] = np.minimum(env[a:b], db(-5))      # "Seen": softer
    env = np.convolve(env, np.ones(int(.3 * SR)) / int(.3 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.5), fin=.2, fout=2.0)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(3 if k == 'm1' else 1))
    m1 = load(A + '/m1.mp3'); place(buf, m1, 18.0, db(-13), fout=1.5)        # he plays it again (heard faintly)
    place(buf, S('pop.wav'), .25, db(-8))
    place(buf, S('heartbeat.mp3')[:int(4.4 * SR)], 2.6, db(-10), fin=.3, fout=.6)
    for tt in (7.55, 17.55): place(buf, S('tap.wav'), tt, db(-13))
    place(buf, S('send.wav'), 66.6, db(-11)); place(buf, S('tap.wav'), 66.15, db(-13))
    place(buf, S('swipe.wav'), 78.0, db(-14))
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_ in [(2.5, 7.0), (36.0, 47.5)]:
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(-18), fin=.4, fout=.5)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep04_anime_ml_9x16.mp4')
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
