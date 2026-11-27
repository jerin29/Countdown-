"""COUNTDOWN — official lyric video for the full title song "പത്തു മണിയൊച്ച" (2:59, 16:9 1080p).

Picture: the series' panels, each section of the song on its part of the story (verse 1 = Ep 1–4, chorus = the Keeper,
verse 2 = Ep 5–8, bridge = the 1946 legend in sepia, verse 3 + final chorus = the finale, outro = the season 2 hook),
with slow camera moves and the film look. Text: each Malayalam line large in the lower third as it is sung, with its
English meaning underneath. Line times come from lyric_times.json (aligned to the recording).
Usage: python3 make_lyric_video.py [--vertical]
"""
import json, math, os, subprocess, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.abspath(os.path.join(HERE, ".."))
HS = os.path.abspath(os.path.join(V, ".."))
PANELS = os.path.abspath(os.path.join(HS, "..", "animation-base", "out", "panels_hd"))
SONG = os.path.join(HS, "audio", "songs", "ten-little-chimes-FULL-ml_master.mp3")
OUT = os.path.join(V, "lyric")
W, H, FPS = 1920, 1080, 24
DUR = 179.1
rng = np.random.default_rng(11)

# (song start, panel, move, fx) — each shot lasts until the next one starts
SHOTS = [
    (0.0, "e01_p01", "hold", ""), (4.0, "e01_p02", "push", ""), (9.0, "e01_p12", "rise", ""), (14.0, "e01_p06", "push", ""),
    # verse 1 (Ep 1–4)
    (21.0, "e01_p10", "push", ""), (24.5, "e01_p14", "push", ""), (28.0, "e02_p11", "push", ""), (31.0, "e02_p15", "push", ""),
    (35.0, "e03_p07", "pushR", "vhs"), (38.5, "e03_p06", "push", ""), (42.0, "e03_p13", "push", ""),
    # chorus 1 (the Keeper)
    (47.0, "e05_p06", "push", "phone"), (51.0, "e05_p08", "push", "phone"), (55.0, "e06_p10", "push", ""), (59.0, "e01_p13", "pull", ""),
    (63.0, "e09_p07", "rise", ""), (67.0, "e05_p11", "push", "phone"),
    # verse 2 (Ep 5–8)
    (72.5, "e05_p04", "push", "phone"), (76.5, "e06_p05", "push", ""), (80.5, "e06_p07", "driftL", ""), (84.5, "e07_p06", "push", ""),
    (88.5, "e08_p03", "push", ""), (92.0, "e08_p09", "push", ""),
    # chorus 2
    (95.0, "e08_p01", "driftR", ""), (99.0, "e03_p12", "push", "vhs"), (103.0, "e06_p09", "pull", ""), (107.0, "e09_p12", "push", ""),
    (111.0, "e08_p13", "rise", ""), (115.0, "e09_p04", "push", ""),
    # bridge (the 1946 legend)
    (121.0, "e04_p06", "driftL", "sepia"), (126.0, "e04_p07", "pushR", "sepia"), (131.0, "e04_p08", "push", "sepia"), (135.5, "e04_p12", "push", ""),
    # verse 3 (finale)
    (139.0, "e09_p10", "push", ""), (142.5, "e09_p11", "push", ""), (145.0, "e10_p07", "push", ""), (148.5, "e10_p08", "pull", "vhs"),
    # final chorus
    (152.0, "e10_p09", "push", ""), (156.0, "e10_p10", "pull", ""), (160.0, "e10_p11", "driftR", ""), (164.0, "e10_p12", "push", ""),
    (168.0, "e10_p13", "push", ""),
    # outro
    (172.0, "e10_p01", "hold", ""), (175.0, "e01_p02", "pull", ""),
]
MEAN = {  # English meaning per Malayalam line (shown small)
    "ആരിരാരോ... ആരാരിരാരോ...": "(lullaby hum)",
    "പത്തു മണിയൊച്ച മേലേ ഗോപുരത്തിൽ": "Ten chimes in the tower high",
    "ഒൻപത് പോയവർക്കായ് ഇരുളിൻ നടുവിൽ": "Nine for the ones who left, deep in the dark",
    "എട്ട് നീല റിബ്ബൺ കെട്ടിയ പെണ്ണിനായ്": "Eight for the girl with the blue ribbons",
    "ഏഴ് ഒന്നുമറിയാത്ത കൂട്ടുകാരനായ്": "Seven for the friend who never knew",
    "എണ്ണരുതേ, എണ്ണരുതേ, മണിയൊച്ച കേട്ടാലും": "Don't count, don't count, even if you hear the bells",
    "തിരിയരുതേ, തിരിയരുതേ, പിന്നിൽ നിഴൽ വന്നാലും": "Don't turn around, even if a shadow comes behind you",
    "മൂന്നു മണിക്കവൻ വരും, മഞ്ഞിലൂടെ മെല്ലെ": "At three o'clock he comes, slowly through the mist",
    "ആരിരാരോ പാടിയുറങ്ങ്... അവൻ കേൾക്കും മെല്ലെ": "Sing aariraro and sleep... he is listening",
    "ആറ് മഞ്ഞുമൂടും വഴിയോരത്ത്": "Six on the road where the fog rolls in",
    "അഞ്ച് പേരെഴുതിയ ഘടികാരത്തിൽ": "Five in the clock with a name",
    "നാല് നീ കാണാത്ത നാഴികകൾ": "Four for the hours you'll never find",
    "മൂന്ന് ആടിയാടും ഒഴിഞ്ഞ കസേര": "Three for the empty chair that rocks",
    "പണ്ടൊരു ഘടികാരപ്പണിക്കാരൻ...": "Long ago, a clockmaker...",
    "ചെയ്യാത്ത കുറ്റത്തിന് അവനെ പൂട്ടിയിട്ടു...": "locked away for a crime he never did...",
    "പുലർച്ചെ മൂന്നു മണിക്ക് അവൻ മരിച്ചു...": "he died at three in the morning...",
    "“നിങ്ങളെടുത്ത ഓരോ നിമിഷവും... ഞാൻ തിരിച്ചെടുക്കും...”": "\"Every moment you took... I will take back.\"",
    "രണ്ട് കുഞ്ഞുഹൃദയം പിച്ചളച്ചക്രത്തിൽ": "Two little hearts in the gears of brass",
    "ഒന്ന്... അവസാനത്തെ മണിയൊച്ചയിൽ": "One... at the very last chime",
    "പിന്നോട്ട് ചുറ്റൂ, മെല്ലെ ചുറ്റൂ": "Wind it back, slowly wind it back",
    "കാലം മടങ്ങിവരും, ഇരുൾ മായും": "Time will return, the darkness will fade",
    "എണ്ണരുതേ, എണ്ണരുതേ, മണിയൊച്ച തീർന്നാലും": "Don't count, don't count, even when the bells are done",
    "ഉറങ്ങിക്കോ, ഉറങ്ങിക്കോ, പുലരി വന്നാലും": "Sleep now, sleep, even when the dawn comes",
    "നാൽപതാണ്ടു കഴിയുമ്പോൾ ഗോപുരം ഉണരും": "When forty years pass, the tower will wake",
    "ആരിരാരോ... അന്നവൻ വീണ്ടും നിന്നെ തിരയും": "Aariraro... and he will come looking for you again",
    "കണ്ണടച്ചുറങ്ങൂ എൻ പൊന്നോമനേ...": "Close your eyes and sleep, my darling...",
    "മൂന്നു മണിക്കവൻ വരുമല്ലോ... ഇന്ന്.": "at three o'clock he's coming... tonight.",
}

ease = lambda x: x * x * (3 - 2 * x)
easeIn = lambda x: x ** 3
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .55 * np.clip(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2, 0, 1) ** 1.3)[..., None]
GRAIN = [cv2.resize((rng.standard_normal((H // 2, W // 2)) * 5).astype(np.float32), (W, H))[..., None] for _ in range(8)]
LUT = np.clip(255 * (np.linspace(0, 1, 256) ** 1.08 * 1.04 - .015), 0, 255).astype(np.uint8)
# darken the lower third so the lyrics always read
SHADE = np.ones((H, W, 1), np.float32)
SHADE[int(H * .55):] = np.linspace(1, .45, H - int(H * .55))[:, None, None]


def camera(move, k):
    e = ease(k)
    return {"push": (1.02 + .07 * e, .5, .5), "pushR": (1.03 + .07 * e, .5 + .03 * e, .5), "pull": (1.10 - .08 * e, .5, .5),
            "driftL": (1.08, .53 - .06 * e, .5), "driftR": (1.08, .47 + .06 * e, .5), "rise": (1.10, .5, .55 - .1 * e),
            "hold": (1.03 + .01 * e, .5, .5)}[move]


def look(img, t, fr, fx):
    f = img.astype(np.float32)
    lum = f.mean(axis=2, keepdims=True)
    f = lum + (f - lum) * (.55 if fx == "sepia" else .86)
    if fx == "sepia": f *= np.array([.78, .92, 1.08], np.float32)
    else: f[..., 0] += 6; f[..., 2] -= 4
    f = f * VIG * SHADE * (1 + .018 * math.sin(t * 37.1) * math.sin(t * 11.3)) + GRAIN[(fr // 2) % 8]
    out = cv2.LUT(np.clip(f, 0, 255).astype(np.uint8), LUT)
    if fx in ("vhs", "phone") and rng.random() < .3:
        for _ in range(3):
            y = int(rng.random() * H); h = int(4 + rng.random() * 30)
            out[y:y + h] = np.roll(out[y:y + h], int(rng.normal(0, 25)), axis=1)
    return out


def ass(path, lines, vertical):
    t = lambda s: f"0:{int(s // 60):02d}:{s % 60:05.2f}"
    rx, ry = (1080, 1920) if vertical else (1920, 1080)
    mv, mv2 = (420, 360) if vertical else (150, 95)
    fs, fs2 = (66, 34) if vertical else (68, 34)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {rx}
PlayResY: {ry}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ml,Noto Sans Malayalam,{fs},&H00F2F5F7,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,3,3,2,80,80,{mv},1
Style: En,Noto Sans,{fs2},&H00A9B8C6,&H000000FF,&H00101010,&H96000000,0,1,0,0,100,100,0,0,1,2,2,2,80,80,{mv2},1
Style: Title,Permanent Marker,{130 if not vertical else 140},&H00D0E2E9,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,8,0,1,0,8,5,40,40,0,1
Style: Sub,Noto Sans Malayalam,{54},&H00C9D2DA,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,4,5,40,40,0,1
Style: Credit,Noto Sans Malayalam,{34},&H0090A0B0,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    cx, cy = rx // 2, ry // 2
    ev = [f"Dialogue: 0,{t(.6)},{t(11.0)},Title,,0,0,0,,{{\\fad(800,800)\\pos({cx},{cy - 60})}}COUNTDOWN",
          f"Dialogue: 0,{t(1.4)},{t(11.0)},Sub,,0,0,0,,{{\\fad(800,800)\\pos({cx},{cy + 70})}}“പത്തു മണിയൊച്ച”",
          f"Dialogue: 0,{t(2.2)},{t(11.0)},Credit,,0,0,0,,{{\\fad(800,800)\\pos({cx},{cy + 150})}}ഔദ്യോഗിക ലിറിക് വീഡിയോ · Official Lyric Video",
          f"Dialogue: 0,{t(DUR - 6.5)},{t(DUR)},Title,,0,0,0,,{{\\fad(800,600)\\pos({cx},{cy - 60})}}COUNTDOWN",
          f"Dialogue: 0,{t(DUR - 6.0)},{t(DUR)},Sub,,0,0,0,,{{\\fad(800,600)\\pos({cx},{cy + 70})}}മലയാളം ഹൊറർ സീരീസ് · 10 എപ്പിസോഡുകൾ"]
    for i, (a, txt) in enumerate(lines):
        b = lines[i + 1][0] - .15 if i + 1 < len(lines) else a + 6
        b = min(b, a + 7.5)
        ev.append(f"Dialogue: 1,{t(a)},{t(b)},Ml,,0,0,0,,{{\\fad(220,280)}}{txt}")
        if MEAN.get(txt):
            ev.append(f"Dialogue: 1,{t(a + .1)},{t(b)},En,,0,0,0,,{{\\fad(300,280)}}{MEAN[txt]}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def main(vertical=False):
    os.makedirs(OUT, exist_ok=True)
    lines = json.load(open(os.path.join(HERE, "lyric_times.json"), encoding="utf-8"))
    lines = [(float(a), txt) for a, txt in lines]
    imgs = {p: cv2.imread(os.path.join(PANELS, p + ".jpg")) for _, p, _, _ in SHOTS}
    assert all(v is not None for v in imgs.values()), "render HD panels first"
    sub = os.path.join(OUT, "lyrics.ass"); ass(sub, lines, vertical)
    name = "COUNTDOWN_title_song_lyric_video_ml" + ("_9x16" if vertical else "") + ".mp4"
    out = os.path.join(OUT, name)
    ow, oh = (1080, 1920) if vertical else (W, H)
    vf = (f"[0:v]split[p][q];[p]scale=-2:1920,crop=1080:1920,gblur=sigma=38,eq=brightness=-0.2:saturation=0.7[bg];"
          f"[q]scale=1440:810,crop=1080:810[fg];[bg][fg]overlay=0:380,ass='{sub}':fontsdir={os.path.join(HERE, 'fonts')}[v]") if vertical \
        else f"[0:v]ass='{sub}':fontsdir={os.path.join(HERE, 'fonts')}[v]"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", SONG, "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "256k", "-t", str(DUR), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    starts = [s[0] for s in SHOTS] + [DUR]
    for fr in range(int(DUR * FPS)):
        t = fr / FPS
        i = max(j for j in range(len(SHOTS)) if SHOTS[j][0] <= t)
        a, pid, move, fx = SHOTS[i]
        k = (t - a) / (starts[i + 1] - a)
        z, cx, cy = camera(move, k)
        M = np.array([[z, 0, W / 2 - z * W * cx], [0, z, H / 2 - z * H * cy]], np.float32)
        img = cv2.warpAffine(imgs[pid], M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # soft cross-dissolve into the next shot
        if i + 1 < len(SHOTS) and starts[i + 1] - t < .5:
            n = SHOTS[i + 1]; z2, cx2, cy2 = camera(n[2], 0)
            M2 = np.array([[z2, 0, W / 2 - z2 * W * cx2], [0, z2, H / 2 - z2 * H * cy2]], np.float32)
            w = (starts[i + 1] - t) / .5
            img = cv2.addWeighted(img, w, cv2.warpAffine(imgs[n[1]], M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), 1 - w, 0)
        img = look(img, t, fr, fx)
        dip = min(1.0, t / 1.2, (DUR - t) / 1.5)
        if t < 11.0: dip = min(dip, .55)                               # title over the intro
        if t > DUR - 6.5: dip = min(dip, .5)
        if dip < 1: img = (img * max(0, dip)).astype(np.uint8)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(sub)
    print("wrote", os.path.relpath(out, V))


if __name__ == "__main__":
    main(vertical="--vertical" in sys.argv)
