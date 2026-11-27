"""COUNTDOWN promo v2 (~1:40, 9:16) cut to the FULL title song: hummed intro, verse 1, chorus 1, then a crossfade to
verse 3, the final chorus and the outro ("മൂന്നു മണിക്കവൻ വരുമല്ലോ... ഇന്ന്") over the title card.
Song cut points sit in the song's own gaps (measured + Whisper-aligned): A = 11.3 → 64.0 s (end of chorus 1), B = 138.6 → end (verse 3).
Usage: python3 make_promo_full.py
"""
import math, os, subprocess
import numpy as np
import cv2
from make_promo import frame_of, look, ease, W, H, FPS, SW, SH, PANELS, HS, HERE, OUT

A0, A1, B0 = 11.3, 64.0, 138.6
SONG = os.path.join(HS, "audio", "songs", "ten-little-chimes-FULL-ml.mp3")
FONT = "Noto Sans Malayalam"                                     # text font (Hindi: Noto Sans Devanagari)
TITLE2, INFO, CTA = "കൗണ്ട്ഡൗൺ", "10 എപ്പിസോഡുകൾ · ഉടൻ വരുന്നു", "Follow ചെയ്യൂ · ഓരോ രാത്രിയും ഒരു മണി കുറയും"
OUTNAME = "COUNTDOWN_promo_fullsong_ml"
XF = 0.4
B_LEN = 179.17 - B0
DUR = round((A1 - A0) + B_LEN - XF, 2)                       # ≈ 92.9 s
TT = 88.7                                                     # title card

SHOTS = [  # (start, end, panel, focus x, focus y, move, fx) in promo time
    (0.0, 3.0, "e01_p02", .50, .50, "push", ""), (3.0, 6.4, "e01_p12", .50, .45, "rise", ""), (6.4, 9.9, "e01_p04", .20, .55, "push", ""),
    # verse 1
    (9.9, 12.6, "e01_p11", .51, .50, "push", ""), (12.6, 15.6, "e01_p10", .34, .50, "push", ""), (15.6, 18.4, "e01_p14", .58, .50, "stinger", ""),
    (18.4, 21.4, "e02_p11", .50, .56, "push", ""), (21.4, 24.4, "e03_p07", .52, .40, "push", "vhs"), (24.4, 26.8, "e03_p06", .50, .45, "push", ""),
    (26.8, 29.3, "e04_p08", .52, .50, "push", "sepia"),
    # chorus 1
    (29.3, 32.2, "e05_p08", .50, .55, "push", "phone"), (32.2, 35.0, "e05_p11", .50, .35, "stinger", "phone"), (35.0, 37.8, "e06_p10", .50, .45, "push", ""),
    (37.8, 40.6, "e07_p06", .74, .45, "push", ""), (40.6, 43.4, "e07_p12", .50, .55, "push", ""), (43.4, 46.4, "e08_p03", .50, .55, "push", ""),
    (46.4, 49.4, "e08_p13", .62, .45, "rise", ""), (49.4, 52.3, "e09_p04", .45, .50, "drift", ""),
    # verse 3
    (52.3, 56.9, "e09_p10", .50, .45, "push", ""), (56.9, 61.0, "e09_p12", .62, .50, "stinger", ""), (61.0, 64.7, "e10_p07", .47, .55, "push", ""),
    # final chorus
    (64.7, 68.8, "e10_p05", .50, .42, "push", ""), (68.8, 72.0, "e10_p09", .62, .45, "stinger", ""), (72.0, 76.3, "e10_p10", .60, .45, "push", ""),
    (76.3, 80.7, "e10_p11", .55, .60, "drift", ""), (80.7, 84.8, "e10_p12", .50, .55, "push", ""), (84.8, TT, "e10_p13", .30, .45, "push", ""),
    (TT, DUR, "e01_p02", .50, .50, "title", ""),
]
LINES = [
    (2.8, 6.2, "മഞ്ഞുമലയിലെ ഗോപുരം\\Nനാൽപതു വർഷമായി നിശ്ശബ്ദമായിരുന്നു."),
    (6.5, 9.7, "ഒരു രാത്രി, പുലർച്ചെ 3 മണിക്ക്...\\Nഅത് പത്തു തവണ മുഴങ്ങി."),
    (12.8, 15.4, "മീര മാത്രം അത് കേട്ടു."),
    (18.6, 24.2, "ഓരോ രാത്രിയും ഒരു മണി കുറയും.\\Nഓരോ രാത്രിയും ഒരാൾ അപ്രത്യക്ഷമാകും."),
    (24.6, 27.0, "ആരും അവരെ ഓർക്കില്ല."),
    (35.2, 40.4, "അവൻ ഒരിക്കലും ഓടില്ല...\\Nപക്ഷേ എപ്പോഴും കൂടുതൽ അടുത്തായിരിക്കും."),
    (46.6, 52.0, "എണ്ണം പൂജ്യമാകുമ്പോൾ\\Nകേട്ടവരെല്ലാം അവന്റേത്."),
    (61.2, 64.5, "അവസാന മണിക്ക് മുമ്പ്...\\Nമീര അത് പിന്നോട്ട് ചുറ്റണം."),
    (84.9, 88.5, "നാൽപതു വർഷം കഴിയുമ്പോൾ...\\Nഅത് വീണ്ടും ഉണരും."),
]
HITS = [(0.0, 1.0), (15.6, .7), (32.2, .6), (56.9, .7), (68.8, .7), (TT, 1.0)]


def ass(path):
    t = lambda s: f"0:{int(s // 60):02d}:{s % 60:05.2f}"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Line,{FONT},60,&H00F0F4F6,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,4,3,2,70,70,330,1
Style: Title,Permanent Marker,150,&H00D0E2E9,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,8,0,1,0,8,5,40,40,0,1
Style: TitleMl,{FONT},78,&H00C9D2DA,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,4,5,40,40,0,1
Style: Info,{FONT},52,&H003A3AD3,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,3,5,40,40,0,1
Style: Cta,{FONT},46,&H00D8E8FF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,3,2,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{t(a)},{t(b)},Line,,0,0,0,,{{\\fad(250,300)}}{x}" for a, b, x in LINES]
    ev += [f"Dialogue: 0,{t(TT + .4)},{t(DUR)},Title,,0,0,0,,{{\\fad(400,0)\\pos(540,1420)}}COUNTDOWN",
           f"Dialogue: 0,{t(TT + .9)},{t(DUR)},TitleMl,,0,0,0,,{{\\fad(400,0)\\pos(540,1560)}}{TITLE2}",
           f"Dialogue: 0,{t(TT + 1.5)},{t(DUR)},Info,,0,0,0,,{{\\fad(400,0)\\pos(540,1690)}}{INFO}",
           f"Dialogue: 0,{t(TT + 2.1)},{t(DUR)},Cta,,0,0,0,,{{\\fad(400,0)\\pos(540,1790)}}{CTA}"]
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    imgs = {s[2]: cv2.imread(os.path.join(PANELS, s[2] + ".jpg")) for s in SHOTS}
    assert all(v is not None for v in imgs.values()), "render HD panels first"
    sub = os.path.join(OUT, "promo_full.ass"); ass(sub)
    bell = os.path.join(HS, "audio", "sfx", "chime_tower_bell.wav")
    out = os.path.join(OUT, OUTNAME + ".mp4")
    fc = (f"[0:v]ass='{sub}':fontsdir={os.path.join(HERE, 'fonts')}[v];"
          f"[1:a]atrim={A0}:{A1},asetpts=PTS-STARTPTS,afade=t=in:d=0.3[sa];"
          f"[1:a]atrim={B0},asetpts=PTS-STARTPTS,afade=t=out:st={B_LEN - 1.5:.2f}:d=1.5[sb];"
          f"[sa][sb]acrossfade=d={XF}:c1=tri:c2=tri[s];"
          f"[2:a]volume=0.8,asplit=2[b1][b2];[b2]adelay={int(TT*1000)}|{int(TT*1000)}[b2d];"
          f"[s][b1][b2d]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", SONG, "-i", bell, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "25", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", str(DUR), "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(DUR * FPS)):
        t = fr / FPS
        a, b, pid, fx_, fy_, move, fx = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1])
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
        img = look(frame_of(imgs[pid], fx_, fy_, z, dx + sx, dy + sy), t, fr, fx, flash)
        dip = min(1.0, t / .8)
        if move == "title": dip = min(dip, .5)
        elif b - t < .12: dip = min(dip, .35 + (b - t) / .12 * .65)
        if t > DUR - .8: dip = min(dip, (DUR - t) / .8)
        if dip < 1: img = (img * max(0, dip)).astype(np.uint8)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "17.0", "-i", out, "-frames:v", "1", "-q:v", "3", os.path.join(OUT, OUTNAME.replace("_ml", "").replace("_hi", "") + ("_hi" if OUTNAME.endswith("_hi") else "") + "_cover.jpg")], check=True)
    os.remove(sub)
    print("wrote", os.path.relpath(out, os.path.dirname(OUT)), DUR, "s")


if __name__ == "__main__":
    main()
