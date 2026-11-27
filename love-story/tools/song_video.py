"""ഒരു റിപ്ലൈ — title song video (version 1 song, anime visuals, vertical 1080x1920, 24 fps).
Each lyric line gets a picture (timings from the song's speech-to-text); slow Ken Burns moves, soft crossfades,
the two animated clips (Manjusha's dance, Aadhi's happy dance), title card at the start and release card at the end.
Usage: python3 song_video.py [--sheet t,t,...] [--out file.mp4]
"""
import os, sys, math, argparse, subprocess, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

AN = '/home/user/Countdown-/love-story/anime_test'
SONG = '/home/user/Countdown-/love-story/song/oru-reply-ml_master.mp3'
OUT = '/home/user/Countdown-/love-story/trial/out/ONE_REPLY_title_song_v1_ml_9x16.mp4'
W, H, FPS = 1080, 1920, 24
DUR = 176.5
XF = .55  # crossfade

# (start, end, source, move) — move: 'in' zoom in, 'out' zoom out, 'up'/'down' pan; source *.mp4 = clip
SHOTS = [
    (0.0, 12.4, 'city_night', 'down'),           # intro + title
    (12.4, 15.5, 'aadhi_214am', 'in'),           # രാത്രി രണ്ടു മണിക്ക് സ്ക്രീനിൻ വെളിച്ചം
    (15.5, 20.6, 'manjusha_dance.mp4', None),    # ഒരു റീലിൽ നിന്നെ കണ്ടു ഞാൻ
    (20.6, 23.2, 'aadhi_wonder', 'in'),          # ഒരു ചിരിയിൽ
    (23.2, 26.6, 'manjusha_portrait', 'out'),    # നിന്നുപോയി എൻ ലോകം
    (26.6, 29.0, 'aadhi_sit', 'in'),             # വീണ്ടും വീണ്ടും
    (29.0, 31.6, 'aadhi_smile', 'in'),           # കണ്ടു ഞാൻ
    (31.6, 34.4, 'manjusha_dance', 'out'),       # ആയിരം പേർ നോക്കും നിന്നെ
    (34.4, 38.6, 'aadhi_back', 'in'),            # അതിലൊരാൾ മാത്രം ഞാൻ
    (38.6, 45.3, 'aadhi_hesitant', 'in'),        # എങ്കിലും എൻ മനസ്സു പറഞ്ഞു, ഒന്ന് പറഞ്ഞു നോക്കാം
    (45.3, 50.0, 'aadhi_joy', 'out'),            # ഒരു reply, ഒരു വരി മതി
    (50.0, 54.8, 'manjusha_reading', 'in'),      # എൻ രാവുകൾ പൂത്തു വിടരാൻ
    (54.8, 60.0, 'aadhi_dance.mp4', None),       # ഒരു reply, നിന്നൊരു വാക്ക്, എൻ ഹൃദയം പാടി നടക്കാൻ
    (60.0, 69.6, 'aadhi_rainbow', 'up'),         # ഒരു reply… (instrumental)
    (69.6, 74.0, 'aadhi_smile', 'out'),          # നന്ദി എന്ന ചെറിയൊരു വാക്ക്
    (74.0, 78.6, 'aadhi_joy', 'in'),             # നൂറുവട്ടം വായിച്ചു ഞാൻ
    (78.6, 84.0, 'aadhi_rainbow', 'in'),         # ഒരു മെസ്സേജിൽ ഒരു മഴവില്ല്
    (84.0, 89.2, 'aadhi_sit', 'out'),            # ഇന്നലെ വരെ ഇല്ലാത്തൊരു ഞാൻ
    (89.2, 92.6, 'manjusha_reading', 'out'),     # ദൂരെ ദൂരെ നീ നിൽക്കുമ്പോഴും
    (92.6, 96.2, 'aadhi_rooftop', 'up'),         # അരികിലാണെന്ന് തോന്നും
    (96.2, 103.2, 'aadhi_joy', 'in'),            # ഒരു notification കേട്ടാൽ മതി, ഉള്ളിൽ പൂക്കൾ വിടരും
    (103.2, 108.2, 'manjusha_dance.mp4', None),  # ഒരു reply, ഒരു വരി മതി
    (108.2, 113.0, 'aadhi_dance.mp4', None),     # എൻ രാവുകൾ പൂത്തു വിടരാൻ
    (113.0, 119.6, 'aadhi_rainbow', 'out'),      # ഒരു reply, നിന്നൊരു വാക്ക്…
    (119.6, 127.0, 'city_night', 'up'),          # ഒരു reply, ഒരു reply (instrumental)
    (127.0, 135.0, 'aadhi_rooftop', 'in'),       # ചില ഇഷ്ടങ്ങൾ പറയേണ്ട, ചില ഇഷ്ടങ്ങൾ കാക്കേണ്ട
    (135.0, 141.6, 'manjusha_sunrise', 'in'),    # ദൂരെ നിന്നു നീ ചിരിച്ചാൽ മതി
    (141.6, 146.6, 'aadhi_back', 'out'),         # അതുമതി, അതുമതി
    (146.6, 151.6, 'manjusha_dance.mp4', None),  # ഒരു reply, ഒരു വരി മതി
    (151.6, 156.2, 'aadhi_joy', 'out'),          # എൻ രാവുകൾ പൂത്തു വിടരാൻ
    (156.2, 161.2, 'aadhi_dance.mp4', None),     # ഒരു reply, നിന്നൊരു വാക്ക്
    (161.2, 168.4, 'manjusha_sunrise', 'out'),   # ചില ഇഷ്ടങ്ങൾ ഒരു reply…
    (168.4, 176.5, 'city_night', 'in'),          # outro + release card
]


@functools.lru_cache(maxsize=None)
def img(name):
    im = cv2.imread(os.path.join(AN, name + '.jpg'))
    return cv2.resize(im, (int(W * 1.18), int(H * 1.18)), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


@functools.lru_cache(maxsize=None)
def clip(name):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(AN, name), '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3)


def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)


def shot_frame(i, t):
    t0, t1, src, mv = SHOTS[i]
    k = (t - t0) / (t1 - t0)
    if src.endswith('.mp4'):
        F = clip(src); j = min(len(F) - 1, int((t - t0) * FPS))
        return F[j].astype(np.float32) / 255
    im = img(src); ih, iw = im.shape[:2]
    z0, z1, dy0, dy1 = {'in': (1.0, 1.12, 0, 0), 'out': (1.12, 1.0, 0, 0), 'up': (1.06, 1.06, .5, -.5), 'down': (1.06, 1.06, -.5, .5)}[mv]
    z = z0 + (z1 - z0) * ease(k) ; dy = dy0 + (dy1 - dy0) * ease(k)
    sc = z / 1.18   # images are stored at 1.18x the frame, so zoom 1.0 fills the frame exactly
    cx, cy = iw / 2, ih / 2 + dy * (ih - H / sc) / 2 * .9
    M = np.float32([[sc, 0, W / 2 - cx * sc], [0, sc, H / 2 - cy * sc]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


F_ML = '/usr/share/fonts/truetype/noto/NotoSansMalayalam-{}.ttf'
F_IN = '/usr/share/fonts/opentype/inter/Inter-{}.otf'


@functools.lru_cache(maxsize=None)
def card(kind):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ml = lambda w, s: ImageFont.truetype(F_ML.format(w), s, layout_engine=ImageFont.Layout.RAQM)
    en = lambda w, s: ImageFont.truetype(F_IN.format(w), s)
    def shadowed(xy, txt, f, fill):
        for dx, dy in [(0, 4), (3, 3), (-3, 3)]: d.text((xy[0] + dx, xy[1] + dy), txt, font=f, fill=(0, 0, 0, 150), anchor='mm')
        d.text(xy, txt, font=f, fill=fill, anchor='mm')
    if kind == 'title':
        shadowed((540, 470), 'ഒരു റിപ്ലൈ', ml('Bold', 160), (250, 236, 210, 255))
        shadowed((540, 610), 'Title Song', en('Medium', 46), (225, 215, 200, 255))
    else:
        shadowed((540, 430), 'ഒരു റിപ്ലൈ', ml('Bold', 140), (250, 236, 210, 255))
        shadowed((540, 570), 'എപ്പിസോഡ് 1', ml('Regular', 60), (235, 225, 210, 255))
        shadowed((540, 650), 'January 1 · 9 PM', en('SemiBold', 48), (245, 205, 140, 255))
        shadowed((540, 1660), 'Story by Jerin Joseph Sebastian', en('Regular', 36), (230, 224, 212, 255))
        shadowed((540, 1714), 'Created with Claude AI & vidIQ', en('Regular', 30), (200, 194, 182, 255))
    return np.asarray(im, np.float32) / 255


def over(fr, layer, a):
    al = layer[..., 3:4] * a
    return fr * (1 - al) + layer[..., [2, 1, 0]] * al


# lyric lines (start, end, text) from the song's speech-to-text, spelled as in the lyrics sheet
LYRICS = [
    (12.3, 20.3, 'രാത്രി രണ്ടു മണിക്ക് സ്ക്രീനിൻ വെളിച്ചം\nഒരു റീലിൽ നിന്നെ കണ്ടു ഞാൻ'),
    (21.3, 26.3, 'ഒരു ചിരിയിൽ നിന്നുപോയി എൻ ലോകം'), (26.7, 30.0, 'വീണ്ടും വീണ്ടും കണ്ടു ഞാൻ'),
    (31.5, 37.2, 'ആയിരം പേർ നോക്കും നിന്നെ\nഅതിലൊരാൾ മാത്രം ഞാൻ'),
    (38.7, 45.1, 'എങ്കിലും എൻ മനസ്സു പറഞ്ഞു\nഒന്ന് പറഞ്ഞു നോക്കാം'),
    (45.3, 53.8, 'ഒരു റിപ്ലൈ… ഒരു വരി മതി\nഎൻ രാവുകൾ പൂത്തു വിടരാൻ'),
    (54.9, 61.3, 'ഒരു റിപ്ലൈ… നിൻ ഒരു വാക്ക്\nഎൻ ഹൃദയം പാടി നടക്കാൻ'), (62.1, 65.0, 'ഒരു റിപ്ലൈ… ഒരു റിപ്ലൈ…'),
    (69.6, 78.2, 'നന്ദി എന്ന ചെറിയൊരു വാക്ക്\nനൂറു വട്ടം വായിച്ചു ഞാൻ'),
    (78.9, 87.2, 'ഒരു മെസ്സേജിൽ ഒരു മഴവില്ല്\nഇന്നലെ വരെ ഇല്ലാത്തൊരു ഞാൻ'),
    (89.2, 96.1, 'ദൂരെ ദൂരെ നീ നിൽക്കുമ്പോഴും\nഅരികിലാണെന്നു തോന്നും'),
    (96.3, 102.8, 'ഒരു നോട്ടിഫിക്കേഷൻ കേട്ടാൽ മതി\nഉള്ളിൽ പൂക്കൾ വിടരും'),
    (103.2, 111.5, 'ഒരു റിപ്ലൈ… ഒരു വരി മതി\nഎൻ രാവുകൾ പൂത്തു വിടരാൻ'),
    (112.8, 119.3, 'ഒരു റിപ്ലൈ… നിൻ ഒരു വാക്ക്\nഎൻ ഹൃദയം പാടി നടക്കാൻ'), (120.0, 122.8, 'ഒരു റിപ്ലൈ… ഒരു റിപ്ലൈ…'),
    (127.2, 135.0, 'ചില ഇഷ്ടങ്ങൾ പറയേണ്ട\nചില ഇഷ്ടങ്ങൾ കാക്കേണ്ട'),
    (137.1, 145.3, 'ദൂരെ നിന്നു നീ ചിരിച്ചാൽ മതി\nഅതു മതി… അതു മതി…'),
    (146.6, 154.8, 'ഒരു റിപ്ലൈ… ഒരു വരി മതി\nഎൻ രാവുകൾ പൂത്തു വിടരാൻ'),
    (156.1, 161.0, 'ഒരു റിപ്ലൈ… നിൻ ഒരു വാക്ക്\nഎൻ ഹൃദയം പാടി നടക്കാൻ'),
    (161.0, 166.0, 'ചില ഇഷ്ടങ്ങൾ… ഒരു റിപ്ലൈയിൽ പൂർണം'), (168.0, 174.6, 'ഒരു റിപ്ലൈ… ഒരു റിപ്ലൈ…'),
]
SHOW_LYRICS = False


@functools.lru_cache(maxsize=None)
def lyric_layer(text):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F_ML.format('Bold'), 50, layout_engine=ImageFont.Layout.RAQM)
    lines = text.split('\n'); y0 = 1560 - (len(lines) - 1) * 40
    d.rounded_rectangle([60, y0 - 52, W - 60, y0 + len(lines) * 80 - 28], 26, fill=(0, 0, 0, 105))
    for i, ln in enumerate(lines):
        y = y0 + i * 80; fs = 50
        while fs > 34 and d.textlength(ln, font=ImageFont.truetype(F_ML.format('Bold'), fs, layout_engine=ImageFont.Layout.RAQM)) > W - 170: fs -= 2
        fl = ImageFont.truetype(F_ML.format('Bold'), fs, layout_engine=ImageFont.Layout.RAQM)
        for dx, dy in [(0, 3), (2, 2), (-2, 2)]: d.text((540 + dx, y + dy), ln, font=fl, fill=(0, 0, 0, 170), anchor='mm')
        d.text((540, y), ln, font=fl, fill=(255, 246, 228, 255), anchor='mm')
    return np.asarray(im, np.float32) / 255


def frame(t):
    cur = [i for i, s in enumerate(SHOTS) if s[0] <= t < s[1]] or [len(SHOTS) - 1]
    i = cur[0]
    fr = shot_frame(i, t)
    t1 = SHOTS[i][1]
    if i + 1 < len(SHOTS) and t > t1 - XF:   # crossfade into the next shot
        k = ease((t - (t1 - XF)) / XF)
        fr = fr * (1 - k) + shot_frame(i + 1, max(t, SHOTS[i + 1][0])) * k
    # title + release cards
    if t < 12.4: fr = over(fr, card('title'), ease((t - 2.0) / 1.2) * (1 - ease((t - 10.4) / 1.4)))
    if t > 168.4: fr = over(fr, card('end'), ease((t - 169.0) / 1.2))
    if SHOW_LYRICS:
        for a, b, txt in LYRICS:
            if a - .3 <= t < b + .3: fr = over(fr, lyric_layer(txt), ease((t - a + .3) / .35) * (1 - ease((t - b) / .3)))
    # fade in/out
    fr = fr * ease(t / 1.2) * (1 - ease((t - (DUR - 2.0)) / 2.0))
    return np.clip(fr, 0, 1)


def main():
    global SHOW_LYRICS
    ap = argparse.ArgumentParser(); ap.add_argument('--sheet'); ap.add_argument('--out', default=OUT)
    ap.add_argument('--lyrics', action='store_true'); ap.add_argument('--teaser', action='store_true'); a = ap.parse_args()
    SHOW_LYRICS = a.lyrics
    if a.teaser: return teaser(a.out)
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((frame(t) * 255).astype(np.uint8), (216, 384)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f'{t:.0f}', (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 255, 255), 1)
        cols = 8; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)); print('sheet', a.out); return
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', SONG,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                           '-level', '4.0', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest',
                           '-movflags', '+faststart', a.out], stdin=subprocess.PIPE)
    for n in range(int(DUR * FPS)):
        ff.stdin.write((frame(n / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', a.out)


@functools.lru_cache(maxsize=None)
def teaser_card():
    im = Image.new('RGBA', (W, H), (8, 10, 22, 235)); d = ImageDraw.Draw(im)
    ml = lambda w, sz: ImageFont.truetype(F_ML.format(w), sz, layout_engine=ImageFont.Layout.RAQM)
    en = lambda w, sz: ImageFont.truetype(F_IN.format(w), sz)
    d.text((540, 760), 'ഒരു റിപ്ലൈ', font=ml('Bold', 150), fill=(250, 236, 210, 255), anchor='mm')
    d.text((540, 920), 'ടൈറ്റിൽ സോങ്', font=ml('Regular', 60), fill=(235, 225, 210, 255), anchor='mm')
    d.text((540, 1010), 'December 31 · 9 PM', font=en('SemiBold', 52), fill=(245, 205, 140, 255), anchor='mm')
    d.text((540, 1120), 'എപ്പിസോഡ് 1 · January 1', font=ml('Regular', 46), fill=(210, 204, 192, 255), anchor='mm')
    return np.asarray(im, np.float32) / 255


def teaser(out):
    """60 s teaser: verse 1 → first chorus (song 12.0–66.0), then a 'December 31' card."""
    global SHOW_LYRICS
    SHOW_LYRICS = True
    s0, s1, CARD = 12.0, 66.0, 5.0
    T = (s1 - s0) + CARD
    wav = out.replace('.mp4', '.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s0), '-t', str(s1 - s0 + CARD), '-i', SONG,
                    '-af', f'afade=t=in:d=.6,afade=t=out:st={s1 - s0 - .5}:d={CARD + .4},loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', wav], check=True)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                           '-level', '4.0', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for n in range(int(T * FPS)):
        lt = n / FPS; t = s0 + min(lt, s1 - s0 - .01)
        fr = frame(t) if lt > .1 else frame(t) * 0
        fr = fr * ease(lt / .4)
        if lt > s1 - s0 - .6: fr = over(fr, teaser_card(), ease((lt - (s1 - s0 - .6)) / .8))
        ff.stdin.write((np.clip(fr, 0, 1) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', out)


if __name__ == '__main__':
    main()
