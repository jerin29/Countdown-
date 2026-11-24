"""COUNTDOWN S2 title-song videos (lyric video ~3:00 and promo ~1:30) in ml / hi / ta.
Usage: python3 song_video.py LANG PLATES {lyric|promo} [--sheet t1,t2,...] [--out f]
Shots are the episodes' own painted plates, chosen per lyric meaning; the girl is only seen from behind / behind her hair."""
import os, sys, math, argparse, subprocess, functools, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); SONG = os.path.dirname(HERE); S2 = os.path.dirname(SONG)
sys.path.insert(0, os.path.join(S2, 'video', 'tools')); sys.path.insert(0, HERE)
import s2ep, horrorfx as HFX, ep01 as B
from eps import EPS
from lyrics import timed, FILES
W, H, FPS = 1920, 1080, 24
seg = B.seg

# meaning -> list of shots (episode, segment index); repeated lines take the next shot in the list
SHOTS = {
 'intro': [(8, 2), (2, 1)], 'city': [(6, 1)], 'three': [(2, 4)], 'notten': [(8, 2)], 'name': [(8, 4)],
 'turned': [(9, 1)], 'woke': [(5, 3)], 'wake': [(3, 2), (13, 1), (3, 2)], 'return': [(8, 1), (13, 3), (8, 1)],
 'close': [(7, 1), (12, 1), (7, 1)], 'open': [(2, 3), (5, 4), (2, 3)], 'forty': [(2, 2), (11, 2), (9, 3), (2, 2), (11, 2)],
 'mirror': [(4, 2)], 'gears': [(11, 2)], 'faces': [(6, 2)], 'blink': [(6, 4)], 'lullaby': [(12, 2)],
 'breath': [(7, 4), (7, 3)], 'look': [(14, 1)], 'count': [(3, 3)], 'sings': [(14, 2)], 'behind': [(13, 2)],
 'zero': [(8, 4)], 'fill': [(13, 2), (6, 1), (8, 2)],
}
CHORUS = {'wake', 'return', 'close', 'open'}
FONT = {'ml': 'NotoSerifMalayalam-Bold.ttf', 'hi': 'NotoSerifDevanagari-Bold.ttf', 'ta': 'NotoSerifTamil-Bold.ttf'}
TITLE = {'ml': 'നാൽപത്', 'hi': 'चालीस', 'ta': 'நாற்பது'}
DATE = {'ml': ('സീസൺ 2 · ഡിസംബർ 10 മുതൽ · രാത്രി 9 മണി', 'Season 2 · from 10 Dec · 9 PM IST'),
        'hi': ('सीज़न 2 · 11 दिसंबर से · रात 9:20', 'Season 2 · from 11 Dec · 9:20 PM IST'),
        'ta': ('சீசன் 2 · டிசம்பர் 11 முதல் · இரவு 9:40', 'Season 2 · from 11 Dec · 9:40 PM IST')}
SONGF = {'ml': 'naalpathu-ml-v2_master.mp3', 'hi': 'chaalis-hi_master.mp3', 'ta': 'naarpathu-ta_master.mp3'}
NF = '/usr/share/fonts/truetype/noto/'


@functools.lru_cache(None)
def text_img(text, font, size, fill=(236, 228, 210), stroke=5):
    f = ImageFont.truetype(font if font.startswith('/') else NF + font, size)
    d = ImageDraw.Draw(Image.new('RGBA', (10, 10))); bb = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    im = Image.new('RGBA', (bb[2] - bb[0] + 40, bb[3] - bb[1] + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - bb[0], 20 - bb[1]), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=(4, 3, 6, 255))
    a = np.asarray(im).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3:4]


DJ = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


@functools.lru_cache(None)
def row(parts, size, fill, stroke=4):
    """join text pieces horizontally; parts = ((text, font), ...) so Latin bits use a Latin font"""
    ims = [text_img(t, f, size, fill, stroke) for t, f in parts]
    h = max(i[0].shape[0] for i in ims); w = sum(i[0].shape[1] - 24 for i in ims) + 24
    rgb = np.zeros((h, w, 3), np.float32); al = np.zeros((h, w, 1), np.float32); x = 0
    for r, a in ims:
        y = (h - r.shape[0]) // 2; rgb[y:y + r.shape[0], x:x + r.shape[1]] = rgb[y:y + r.shape[0], x:x + r.shape[1]] * (1 - a) + r * a
        al[y:y + r.shape[0], x:x + r.shape[1]] = np.maximum(al[y:y + r.shape[0], x:x + r.shape[1]], a); x += r.shape[1] - 24
    return rgb, al


def mixed(text, font, size, fill, stroke=4):
    parts = []
    for i, piece in enumerate(text.split(' · ')):
        if i: parts.append(('  ·  ', DJ))
        parts.append((piece, font))
    return row(tuple(parts), size, fill, stroke)


def put(fr, img, cx, cy, k=1.0, dx=0):
    rgb, al = img; h, w = rgb.shape[:2]; x = int(cx - w / 2 + dx); y = int(cy - h / 2)
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return fr
    r, a = rgb[y0 - y:y1 - y, x0 - x:x1 - x], al[y0 - y:y1 - y, x0 - x:x1 - x] * k
    fr[y0:y1, x0:x1] = fr[y0:y1, x0:x1] * (1 - a) + r * a; return fr


class Song:
    def __init__(self, lang, P, mode):
        self.lang, self.P, self.mode = lang, P, mode
        self.lines = timed(lang)
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    os.path.join(SONG, SONGF[lang])], capture_output=True, text=True).stdout)
        L = self.lines
        if mode == 'lyric':
            self.s0, self.s1, self.card = 0.0, dur, 9.0          # song range; end card overlaps the outro
            self.length = dur
        else:
            first_forty = next(o for o in L if o['key'] == 'forty')
            self.s0 = max(0.0, L[0]['t0'] - 6.0); self.s1 = first_forty['t1'] + 1.0; self.card = 8.0
            self.length = self.s1 - self.s0 + self.card
        # cut list (song time): intro, one shot per lyric line, fill shots in long gaps, end
        used, cuts = {}, [(0.0, 'intro')]
        def take(k):
            i = used.get(k, 0); used[k] = i + 1; lst = SHOTS[k]; return lst[i % len(lst)]
        self.shots = [(0.0, take('intro'))]
        intro_end = L[0]['t0'] - .3
        if intro_end > 7: self.shots.append((intro_end / 2, take('intro')))
        prev_end = None
        for o in L:
            if prev_end is not None and o['t0'] - prev_end > 4.5: self.shots.append((prev_end + .3, take('fill')))
            self.shots.append((o['t0'] - .3, take(o['key']))); prev_end = o['t1']
        self.shots.append((prev_end + .3, take('zero')))
        self.shots = [(max(0, t), s) for t, s in self.shots]
        self.ev = self.events()
        self.eps = {}

    def events(self):
        ev = {'glitch': [], 'red': [], 'chroma': [], 'flicker': [], 'heart': []}
        for o in self.lines:
            ev['chroma'].append(o['t0'] - .3)
            if o['key'] in CHORUS: ev['glitch'].append((o['t0'] - .32, .14)); ev['red'].append(o['t0'] - .3)
            if o['key'] in ('look', 'count', 'sings', 'behind'): ev['flicker'].append((o['t0'], o['t1']))
            if o['key'] in ('count', 'sings', 'behind'): ev['heart'] += HFX.heartbeats(o['t0'], o['t1'], 80, 120)
            if o['key'] == 'zero': ev['glitch'].append((o['t0'], .5)); ev['red'].append(o['t0'])
        return ev

    def ep(self, n):
        if n not in self.eps:
            if len(self.eps) >= 2: self.eps.pop(next(iter(self.eps)))
            e = s2ep.Ep(n, self.P, self.lang); e.cues = []; e.ev = {}; self.eps[n] = e
        return self.eps[n]

    def shot_frame(self, st):
        i = max(j for j, (t, _) in enumerate(self.shots) if t <= st)
        a = self.shots[i][0]; b = self.shots[i + 1][0] if i + 1 < len(self.shots) else self.s1 + 30
        n, si = self.shots[i][1]; t0, t1 = EPS[n]['segs'][si][:2]
        lo, hi_ = t0 + .7, t1 - .7; span = hi_ - lo; d = b - a
        te = lo + (st - a) * min(1.0, span / max(d, 1e-3)) if d > span else lo + (span - d) / 2 + (st - a)
        fr = self.ep(n).frame(min(max(te, lo), hi_))
        k = seg(st, a, a + .35) * (1 - seg(st, b - .35, b))       # through darkness between shots
        return fr * (0.04 + .96 * k) if i else fr * k

    def lyric(self, fr, st):
        for o in self.lines:
            if o['t0'] <= st < o['t1']:
                k = min(1, (st - o['t0']) / .35, (o['t1'] - st) / .35)
                jit = (HFX.hb(int(st * 24)) - .5) * 6 if o['key'] in CHORUS | {'look', 'behind'} else 0
                col = (205, 40, 30) if o['key'] in ('wake', 'return', 'behind', 'zero') else (236, 228, 210)
                y = H - 205 if self.lang != 'ml' else H - 150
                fr = put(fr, text_img(o['text'], FONT[self.lang], 66, col[::-1] if False else col), W / 2, y, k, jit)
                if self.lang != 'ml':
                    fr = put(fr, text_img(o['en'], '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 38, (200, 196, 186), 4), W / 2, H - 120, k * .95)
        return fr

    def title(self, fr, lt, big=True):
        a = text_img('COUNTDOWN', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 150, (236, 228, 210), 6)
        b = row(((TITLE[self.lang], FONT[self.lang]), ('  ·  FORTY', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf')), 84, (200, 34, 26), 5)
        c = text_img('SEASON 2', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 44, (190, 186, 176), 3)
        k = seg(lt, .2, 1.4); j = (HFX.hb(int(lt * 24) * .7) - .5) * 10 * (1 - seg(lt, 0, 1.2))
        fr = put(fr, a, W / 2, H / 2 - 110, k, j); fr = put(fr, c, W / 2, H / 2 + 5, seg(lt, .8, 1.8)); fr = put(fr, b, W / 2, H / 2 + 110, seg(lt, 1.3, 2.4))
        return fr

    def frame(self, t):
        if self.mode == 'promo' and t >= self.s1 - self.s0:
            lt = t - (self.s1 - self.s0); fr = np.zeros((H, W, 3), np.float32)
            fr = self.title(fr, lt)
            d1, d2 = DATE[self.lang]
            fr = put(fr, mixed(d1, FONT[self.lang], 54, (236, 228, 210), 4), W / 2, H / 2 + 250, seg(lt, 2.2, 3.0))
            fr = put(fr, text_img(d2, '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34, (180, 176, 168), 3), W / 2, H / 2 + 325, seg(lt, 2.6, 3.4))
            fr = put(fr, text_img('@kili_poyi_ai', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30, (150, 146, 140), 3), W / 2, H - 70, seg(lt, 3, 4))
            fr *= 1 - seg(lt, self.card - .8, self.card)
            ev = {'glitch': [(0, .4), (2.2, .12)], 'red': [0.0], 'chroma': [0.0, 2.2]}
            fr = HFX.apply(fr, lt, ev, {})
        else:
            st = self.s0 + t
            fr = self.shot_frame(st)
            if self.mode == 'lyric' and st > self.s1 - self.card:      # end card over the outro
                lt = st - (self.s1 - self.card); fr = fr * (1 - .85 * seg(lt, 0, 1.2))
                fr = self.title(fr, lt)
                d1, d2 = DATE[self.lang]
                fr = put(fr, mixed(d1, FONT[self.lang], 54, (236, 228, 210), 4), W / 2, H / 2 + 250, seg(lt, 2.2, 3.0))
                fr = put(fr, text_img(d2, '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34, (180, 176, 168), 3), W / 2, H / 2 + 325, seg(lt, 2.6, 3.4))
                fr *= 1 - seg(lt, self.card - 1.2, self.card)
            elif st < self.lines[0]['t0'] - .5:
                lt = st - self.s0 - (1.0 if self.mode == 'lyric' else .3); e = self.lines[0]['t0'] - .5 - st
                if lt > 0:
                    w = min(1, e / 1.0); ti = self.title(fr * (1 - .5 * seg(lt, 0, 2)), lt); fr = ti * w + fr * (1 - w)
            fr = HFX.apply(fr, st, self.ev, {})
            fr = self.lyric(fr, st)
            if self.mode == 'promo': fr *= seg(t, 0, 1.0) * (1 - seg(t, self.s1 - self.s0 - 1.2, self.s1 - self.s0))
        fr = np.clip(fr, 0, 1) * B.VIGN + B.GRAIN[int(t * 24) % 6][..., None] * .02
        return np.clip(fr, 0, 1)

    def audio(self, out):
        src = os.path.join(SONG, SONGF[self.lang])
        if self.mode == 'lyric':
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-ar', '48000', out], check=True); return
        bell = os.path.join(S2, 'audio', 'sfx_el', 'bell_toll.mp3'); hit = os.path.join(S2, 'audio', 'sfx_el', 'impact_hit.mp3')
        L = self.s1 - self.s0; ms = int(L * 1000)
        fc = (f"[0:a]atrim={self.s0}:{self.s1},asetpts=PTS-STARTPTS,afade=t=in:d=1,afade=t=out:st={L - 1.5}:d=1.5,apad=pad_dur={self.card}[s];"
              f"[1:a]asetrate=48000*0.89,aresample=48000,adelay={ms}|{ms},volume=0.9[b];[2:a]adelay={ms}|{ms},volume=0.6[h];"
              f"[s][b][h]amix=inputs=3:normalize=0,atrim=0:{self.length},loudnorm=I=-14:TP=-1:LRA=11[o]")
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-i', bell, '-i', hit, '-filter_complex', fc, '-map', '[o]', '-ar', '48000', out], check=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('lang'); ap.add_argument('plates'); ap.add_argument('mode')
    ap.add_argument('--sheet'); ap.add_argument('--out'); a = ap.parse_args()
    s = Song(a.lang, a.plates, a.mode)
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((s.frame(t) * 255).astype(np.uint8), (640, 360)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f"{t:.1f}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 1)
        while len(cells) % 3: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[i:i + 3], 1) for i in range(0, len(cells), 3)], 0)); print('sheet', a.out); return
    vid = os.path.join(SONG, 'video', 'out'); os.makedirs(vid, exist_ok=True)
    out = a.out or os.path.join(vid, f'COUNTDOWN_S2_title_song_{a.mode}_{a.lang}.mp4')
    wav = out[:-4] + '.wav'; s.audio(wav)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                           '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(s.length * FPS)): ff.stdin.write((s.frame(i / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); os.remove(wav); print('wrote', out, f'{s.length:.1f}s')


if __name__ == '__main__':
    main()
