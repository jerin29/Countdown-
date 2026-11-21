"""COUNTDOWN cinematic animatics: storyboard panels + camera moves + film look, cut to each 1:30 soundtrack.

For each episode: every panel holds from its script timecode to the next one, with a slow camera move (push, pull,
drift or a fast stinger push). On top: a dark film grade, grain, gate flicker, vignette, 2:1 letterbox, a camera shake
and flash on every bell chime and impact (read from the audio mixer's cue sheets, so picture hits land on the sound),
VHS glitches on Neha and the phone-footage episode, and a scratched old-film look on the sepia flashbacks.
Malayalam subtitles are muxed as a soft track (and written as .srt).

Usage: python3 make_animatic.py [episode numbers...]     (needs: numpy, opencv-python-headless, soundfile, ffmpeg)
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
HS = os.path.abspath(os.path.join(HERE, "..", ".."))                       # horror-series/
LANG = os.environ.get("COUNTDOWN_LANG", "ml")                                # ml, or hi (Hindi audio + English subtitles)
PANELS = os.path.abspath(os.path.join(HS, "..", "animation-base", "out", "panels_hd" if LANG == "ml" else f"panels_hd_{LANG}"))
AUDIO = os.path.join(HS, "audio")
OUT = os.path.join(HS, "video")
sys.path.insert(0, os.path.join(AUDIO, "tools"))
import mix_episodes as MIX                                                   # cue sheets (times of chimes, lines)

W, H, FPS, DUR = 1920, 1080, 24, 90.0
BAR = 60                                                                    # letterbox: 1920x960 = 2:1
rng = np.random.default_rng(7)

# ---- per-panel direction (episode -> {panel number: (move, fx)}) ----
#  moves: push, pushL, pushR, pull, driftL, driftR, rise, sink, stinger, hold, title, end
#  fx: vhs, phone, sepia, flicker
DIRECT = {
    1: {1: ('hold', ''), 2: ('push', ''), 3: ('title', ''), 4: ('pushL', ''), 5: ('push', ''), 6: ('push', ''), 7: ('driftR', ''),
        8: ('push', ''), 9: ('push', ''), 10: ('pushL', ''), 11: ('push', ''), 12: ('rise', ''), 13: ('pull', ''), 14: ('stinger', ''), 15: ('hold', ''), 16: ('end', '')},
    2: {1: ('push', ''), 2: ('title', ''), 3: ('driftR', ''), 4: ('pushL', ''), 5: ('push', ''), 6: ('push', ''), 7: ('driftL', ''), 8: ('push', ''),
        9: ('pushR', ''), 10: ('push', ''), 11: ('stinger', ''), 12: ('driftL', ''), 13: ('push', ''), 14: ('stinger', ''), 15: ('pull', 'flicker'), 16: ('end', '')},
    3: {1: ('push', ''), 2: ('title', ''), 3: ('push', ''), 4: ('push', ''), 5: ('push', ''), 6: ('push', ''), 7: ('pushR', 'vhs'), 8: ('push', 'vhs'),
        9: ('pull', ''), 10: ('push', 'vhs'), 11: ('push', ''), 12: ('push', 'vhs'), 13: ('stinger', ''), 14: ('end', '')},
    4: {1: ('push', 'sepia'), 2: ('title', ''), 3: ('driftR', ''), 4: ('push', ''), 5: ('push', ''), 6: ('driftL', 'sepia'), 7: ('pushR', 'sepia'),
        8: ('stinger', 'sepia'), 9: ('push', ''), 10: ('push', ''), 11: ('pushR', ''), 12: ('stinger', ''), 13: ('end', '')},
    5: {1: ('hold', 'phone'), 2: ('title', 'phone'), 3: ('driftL', 'phone'), 4: ('push', 'phone'), 5: ('push', 'phone'), 6: ('push', 'phone'),
        7: ('hold', 'phone'), 8: ('push', 'phone'), 9: ('hold', 'phone'), 10: ('hold', 'phone'), 11: ('stinger', 'phone'), 12: ('hold', 'phone'), 13: ('end', '')},
    6: {1: ('rise', ''), 2: ('title', ''), 3: ('push', ''), 4: ('driftR', ''), 5: ('push', ''), 6: ('push', ''), 7: ('driftL', ''), 8: ('push', ''),
        9: ('pull', 'flicker'), 10: ('stinger', ''), 11: ('driftR', ''), 12: ('push', ''), 13: ('end', '')},
    7: {1: ('hold', 'vhs'), 2: ('title', ''), 3: ('push', ''), 4: ('push', ''), 5: ('pushR', ''), 6: ('push', ''), 7: ('push', ''), 8: ('push', ''),
        9: ('push', ''), 10: ('pull', ''), 11: ('hold', ''), 12: ('stinger', ''), 13: ('end', '')},
    8: {1: ('driftR', ''), 2: ('title', ''), 3: ('push', ''), 4: ('push', ''), 5: ('driftL', ''), 6: ('push', ''), 7: ('pushR', ''), 8: ('push', ''),
        9: ('push', ''), 10: ('push', ''), 11: ('push', ''), 12: ('push', ''), 13: ('pull', ''), 14: ('end', '')},
    9: {1: ('rise', ''), 2: ('title', ''), 3: ('rise', ''), 4: ('push', ''), 5: ('push', ''), 6: ('push', 'vhs'), 7: ('rise', ''), 8: ('push', 'flicker'),
        9: ('push', 'flicker'), 10: ('push', ''), 11: ('push', ''), 12: ('stinger', ''), 13: ('end', '')},
    10: {1: ('hold', ''), 2: ('title', ''), 3: ('push', ''), 4: ('push', ''), 5: ('stinger', ''), 6: ('sink', ''), 7: ('push', ''), 8: ('pull', 'vhs'),
         9: ('stinger', ''), 10: ('pull', ''), 11: ('driftR', ''), 12: ('push', ''), 13: ('push', ''), 14: ('end', '')},
}

ease = lambda x: x * x * (3 - 2 * x)
easeIn = lambda x: x ** 3


def tsec(tc):
    m, s = tc.split(":"); return int(m) * 60 + int(s)


def camera(move, k, dur):
    """-> (zoom, cx, cy) with cx, cy as fractions of the frame (0.5 = centre)."""
    e = ease(k)
    a = min(1.0, 6.0 / max(dur, 1.0))   # longer holds move a little less per second
    return {
        'push': (1.02 + .08 * e, .5, .5), 'pushL': (1.03 + .08 * e, .5 - .03 * e, .5), 'pushR': (1.03 + .08 * e, .5 + .03 * e, .5),
        'pull': (1.12 - .09 * e, .5, .5), 'driftL': (1.08, .53 - .06 * e, .5), 'driftR': (1.08, .47 + .06 * e, .5),
        'rise': (1.10, .5, .55 - .1 * e), 'sink': (1.10, .5, .45 + .1 * e), 'hold': (1.03 + .01 * e, .5, .5),
        'stinger': (1.0 + .22 * easeIn(k), .5, .48), 'title': (1.0 + .05 * e, .5, .5), 'end': (1.0 + .02 * e, .5, .5),
    }[move]


def hits(ep):
    """Picture hits from the audio cue sheet: (time, strength)."""
    out = []
    for at, src, gain, opts in MIX.EP[ep]:
        if "chime_tower_bell_distant" in src: out.append((at, .35 * gain))
        elif "chime_tower_bell" in src: out.append((at, 1.0 * gain))
        elif any(k in src for k in ("impact", "violin_screech", "clunk", "lights_snap", "corridor_lights", "chain_snap", "sub_hit")): out.append((at, .8 * gain))
    return out


def subtitles_en(ep):
    en = json.load(open(os.path.join(AUDIO, f"voice_{LANG}", "subtitles_en.json"), encoding="utf-8"))
    subs = []
    for at, src, gain, opts in MIX.cues(ep)[0]:
        if src.startswith("v:"):
            d = sf.info(os.path.join(AUDIO, f"voice_{LANG}", "processed", src[2:] + ".wav")).duration
            subs.append((at, at + d + .3, en[src[2:]]))
    for key, text in en["_screen"].items():
        e, m, sec = key.split(":")
        if int(e) == ep:
            a = int(m) * 60 + int(sec) + .3
            subs.append((a, a + 3.2, text))
    subs.sort()
    fmt = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    return "\n".join(f"{i + 1}\n{fmt(a)} --> {fmt(min(b, subs[i + 1][0] - .05) if i + 1 < len(subs) else b)}\n{t}\n" for i, (a, b, t) in enumerate(subs))


def subtitles(ep):
    if LANG != "ml":
        return subtitles_en(ep)
    lines = {}
    for v in json.load(open(os.path.join(AUDIO, "voice", "lines.json"), encoding="utf-8")).values():
        for name, text in v:
            lines[name] = text
    subs = []
    for at, src, gain, opts in MIX.EP[ep]:
        if src.startswith("v:"):
            name = src[2:]
            d = sf.info(os.path.join(AUDIO, "voice", "processed", name + ".wav")).duration
            who = {"meera": "മീര", "arjun": "അർജുൻ", "ammachi": "അമ്മച്ചി", "neha": "നേഹ", "keeper": "കാവൽക്കാരൻ", "mom": "അമ്മ", "teacher": "ടീച്ചർ",
                   "elias": "ഏലിയാസ്", "meeravoice": "ഫോണിൽ", "reflection": "പ്രതിബിംബം"}[name.split("_")[1]]
            text = lines[name].replace("ആയിരത്തിത്തൊള്ളായിരത്തി നാൽപ്പത്തിയാറിൽ", "1946-ൽ").replace("ആയിരത്തിത്തൊള്ളായിരത്തി എൺപത്തിയാറിൽ", "1986-ൽ")
            subs.append((at, at + d + .3, f"{who}: {text}"))
    subs.sort()
    fmt = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    srt = "\n".join(f"{i + 1}\n{fmt(a)} --> {fmt(min(b, subs[i + 1][0] - .05) if i + 1 < len(subs) else b)}\n{t}\n" for i, (a, b, t) in enumerate(subs))
    return srt


# ---- film look (precomputed) ----
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .55 * np.clip(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2, 0, 1) ** 1.3)[..., None]
GRAIN = [(rng.standard_normal((H // 2, W // 2)) * 5.5).astype(np.float32) for _ in range(8)]
GRAIN = [cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None] for g in GRAIN]
LUT = np.clip(255 * (np.linspace(0, 1, 256) ** 1.08 * 1.04 - .015), 0, 255).astype(np.uint8)   # gentle crush + lift


def grade(img, t, fx, flash, frame):
    f = img.astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    f = lum + (f - lum) * (.55 if fx == 'sepia' else .86)                 # desaturate
    if fx == 'sepia':
        f = f * np.array([.78, .92, 1.08], np.float32)                     # BGR warm
    else:
        f[..., 0] += 6; f[..., 2] -= 4                                     # cold shadows (BGR)
    flick = 1 + .018 * math.sin(t * 37.1) * math.sin(t * 11.3) + (.06 * (rng.random() - .5) if fx in ('sepia', 'flicker') else 0)
    f = f * VIG * flick + GRAIN[(frame // 2) % 8] * (1.6 if fx == 'sepia' else 1.0)
    if flash > 0:
        f = f + (255 - f) * min(.85, flash)
    out = cv2.LUT(np.clip(f, 0, 255).astype(np.uint8), LUT)
    if fx == 'sepia' and rng.random() < .3:                                 # scratches and dust
        x = int(rng.random() * W); cv2.line(out, (x, 0), (x + int(rng.normal(0, 20)), H), (200, 210, 220), 1)
        for _ in range(3): cv2.circle(out, (int(rng.random() * W), int(rng.random() * H)), int(rng.random() * 3) + 1, (30, 30, 30), -1)
    return out


def vhs(img, k, phone=False):
    out = img
    if rng.random() < (.35 if phone else .6) * k:
        out = img.copy()
        for _ in range(int(2 + 6 * k)):
            y = int(rng.random() * H); h = int(4 + rng.random() * 40); s = int(rng.normal(0, 40 * k))
            out[y:y + h] = np.roll(out[y:y + h], s, axis=1)
        b, g, r = cv2.split(out)
        out = cv2.merge([np.roll(b, -4, axis=1), g, np.roll(r, 4, axis=1)])
    if phone:                                                               # compression mush + scanlines
        small = cv2.resize(out, (W // 3, H // 3), interpolation=cv2.INTER_AREA)
        out = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
        out[::4] = (out[::4] * .86).astype(np.uint8)
    return out


def render(ep):
    idx = [p for p in json.load(open(os.path.join(PANELS, "index.json"), encoding="utf-8")) if p["ep"] == ep]
    starts = [tsec(p["tc"]) for p in idx] + [DUR]
    imgs = [cv2.imread(os.path.join(PANELS, p["file"])) for p in idx]
    assert all(i is not None for i in imgs), "missing HD panels: render them first"
    H_ = hits(ep)
    os.makedirs(os.path.join(OUT, "subs"), exist_ok=True)
    sub_tag = "ml" if LANG == "ml" else "en"
    odir = OUT if LANG == "ml" else os.path.join(OUT, LANG)
    os.makedirs(os.path.join(odir, "subs"), exist_ok=True)
    srt = os.path.join(odir, "subs", f"COUNTDOWN_ep{ep:02d}_{sub_tag}.srt")
    open(srt, "w", encoding="utf-8").write(subtitles(ep))
    audio = os.path.join(AUDIO, "episodes" if LANG == "ml" else f"episodes_{LANG}", f"COUNTDOWN_ep{ep:02d}_soundtrack_{LANG}.mp3")
    out = os.path.join(odir, f"COUNTDOWN_ep{ep:02d}_cinematic_{LANG}.mp4")
    burn = [] if LANG == "ml" else ["-vf", f"subtitles='{srt}':force_style='FontName=Noto Sans,FontSize=17,Bold=1,PrimaryColour=&H00F2F5F7,OutlineColour=&H00101010,BorderStyle=1,Outline=1.6,Shadow=0.8,MarginV=34'"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", audio, "-i", srt, "-map", "0:v", "-map", "1:a", "-map", "2:s",
                           *burn, "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-x264-params", "aq-mode=3:deblock=1,1", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-c:s", "mov_text", "-metadata:s:s:0", f"language={'mal' if LANG == 'ml' else 'eng'}", "-metadata:s:s:0", f"title={'മലയാളം' if LANG == 'ml' else 'English'}",
                           "-movflags", "+faststart", "-t", str(DUR), out], stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for fr in range(n):
        t = fr / FPS
        i = max(j for j in range(len(idx)) if starts[j] <= t + 1e-6)
        t0, t1 = starts[i], starts[i + 1]
        k = (t - t0) / max(.01, t1 - t0)
        move, fx = DIRECT.get(ep, {}).get(i + 1, ('push', ''))
        z, cx, cy = camera(move, k, t1 - t0)
        # hits: shake + flash
        shake, flash = [0.0, 0.0], 0.0
        for ht, s in H_:
            d = t - ht
            if 0 <= d < 1.2:
                a = s * math.exp(-d * 5)
                shake[0] += a * 14 * math.sin(d * 63); shake[1] += a * 10 * math.cos(d * 51)
                if s > .5 and d < .12: flash = max(flash, .35 * s * (1 - d / .12))
        if move == 'stinger':
            shake[0] += 3 * easeIn(k) * math.sin(t * 90); shake[1] += 3 * easeIn(k) * math.cos(t * 77)
        z = max(z, 1.0 + (abs(shake[0]) + abs(shake[1])) / 500)            # never show an edge
        M = np.array([[z, 0, W / 2 - z * W * cx + shake[0]], [0, z, H / 2 - z * H * cy + shake[1]]], np.float32)
        img = cv2.warpAffine(imgs[i], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # transitions: fade in from black at the top, dips around title and end cards, cross-dissolve into flashbacks
        dip = 1.0
        if t < .8: dip = ease(t / .8)
        if move in ('title', 'end') and t - t0 < .35: dip = min(dip, ease((t - t0) / .35))
        nxt = DIRECT.get(ep, {}).get(i + 2, ('', ''))
        if nxt[0] in ('title', 'end') and t1 - t < .3: dip = min(dip, ease((t1 - t) / .3))
        if t > DUR - 1.2: dip = min(dip, ease((DUR - t) / 1.2))
        if nxt[1] == 'sepia' and fx != 'sepia' and t1 - t < .6:            # dissolve into the past
            M2 = np.array([[1.02, 0, -W * .01], [0, 1.02, -H * .01]], np.float32)
            img = cv2.addWeighted(img, (t1 - t) / .6, cv2.warpAffine(imgs[i + 1], M2, (W, H)), 1 - (t1 - t) / .6, 0)
        if fx in ('vhs', 'phone'):
            img = vhs(img, .7 if fx == 'vhs' else .5, phone=(fx == 'phone'))
        img = grade(img, t, fx, flash, fr)
        if dip < 1: img = (img * dip).astype(np.uint8)
        img[:BAR] = 0; img[H - BAR:] = 0                                    # letterbox
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print("wrote", os.path.relpath(out, HS))


if __name__ == "__main__":
    eps = [int(a) for a in sys.argv[1:]] or list(range(1, 11))
    for ep in eps:
        render(ep)
