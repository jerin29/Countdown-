"""ഒരു റിപ്ലൈ · Episode 8 "അയക്കാത്ത കത്ത്" (The Letter He Never Sends) — anime, vertical, ~84 s.
He writes an apology, understands that sending it would scare her again, deletes it, lets go — and at dawn starts filming.
Usage: python3 ep08_anime.py [--sheet t,..] [--out f.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2
import ep04_anime as E4

W, H, FPS, DUR = E.W, E.H, E.FPS, 84.0
R = '/home/user/Countdown-/love-story/ep08'
AN = E2.AN
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still
LETTER = ('മഞ്ജുഷ,\nസോറി.\nനിന്നെ പേടിപ്പിക്കാൻ ഞാൻ ഉദ്ദേശിച്ചിട്ടില്ല. ആ ഗിഫ്റ്റ് അയച്ചത് തെറ്റായിരുന്നു, ഇപ്പോൾ എനിക്ക് മനസ്സിലായി.\n'
          'നിന്റെ ഒരു റിപ്ലൈ കൊണ്ട് ഞാൻ കുറച്ചു ദിവസം ഒരുപാട് സന്തോഷിച്ചു.\nഅത്രയേ ഉള്ളൂ.\nഇനി ഒരിക്കലും ശല്യപ്പെടുത്തില്ല.\n— ആദി')
TYPE_T0, TYPE_T1 = 10.4, 19.0


def wrap(d, text, f, maxw):
    out = []
    for para in text.split('\n'):
        line = ''
        for w_ in para.split(' '):
            t = (line + ' ' + w_).strip()
            if d.textlength(t, font=f) <= maxw: line = t
            else: out.append(line); line = w_
        out.append(line)
    return out


@functools.lru_cache(maxsize=None)
def notes_ui(n, cursor, selected, popup, empty):
    im = Image.new('RGBA', (W, H), (28, 28, 30, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:14', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 196, 0, 255), width=6)
    d.text((100, 160), 'Notes', font=font('Regular', 38), fill=(255, 196, 0, 255), anchor='lm')
    d.text((W - 60, 160), 'Done', font=font('SemiBold', 38), fill=(255, 196, 0, 255), anchor='rm')
    d.text((540, 250), 'Today, 2:14 AM', font=font('Regular', 28), fill=(140, 140, 146, 255), anchor='mm')
    if empty:
        if cursor: d.line([(60, 320), (60, 372)], fill=(255, 196, 0, 255), width=4)
        return im
    f = mlfont('Regular', 42); text = LETTER[:n]
    lines = wrap(d, text, f, W - 120); y = 310
    if selected:
        for ln in lines:
            if ln: d.rectangle([56, y - 4, 64 + d.textlength(ln, font=f), y + 64], fill=(60, 110, 200, 160))
            y += 70
        y = 310
    for ln in lines:
        d.text((60, y), ln, font=f, fill=(240, 240, 244, 255)); y += 70
    if cursor and not selected:
        d.line([(64 + d.textlength(lines[-1], font=f), y - 66), (64 + d.textlength(lines[-1], font=f), y - 10)], fill=(255, 196, 0, 255), width=4)
    if popup:
        d.rounded_rectangle([250, 230, 830, 300], 16, fill=(60, 60, 64, 255))
        for i, (lab, x) in enumerate([('Cut', 330), ('Copy', 470), ('Delete', 660)]):
            d.text((x, 265), lab, font=font('SemiBold' if i == 2 else 'Regular', 32), fill=(255, 110, 100, 255) if i == 2 else (255, 255, 255, 255), anchor='mm')
            if i < 2: d.line([(x + 70, 245), (x + 70, 285)], fill=(90, 90, 96, 255), width=2)
    return im


@functools.lru_cache(maxsize=None)
def page_follow_ui(following):
    im = E2.page_ui(False).copy(); d = ImageDraw.Draw(im)
    if following:
        d.rounded_rectangle([60, 760, 520, 850], 18, fill=(54, 54, 58, 255))
        d.text((290, 805), 'Following', font=font('SemiBold', 34), fill=(255, 255, 255, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def thumb(k):
    """screenshots in his gallery: phone screens from earlier episodes."""
    src = {0: lambda: E4.chat_ui(30, False, False, False), 1: lambda: E.profile_ui(True), 2: lambda: E2.page_ui(False),
           3: lambda: E4.story_ui(), 4: lambda: E.profile_ui(False), 5: lambda: E2.page_dm_ui(False)}
    if k in src:
        ui = src[k]()
        base = Image.new('RGBA', (W, H), (0, 0, 0, 255))
        if k == 3: base = Image.fromarray(cv2.cvtColor(cv2.resize(cv2.imread(os.path.join(AN, 'e4_birthday.jpg')), (W, H)), cv2.COLOR_BGR2RGB)).convert('RGBA')
        base.alpha_composite(ui); im = base
    else:
        name = ['manjusha_dance', 'manjusha_portrait', 'manjusha_reading', 'e5_gate'][k - 6]
        im = Image.fromarray(cv2.cvtColor(cv2.resize(cv2.imread(os.path.join(AN, name + '.jpg')), (W, H)), cv2.COLOR_BGR2RGB)).convert('RGBA')
    return im.convert('RGB').resize((350, 622))


ORDER = [1, 6, 2, 7, 0, 8, 4, 9, 3]     # index 4 (k=0) is the reply he keeps


@functools.lru_cache(maxsize=None)
def gallery_ui(stage):
    """stage 0: all selected but the reply; 1: deleted, only the reply left."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '2:41', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.text((60, 140), 'Screenshots', font=font('Bold', 52), fill=(255, 255, 255, 255))
    if stage == 0:
        d.text((W - 60, 165), '8 selected', font=font('Regular', 34), fill=(56, 151, 240, 255), anchor='rm')
        for i, k in enumerate(ORDER):
            c, r = i % 3, i // 3; x, y = 8 + c * 358, 240 + r * 500
            th = thumb(k).resize((350, 492)); im.paste(th, (x, y)); d = ImageDraw.Draw(im)
            if k != 0:
                d.ellipse([x + 290, y + 14, x + 336, y + 60], fill=(56, 151, 240, 255), outline=(255, 255, 255, 255), width=3)
                d.line([(x + 302, y + 38), (x + 312, y + 48), (x + 326, y + 28)], fill=(255, 255, 255, 255), width=4)
            else:
                d.ellipse([x + 290, y + 14, x + 336, y + 60], outline=(255, 255, 255, 255), width=3)
        d.rectangle([0, 1760, W, H], fill=(20, 20, 22, 255))
        d.text((W - 80, 1830), 'Delete', font=font('SemiBold', 40), fill=(255, 90, 80, 255), anchor='rm')
    else:
        th = thumb(0).resize((560, 995)); im.paste(th, (260, 300)); d = ImageDraw.Draw(im)
        d.text((540, 1360), '1 photo', font=font('Regular', 32), fill=(150, 150, 155, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def rec_ui(secs):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([390, 60, 690, 130], 20, fill=(220, 40, 40, 230))
    d.ellipse([416, 83, 440, 107], fill=(255, 255, 255, 255))
    d.text((560, 95), f'00:00:{secs:02d}', font=font('SemiBold', 36), fill=(255, 255, 255, 255), anchor='mm')
    return im


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 8', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'അയക്കാത്ത കത്ത്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank(): return np.zeros((H, W, 3), np.float32)


def frame(t):
    cur = int(t * 2) % 2 == 0; N = len(LETTER)
    if t < 2.5:          # HOOK: the whole apology, selected, thumb on Delete
        fr = over(blank(), notes_ui(N, False, True, True, False)); fr = tap(fr, 660, 265, seg(t, 1.6, 2.2))
    elif t < 10.0:
        fr = still('aadhi_214am', t, 2.5, 10.0, 1.0, 1.2, .5, .5, .6, .55, rain=True)
    elif t < 28.0:
        n = int(N * seg(t, TYPE_T0, TYPE_T1))
        fr = over(blank(), notes_ui(n, cur, False, False, False))
    elif t < 36.0:
        fr = still('e8_reading', t, 28.0, 36.0, 1.05, 1.3, .6, .55, .65, .5, rain=True)
    elif t < 42.0:
        if t < 37.0: fr = over(blank(), notes_ui(N, cur, False, False, False))
        elif t < 40.0: fr = over(blank(), notes_ui(N, False, True, t > 38.0, False)); fr = tap(fr, 660, 265, seg(t, 39.3, 39.9))
        else: fr = over(blank(), notes_ui(0, cur, False, False, True))
    elif t < 50.0:
        fr = over(blank(), page_follow_ui(t < 45.4)); fr = tap(fr, 290, 805, seg(t, 45.0, 45.6))
    elif t < 60.0:
        if t < 54.0: fr = over(blank(), gallery_ui(0)); fr = tap(fr, W - 160, 1830, seg(t, 53.3, 53.9))
        else: fr = over(blank(), gallery_ui(1)) * seg(t, 54.0, 54.5)
    elif t < 70.0:
        fr = still('e8_dawn', t, 60.0, 70.0, 1.15, 1.0, .5, .45)
        fr = fr * (.6 + .4 * seg(t, 60.0, 62.5))
    elif t < 78.0:
        fr = still('e8_record', t, 70.0, 78.0, 1.0, 1.25, .45, .5, .42, .52)
        fr = tap(fr, 470, 1080, seg(t, 73.8, 74.4))
        if t > 74.2: fr = over(fr, rec_ui(int(t - 74.2) + 1))
    else:
        lt = t - 78.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, 0, .6) * (1 - seg(lt, 5.4, 6.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .15: fr = fr * seg(t, 0, .15)
    return np.clip(fr, 0, 1)


CUTS = [2.5, 10.0, 28.0, 36.0, 42.0, 50.0, 60.0, 70.0, 78.0]
VO = [('a1', 19.6), ('a2', 30.0), ('a3', 56.0)]


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
    place(buf, sc * env[:, None], 0, db(-2.5), fin=.2, fout=1.0)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    key = S('key.wav')
    for i in range(46): place(buf, key, TYPE_T0 + (TYPE_T1 - TYPE_T0) * i / 46, db(-22 + (i % 3)))
    for tt in (1.65, 39.35, 45.05, 53.35, 73.85): place(buf, S('tap.wav'), tt, db(-13))
    place(buf, S('swipe.wav'), 40.0, db(-12)); place(buf, S('swipe.wav'), 54.0, db(-12))
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_, g in [(2.5, 42.0, -12), (42.0, 61.5, -17)]:     # heavy rain, then it stops at dawn
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(g), fin=.4, fout=1.5 if b_ > 60 else .3)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep08_anime_ml_9x16.mp4')
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
