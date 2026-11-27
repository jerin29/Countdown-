"""ഒരു റിപ്ലൈ · Episode 7 "മുന്നറിയിപ്പ്" (The Warning) — anime, vertical, ~82 s.
Kiran brings the news; Aadhi understands he scared her; her profile is gone.
Usage: python3 ep07_anime.py [--sheet t,..] [--out f.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as E
import ep02_anime as E2

W, H, FPS, DUR = E.W, E.H, E.FPS, 82.0
R = '/home/user/Countdown-/love-story/ep07'
font, mlfont, heart, over, tap, ease, seg, still = E.font, E.mlfont, E.heart, E.over, E.tap, E.ease, E.seg, E2.still


@functools.lru_cache(maxsize=None)
def not_found_ui():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    d.text((60, 38), '11:02', font=font('SemiBold', 34), fill=(255, 255, 255, 255))
    d.line([(60, 160), (84, 136), (60, 160), (84, 184)], fill=(255, 255, 255, 255), width=6)
    d.text((120, 160), 'manjusha.dances', font=font('Bold', 42), fill=(255, 255, 255, 255), anchor='lm')
    d.ellipse([430, 620, 650, 840], outline=(90, 90, 96, 255), width=6)
    d.ellipse([505, 670, 575, 740], fill=(90, 90, 96, 255)); d.pieslice([468, 750, 612, 880], 180, 360, fill=(90, 90, 96, 255))
    d.text((540, 960), 'User not found', font=font('Bold', 54), fill=(255, 255, 255, 255), anchor='mm')
    d.text((540, 1040), 'The link may be broken, or the profile', font=font('Regular', 34), fill=(150, 150, 155, 255), anchor='mm')
    d.text((540, 1090), 'may have been removed.', font=font('Regular', 34), fill=(150, 150, 155, 255), anchor='mm')
    return im


def spinner(fr, t):
    o = fr.copy()
    for i in range(12):
        a = i / 12 * 2 * math.pi + t * 6; r0, r1 = 26, 44
        k = ((i + int(t * 12)) % 12) / 12
        cv2.line(o, (int(540 + r0 * math.cos(a)), int(400 + r0 * math.sin(a))), (int(540 + r1 * math.cos(a)), int(400 + r1 * math.sin(a))),
                 (.3 + .6 * k,) * 3, 6, cv2.LINE_AA)
    return o


@functools.lru_cache(maxsize=None)
def endcard_ui(stage):
    im = Image.new('RGBA', (W, H), (10, 10, 16, 255)); d = ImageDraw.Draw(im)
    d.text((540, 800), 'ഒരു റിപ്ലൈ', font=mlfont('Bold', 150), fill=(244, 226, 196, 255), anchor='mm')
    heart(d, 540, 970, 36, fill=(237, 233, 222, 255), outline=(237, 233, 222, 255), w=2)
    d.text((540, 1080), 'എപ്പിസോഡ് 7', font=mlfont('Regular', 56), fill=(200, 190, 175, 255), anchor='mm')
    d.text((540, 1170), 'മുന്നറിയിപ്പ്', font=mlfont('Bold', 64), fill=(235, 205, 160, 255), anchor='mm')
    if stage:
        d.text((540, 1460), 'Story by Jerin Joseph Sebastian', font=font('Regular', 38), fill=(220, 214, 200, 255), anchor='mm')
        d.text((540, 1520), 'Created with Claude AI & vidIQ', font=font('Regular', 32), fill=(160, 154, 140, 255), anchor='mm')
    return im


def blank(): return np.zeros((H, W, 3), np.float32)


def grey(fr, k=.8):
    g = fr.mean(axis=2, keepdims=True); return (fr * (1 - k) + g * k) * .8


def frame(t):
    if t < 2.0:
        fr = still('e7_kiran_door', t, 0, 2.0, 1.25, 1.1, .5, .35)
        if t < .35: fr = cv2.warpAffine(fr, np.float32([[1, 0, 8 * math.sin(t * 90)], [0, 1, 0]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    elif t < 6.0:
        fr = still('aadhi_joy', t, 2.0, 6.0, 1.0, 1.1, .55, .45)
    elif t < 10.0:      # refreshing her profile, smiling: no reaction yet
        fr = over(blank(), E.profile_ui(True)); fr = tap(fr, 540, 300, seg(t, 6.3, 6.8))
        if 6.6 < t < 8.2: fr = spinner(fr, t)
        if t > 8.8: fr = tap(fr, 540, 300, seg(t, 8.8, 9.3))
    elif t < 18.0:
        fr = still('e7_kiran_door', t, 10.0, 18.0, 1.0, 1.15, .5, .35)
    elif t < 30.0:
        fr = still('e7_kiran_explain', t, 18.0, 30.0, 1.0, 1.15, .45, .45, .6, .5)
    elif t < 38.0:
        fr = still('e7_shock', t, 30.0, 38.0, 1.0, 1.3, .55, .4, .6, .32)
    elif t < 40.5:
        fr = grey(still('e6_fade', t, 38.0, 40.5, 1.1, 1.2, .5, .4))
    elif t < 43.0:
        fr = grey(still('e6_gate_night', t, 40.5, 43.0, 1.1, 1.2, .55, .4, rain=True))
    elif t < 45.0:
        fr = grey(still('e6_amma_phone', t, 43.0, 45.0, 1.1, 1.2, .5, .35))
    elif t < 48.0:
        fr = still('e7_shock', t, 45.0, 48.0, 1.6, 1.75, .62, .27)
    elif t < 60.0:
        fr = still('e7_sitting', t, 48.0, 60.0, 1.0, 1.12, .5, .5, rain=True)
    elif t < 64.0:
        fr = still('e7_alone', t, 64.0 - 4, 64.0, 1.0, 1.08, .55, .6, rain=True)
    elif t < 72.0:      # he opens her profile — it loads, and loads
        fr = over(blank(), E.profile_ui(True)) if t < 66.5 else blank() + .02
        fr = tap(fr, 540, 300, seg(t, 64.3, 64.8))
        if t >= 66.5: fr = spinner(fr, t)
    elif t < 77.0:
        fr = over(blank(), not_found_ui())
        fr = fr * (1 - .5 * seg(t, 75.5, 77.0))
    else:
        lt = t - 77.0
        fr = over(blank() + np.array([16, 10, 10], np.float32) / 255, endcard_ui(1 if lt > 1.8 else 0)) * seg(lt, 0, .6) * (1 - seg(lt, 4.4, 5.0))
    for c in CUTS:
        if c - .06 <= t < c + .06: fr = fr * (.55 + .45 * abs(t - c) / .06)
    fr = fr * E.vign()
    if t < .1: fr = fr * seg(t, 0, .1)
    return np.clip(fr, 0, 1)


CUTS = [2.0, 6.0, 10.0, 18.0, 30.0, 38.0, 40.5, 43.0, 45.0, 48.0, 60.0, 64.0, 72.0]
VO = [('k1', .15), ('k2', 10.6), ('a1', 18.6), ('k3', 21.2), ('a2', 45.4), ('k4', 50.0)]


def mix(out):
    load, place, db, SR = E.load, E.place, E.db, E.SR
    A = R + '/audio'; S = lambda n: load(E.A + '/sfx/' + n)
    buf = np.zeros((int(DUR * SR), 2), np.float32)
    sc = load(A + '/score.mp3')[:int(DUR * SR)]
    env = np.ones(len(sc), np.float32)
    for k, at in VO:
        d = len(load(f'{A}/{k}.mp3')) / SR; a, b = int((at - .25) * SR), int((at + d + .2) * SR)
        env[max(0, a):min(len(env), b)] = np.minimum(env[max(0, a):min(len(env), b)], db(-6))
    for a_, b_, g in [(30, 38, -40), (72.2, 77, -14)]:        # silence on the shock; almost nothing on "User not found"
        env[int(a_ * SR):int(b_ * SR)] = np.minimum(env[int(a_ * SR):int(b_ * SR)], db(g))
    env = np.convolve(env, np.ones(int(.3 * SR)) / int(.3 * SR), mode='same').astype(np.float32)
    place(buf, sc * env[:, None], 0, db(-2.0), fin=.05, fout=.5)
    for k, at in VO: place(buf, load(f'{A}/{k}.mp3'), at, db(1))
    place(buf, S('swipe.wav'), 0.0, db(-8))                                    # door bang-ish
    for tt in (6.35, 8.85, 64.35): place(buf, S('tap.wav'), tt, db(-13))
    place(buf, S('tap2.wav'), 31.0, db(-6))                                    # phone hits the bed
    place(buf, S('heartbeat.mp3')[:int(7 * SR)], 38.0, db(-12), fin=.3, fout=.6)
    place(buf, S('err.wav'), 72.15, db(-10))
    rn = load(E.A + '/sfx/rain.mp3')
    for a_, b_ in [(30.0, 38.0), (48.0, 72.0)]:
        seg_ = np.tile(rn, (int((b_ - a_) / (len(rn) / SR)) + 2, 1))[:int((b_ - a_ + .4) * SR)]
        place(buf, seg_, a_ - .2, db(-16), fin=.4, fout=.6)
    wav = out.replace('.mp4', '.wav')
    sf = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
                    '-ar', str(SR), wav], input=sf.tobytes(), check=True)
    return wav


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=R + '/out/ONE_REPLY_ep07_anime_ml_9x16.mp4')
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
