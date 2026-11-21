"""COUNTDOWN series promo: one ~76 s vertical (9:16) trailer cut to the theme song "Ten Little Chimes" (Malayalam).

Full-screen vertical shots (each 16:9 panel reframed by hand on its subject), a push or drift on every shot, the film look,
short Malayalam story lines on screen, the song's whispered bridge over the Keeper, a bell hit and the title card.
Usage: python3 make_promo.py        (needs animation-base/out/panels_hd and the songs)
"""
import math, os, subprocess
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.abspath(os.path.join(HERE, ".."))
HS = os.path.abspath(os.path.join(V, ".."))
PANELS = os.path.abspath(os.path.join(HS, "..", "animation-base", "out", "panels_hd"))
OUT = os.path.join(V, "promo")
W, H, FPS = 1080, 1920, 24
SW, SH = 1920, 1080
DUR = 76.0
rng = np.random.default_rng(3)

# (start, end, panel, focus x, focus y, move, fx)  — times are song time; focus = subject position in the 16:9 panel
SHOTS = [
    (0.0, 3.0, "e01_p02", .50, .50, "push", ""),
    (3.0, 6.0, "e01_p12", .50, .45, "rise", ""),
    (6.0, 9.5, "e01_p04", .20, .55, "push", ""),
    (9.5, 12.7, "e01_p11", .51, .50, "push", ""),
    (12.7, 15.4, "e01_p10", .34, .50, "push", ""),
    (15.4, 18.05, "e01_p14", .58, .50, "stinger", ""),
    (18.05, 20.7, "e02_p11", .50, .56, "push", ""),
    (20.7, 24.7, "e02_p15", .50, .48, "stinger", ""),
    (24.7, 27.3, "e03_p07", .52, .40, "push", "vhs"),
    (27.3, 30.5, "e03_p06", .50, .45, "push", ""),
    (30.5, 33.2, "e04_p07", .40, .55, "drift", "sepia"),
    (33.2, 36.0, "e04_p08", .52, .50, "push", "sepia"),
    (36.0, 38.8, "e05_p08", .50, .55, "push", "phone"),
    (38.8, 42.0, "e05_p11", .50, .35, "stinger", "phone"),
    (42.0, 44.8, "e06_p04", .50, .55, "drift", ""),
    (44.8, 47.9, "e06_p10", .50, .45, "push", ""),
    (47.9, 50.8, "e07_p06", .74, .45, "push", ""),
    (50.8, 53.9, "e07_p12", .50, .55, "push", ""),
    (53.9, 56.6, "e08_p03", .50, .55, "push", ""),
    (56.6, 59.9, "e08_p13", .62, .45, "rise", ""),
    (59.9, 62.7, "e09_p04", .45, .50, "drift", ""),
    (62.7, 66.4, "e09_p12", .62, .50, "push", ""),
    (66.4, 69.0, "e10_p05", .50, .42, "push", ""),
    (69.0, 71.6, "e10_p09", .62, .45, "stinger", ""),
    (71.6, 76.0, "e01_p02", .50, .50, "title", ""),
]
# on-screen story lines (Malayalam): (start, end, text)
LINES = [
    (3.2, 6.0, "മഞ്ഞുമലയിലെ ഗോപുരം\\Nനാൽപതു വർഷമായി നിശ്ശബ്ദമായിരുന്നു."),
    (6.4, 12.4, "ഒരു രാത്രി, പുലർച്ചെ 3 മണിക്ക്...\\Nഅത് പത്തു തവണ മുഴങ്ങി."),
    (12.9, 18.0, "മീര മാത്രം അത് കേട്ടു."),
    (18.3, 24.5, "ഓരോ രാത്രിയും ഒരു മണി കുറയും.\\Nഓരോ രാത്രിയും ഒരാൾ അപ്രത്യക്ഷമാകും."),
    (24.9, 30.3, "ആരും അവരെ ഓർക്കില്ല."),
    (45.0, 47.8, "അവൻ ഒരിക്കലും ഓടില്ല."),
    (48.0, 50.7, "...പക്ഷേ എപ്പോഴും\\Nകൂടുതൽ അടുത്തായിരിക്കും."),
    (60.1, 66.2, "എണ്ണം പൂജ്യമാകുമ്പോൾ\\Nകേട്ടവരെല്ലാം അവന്റേത്."),
]
HITS = [(0.0, 1.0), (15.4, .7), (20.7, .9), (38.8, .6), (69.0, .7), (71.6, 1.0)]   # camera shake + flash, on the bell hits

ease = lambda x: x * x * (3 - 2 * x)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .6 * np.clip(((xx - W / 2) / (W * .7)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2, 0, 1) ** 1.3)[..., None]
GRAIN = [cv2.resize((rng.standard_normal((H // 2, W // 2)) * 5.5).astype(np.float32), (W, H))[..., None] for _ in range(8)]
LUT = np.clip(255 * (np.linspace(0, 1, 256) ** 1.08 * 1.04 - .015), 0, 255).astype(np.uint8)


def frame_of(img, fx, fy, z, sx, sy):
    cw, ch = SH * W / H / z, SH / z                     # crop window in panel pixels (9:16)
    cx = min(max(fx * SW, cw / 2), SW - cw / 2) + sx
    cy = min(max(fy * SH, ch / 2), SH - ch / 2) + sy
    s = W / cw
    M = np.array([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


def look(img, t, fr, fx, flash):
    f = img.astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    f = lum + (f - lum) * (.55 if fx == "sepia" else .86)
    if fx == "sepia": f *= np.array([.78, .92, 1.08], np.float32)
    else: f[..., 0] += 6; f[..., 2] -= 4
    f = f * VIG * (1 + .018 * math.sin(t * 37.1) * math.sin(t * 11.3)) + GRAIN[(fr // 2) % 8] * (1.6 if fx == "sepia" else 1)
    if flash > 0: f += (255 - f) * min(.8, flash)
    out = cv2.LUT(np.clip(f, 0, 255).astype(np.uint8), LUT)
    if fx in ("vhs", "phone") and rng.random() < .4:
        for _ in range(4):
            y = int(rng.random() * H); h = int(6 + rng.random() * 50)
            out[y:y + h] = np.roll(out[y:y + h], int(rng.normal(0, 30)), axis=1)
    if fx == "phone": out[::4] = (out[::4] * .86).astype(np.uint8)
    return out


def ass(path):
    t = lambda s: f"0:{int(s // 60):02d}:{s % 60:05.2f}"
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Line,Noto Sans Malayalam,60,&H00F0F4F6,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,4,3,2,70,70,330,1
Style: Title,Permanent Marker,150,&H00D0E2E9,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,8,0,1,0,8,5,40,40,0,1
Style: TitleMl,Noto Sans Malayalam,78,&H00C9D2DA,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,4,5,40,40,0,1
Style: Info,Noto Sans Malayalam,52,&H003A3AD3,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Cta,Noto Sans Malayalam,46,&H00D8E8FF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,3,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{t(a)},{t(b)},Line,,0,0,0,,{{\\fad(250,300)}}{x}" for a, b, x in LINES]
    ev += [f"Dialogue: 0,{t(71.9)},{t(DUR)},Title,,0,0,0,,{{\\fad(400,0)\\pos(540,1420)}}COUNTDOWN",
           f"Dialogue: 0,{t(72.4)},{t(DUR)},TitleMl,,0,0,0,,{{\\fad(400,0)\\pos(540,1560)}}കൗണ്ട്ഡൗൺ",
           f"Dialogue: 0,{t(73.0)},{t(DUR)},Info,,0,0,0,,{{\\fad(400,0)\\pos(540,1690)}}10 എപ്പിസോഡുകൾ · ഉടൻ വരുന്നു",
           f"Dialogue: 0,{t(73.6)},{t(DUR)},Cta,,0,0,0,,{{\\fad(400,0)\\pos(540,1790)}}Follow ചെയ്യൂ · ഓരോ രാത്രിയും ഒരു മണി കുറയും"]
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    imgs = {s[2]: cv2.imread(os.path.join(PANELS, s[2] + ".jpg")) for s in SHOTS}
    assert all(v is not None for v in imgs.values()), "render HD panels first (see video/README.md)"
    sub = os.path.join(OUT, "promo.ass"); ass(sub)
    song = os.path.join(HS, "audio", "songs", "ten-little-chimes-ml.mp3")
    bell = os.path.join(HS, "audio", "sfx", "chime_tower_bell.wav")
    out = os.path.join(OUT, "COUNTDOWN_promo_ml.mp4")
    fc = (f"[0:v]ass='{sub}':fontsdir={os.path.join(HERE, 'fonts')}[v];"
          f"[1:a]atrim=0:{DUR},afade=t=out:st=72.2:d=3.8,volume=1.0[s];"
          f"[2:a]adelay=71600|71600,volume=0.9[b];[s][b]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", song, "-i", bell, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-maxrate", "6M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", str(DUR), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(DUR * FPS)):
        t = fr / FPS
        a, b, pid, fx_, fy_, move, fx = next(s for s in SHOTS if s[0] <= t < s[1] or s is SHOTS[-1])
        k = (t - a) / (b - a); e = ease(min(1, k))
        z = {"push": 1.0 + .10 * e, "rise": 1.06, "drift": 1.08, "stinger": 1.0 + .25 * k ** 3, "title": 1.0 + .05 * e}[move]
        dx = {"drift": (-.05 + .1 * e) * SW}.get(move, 0)
        dy = {"rise": (.06 - .12 * e) * SH}.get(move, 0)
        sx = sy = flash = 0.0
        for ht, s in HITS:
            d = t - ht
            if 0 <= d < 1.0:
                amp = s * math.exp(-d * 5); sx += amp * 10 * math.sin(d * 63); sy += amp * 7 * math.cos(d * 51)
                if d < .12: flash = max(flash, .35 * s * (1 - d / .12))
        img = frame_of(imgs[pid], fx_, fy_, z, dx + sx, dy + sy)
        img = look(img, t, fr, fx, flash)
        dip = min(1.0, t / .8, (t - a) / .25 + .0 if move == "title" else 1.0)
        if b - t < .12 and move != "title": dip = min(dip, .35 + (b - t) / .12 * .65)   # tiny dip between shots, on the cut
        if t > DUR - .6: dip = min(dip, (DUR - t) / .6)
        if move == "title": dip = min(dip, .5)
        if dip < 1: img = (img * max(0, dip)).astype(np.uint8)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "16.0", "-i", out, "-frames:v", "1", "-q:v", "3", os.path.join(OUT, "COUNTDOWN_promo_cover.jpg")], check=True)
    os.remove(sub)
    print("wrote", os.path.relpath(out, V))


if __name__ == "__main__":
    main()
