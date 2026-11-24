"""COUNTDOWN S2 · Episodes 2–15 compositor (shared). Usage:
  python3 s2ep.py N PLATES_DIR [--lang ml] [--sheet 1,5,...] [--out file]
Episode timelines are in eps.py; painted plates come from animation-base/src/s2/eps.js."""
import os, sys, math, argparse, subprocess
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ep01 as B, horrorfx as HFX
from eps import EPS

W, H, FPS, DUR = 1920, 1080, 24, 90.0
S2 = B.S2
seg, ease, kf, over = B.seg, B.ease, B.kf, B.over
FADE = .55


def auto_events(E):
    ev = {k: list(v) for k, v in E.get('ev', {}).items()}
    add = lambda k, *v: ev.setdefault(k, []).extend(v)
    add('flash', (2.1, 2, 'cu')); add('glitch', (2.0, .3)); add('red', 2.05); add('chroma', 2.05)
    if E['count'] > 0:
        add('flash', (78.5, 3, 'cu')); add('glitch', (78.38, .6)); add('red', 78.4); add('chroma', 78.4)
        add('heart', *HFX.heartbeats(70.5, 78.3, 118, 150))
    for a, b, b0, b1 in E.get('heart', []): add('heart', *HFX.heartbeats(a, b, b0, b1))
    add('glitch', (80.0, .3))
    return ev


class Ep:
    def __init__(self, n, P):
        self.n, self.E, self.P = n, EPS[n], P
        self.ev = auto_events(self.E)
        self.cache = {}
        self.warn = cv2.imread(os.path.join(P, 'e1_warn', 't0_00.png')).astype(np.float32) / 255
        self.credits = [cv2.imread(os.path.join(P, 'e1_credits', f)).astype(np.float32) / 255 for f in sorted(os.listdir(os.path.join(P, 'e1_credits')))]
        d = os.path.join(P, f"s2_count_{self.E['count']}")
        self.count = [cv2.imread(os.path.join(d, f)).astype(np.float32) / 255 for f in sorted(os.listdir(d))]
        self.scares = HFX.load_scares(P)
        rng = np.random.default_rng(3)
        self.rain = [(rng.random() * W, rng.random() * H, 30 + rng.random() * 50) for _ in range(260)]

    def plate(self, scene, v):
        k = (scene, v)
        if k not in self.cache: self.cache[k] = B.Plate(B.stitch(os.path.join(self.P, f's2e{self.n}_{scene}_{v}'), 2, 2), 0, 0, 2)
        return self.cache[k]

    def variants(self, sched, t):
        """[(variant, weight)] at time t"""
        if sched[0] == 'cycle':
            _, vs, per = sched; i = int(t / per) % len(vs); return [(vs[i], 1.0)]
        out, cur = [], sched[0][1]
        for i, (tv, v) in enumerate(sched):
            if t >= tv: cur = v
        # crossfade from previous variant
        for i in range(1, len(sched)):
            tv, v = sched[i]
            if tv <= t < tv + .35: return [(sched[i - 1][1], 1.0), (v, seg(t, tv, tv + .35))]
        return [(cur, 1.0)]

    def frame(self, t):
        E = self.E
        if 3 <= t < 8:
            fr = self.warn * seg(t - 3, .25, .8) * (1 - seg(t - 3, 4.4, 5.0))
        elif t < 80:
            fr = np.zeros((H, W, 3), np.float32)
            for (t0, t1, scene, sched, keys) in E['segs']:
                if not (t0 <= t < t1): continue
                c = kf(t, keys)
                sx, sy = B.shake(t, 12 * math.exp(-(t - 2.05) * 5)) if 2.05 < t < 3 else (B.shake(t, 10) if t > 78.4 and E['count'] > 0 else (0, 0))
                dr = (math.sin(t * .37) * 6, math.sin(t * .29 + 1) * 4)
                c = (c[0] + (sx + dr[0]) / c[2], c[1] + (sy + dr[1]) / c[2], c[2])
                for v, w in self.variants(sched, t):
                    rgb, al = self.plate(scene, v).view(*c); fr = over(fr, rgb, al, w)
                # through darkness between scenes
                k = 1.0
                if t0 >= 8: k *= seg(t, t0, t0 + FADE)
                if t1 <= 80 and t0 >= 8: k *= 1 - seg(t, t1 - FADE, t1) if t1 < 80 else 1
                if t1 == 3: k *= 1 - seg(t, 2.6, 3.0)
                fr *= k
            for a, b in E.get('rain_up', []):
                if a <= t < b: fr = self.rain_up(fr, t - a)
            for bt in self.ev.get('blink', []):
                if bt <= t < bt + .18: fr *= 0
            fr = B.fog(fr, t, .045)
            if t > 78.4 and E['count'] > 0: fr = fr * (1 - seg(t, 78.8, 79.7))
            if t >= 79.7 and E['count'] > 0: fr *= 0
        elif t < 85:
            lt = t - 80; a, b = self.count; k = 1.15 - .15 * ease(seg(lt, 0, .4))
            sx, sy = B.shake(t, 10 * math.exp(-lt * 6))
            M = np.float32([[k, 0, W / 2 * (1 - k) + sx], [0, k, H / 2 * (1 - k) + sy]])
            img = a * (1 - seg(lt, .35, .7)) + b * seg(lt, .35, .7)
            fr = cv2.warpAffine(img, M, (W, H)) * seg(lt, 0, .25) * (1 - seg(lt, 4.6, 5))
        else:
            lt = t - 85; a, b, c3 = self.credits
            img = a * (1 - seg(lt, .7, 1.4)) + b * seg(lt, .7, 1.4) * (1 - seg(lt, 1.6, 2.3)) + c3 * seg(lt, 1.6, 2.3)
            fr = img * seg(lt, .2, .9) * (1 - seg(lt, 4.4, 5))
        fr = HFX.apply(fr, t, self.ev, self.scares)
        fr = np.clip(fr, 0, 1) * B.VIGN + B.GRAIN[int(t * 24) % 6][..., None] * .022
        return np.clip(fr, 0, 1)

    def rain_up(self, fr, lt):
        fr = fr.copy(); sp = min(1, lt / 6) * 420
        for x, y, l in self.rain:
            yy = (y - lt * sp) % H
            cv2.line(fr, (int(x), int(yy)), (int(x - 4), int(yy + l)), (.85, .8, .75), 1, cv2.LINE_AA)
        return fr


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('n', type=int); ap.add_argument('plates')
    ap.add_argument('--lang', default='ml'); ap.add_argument('--sheet'); ap.add_argument('--out')
    a = ap.parse_args(); ep = Ep(a.n, a.plates)
    if a.sheet:
        ts = [float(x) for x in a.sheet.split(',')]
        cells = [cv2.resize((ep.frame(t) * 255).astype(np.uint8), (480, 270)) for t in ts]
        for c, t in zip(cells, ts): cv2.putText(c, f"{t:.1f}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 1)
        cols = 4; rows = math.ceil(len(cells) / cols)
        while len(cells) < rows * cols: cells.append(np.zeros_like(cells[0]))
        cv2.imwrite(a.out, np.concatenate([np.concatenate(cells[r * cols:(r + 1) * cols], 1) for r in range(rows)], 0)); print('sheet', a.out); return
    out = a.out or os.path.join(S2, 'video', f'COUNTDOWN_S2_ep{a.n:02d}_{a.lang}.mp4')
    audio = os.path.join(S2, 'audio', 'mix', f'ep{a.n:02d}_{a.lang}.wav')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', audio,
                           '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                           '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): ff.stdin.write((ep.frame(i / FPS) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('wrote', out)


if __name__ == '__main__':
    main()
