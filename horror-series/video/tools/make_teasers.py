"""~30 s vertical teasers for Instagram Reels / YouTube Shorts, cut from the cinematic episodes.

Hook first: each teaser opens on the episode's scariest moment with a big Malayalam hook line, then the key beats
(best dialogue + chimes), then the cracking countdown number with a follow prompt. 1080x1920, subtitles burned in.
Usage: python3 make_teasers.py [episodes...]
"""
import os, subprocess, sys
from make_reels import TITLES, ass_time, srt_events, BAND_W, BAND_H, BAND_Y, HERE, V

OUT = os.path.join(V, "teasers")
# (start, end) cuts from each 1:30 cinematic episode, in teaser order. The first is the hook, the last the end card.
CUTS = {
    1: [(75.0, 79.0), (12.0, 15.0), (24.0, 28.0), (38.3, 44.5), (52.0, 56.5), (82.0, 90.0)],
    2: [(74.5, 78.5), (13.0, 17.0), (18.0, 23.0), (24.0, 29.5), (52.5, 57.5), (83.0, 90.0)],
    3: [(77.5, 81.5), (31.0, 37.0), (40.5, 45.5), (47.0, 51.5), (58.5, 63.0), (83.0, 90.0)],
    4: [(76.0, 81.0), (17.5, 20.0), (28.3, 34.0), (40.3, 46.0), (57.0, 62.0), (84.5, 90.0)],
    5: [(55.0, 59.0), (0.0, 5.0), (28.0, 33.0), (46.5, 52.5), (74.5, 79.5), (85.0, 90.0)],
    6: [(75.5, 80.0), (12.0, 17.0), (27.5, 31.0), (34.0, 38.0), (55.0, 60.0), (63.0, 67.0), (85.5, 90.0)],
    7: [(76.5, 80.0), (12.0, 16.0), (33.0, 38.0), (44.0, 46.0), (49.0, 54.5), (62.0, 66.0), (85.5, 90.0)],
    8: [(77.0, 82.0), (13.0, 16.0), (19.0, 21.0), (37.5, 44.0), (48.2, 51.5), (58.5, 64.5), (86.0, 90.0)],
    9: [(70.0, 75.0), (1.0, 7.5), (20.0, 24.0), (37.5, 42.7), (58.0, 60.0), (63.0, 67.0), (85.0, 89.0)],
    10: [(52.0, 57.0), (18.0, 23.0), (26.0, 31.5), (37.0, 41.0), (72.0, 75.0), (79.0, 82.5), (85.5, 90.0)],
}
HOOK = {
    1: "പുലർച്ചെ 3 മണിക്ക് ഈ മണിയൊച്ച\\Nകേട്ടാൽ... തിരിഞ്ഞുനോക്കരുത്.",
    2: "ഇന്നലെ വരെ അവൻ ഇവിടെയുണ്ടായിരുന്നു.\\Nആർക്കും ഓർമയില്ല.",
    3: "കണ്ണാടിയിൽ ആരോ എഴുതി:\\N“എണ്ണരുത്.”",
    4: "1986-ൽ അമ്മച്ചി ഒളിച്ചു.\\Nപകരം അവൻ കൊണ്ടുപോയത്...",
    5: "ഞങ്ങൾ ആ ഗോപുരം റെക്കോർഡ് ചെയ്തു.\\Nഇതാണ് കിട്ടിയത്.",
    6: "ഓരോ ക്ലോക്കിലും ഓരോ പേര്.\\Nഅതിൽ എന്റെ പേരും.",
    7: "കണ്ണാടിയിലെ ഞാൻ...\\Nഅര സെക്കൻഡ് വൈകി.",
    8: "ഇന്നലെ വരെ അമ്മച്ചി ഉണ്ടായിരുന്നു.\\Nഇന്ന് ആർക്കും ഓർമയില്ല.",
    9: "ഗോപുരത്തിനുള്ളിൽ...\\Nഅവർ ജീവനോടെയുണ്ട്.",
    10: "അവസാന മണി.\\Nഇനി ഒന്ന് മാത്രം.",
}
CTA = {**{ep: "അടുത്ത മണിയൊച്ച നാളെ  ·  Follow ചെയ്യൂ" for ep in range(1, 10)}, 10: "സീസൺ 2 ഉടൻ  ·  Follow ചെയ്യൂ"}


def make_ass(ep, path, cuts):
    total = sum(b - a for a, b in cuts)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Permanent Marker,104,&H00D0E2E9,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,6,0,1,0,6,8,40,40,170,1
Style: Ep,Noto Sans Malayalam,46,&H00C9C9C9,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,3,8,40,40,320,1
Style: Hook,Noto Sans Malayalam,64,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,5,3,8,50,50,{BAND_Y + BAND_H + 90},1
Style: Sub,Noto Sans Malayalam,50,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,4,2,8,60,60,{BAND_Y + BAND_H + 70},1
Style: Cta,Noto Sans Malayalam,50,&H00D8E8FF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,4,2,8,60,60,{BAND_Y + BAND_H + 260},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hook_end = cuts[0][1] - cuts[0][0]
    ev = [f"Dialogue: 0,0:00:00.00,{ass_time(total)},Title,,0,0,0,,COUNTDOWN",
          f"Dialogue: 0,0:00:00.00,{ass_time(total)},Ep,,0,0,0,,എപ്പിസോഡ് {ep} · {TITLES[ep]}",
          f"Dialogue: 2,0:00:00.00,{ass_time(hook_end)},Hook,,0,0,0,,{{\\fad(150,250)}}{HOOK[ep]}",
          f"Dialogue: 2,{ass_time(total - 4.0)},{ass_time(total)},Cta,,0,0,0,,{{\\fad(300,0)}}{CTA[ep]}"]
    # subtitles, remapped from episode time onto the teaser timeline (not during the hook text)
    subs = srt_events(os.path.join(V, "subs", f"COUNTDOWN_ep{ep:02d}_ml.srt"))
    off = 0.0
    for k, (a, b) in enumerate(cuts):
        for s0, s1, t in subs:
            x0, x1 = max(a, s0), min(b, s1)
            if x1 - x0 < .5 or k == 0:
                continue
            who, _, line = t.partition(": ")
            ev.append(f"Dialogue: 1,{ass_time(off + x0 - a)},{ass_time(off + x1 - a)},Sub,,0,0,0,,{{\\c&H8FB8E8&}}{who}{{\\c&HFFFFFF&}}\\N{line}")
        off += b - a
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
    return total


def build(ep):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(V, f"COUNTDOWN_ep{ep:02d}_cinematic_ml.mp4")
    cuts = CUTS[ep]
    ass = os.path.join(OUT, f"ep{ep:02d}.ass")
    total = make_ass(ep, ass, cuts)
    parts, labels = [], []
    for i, (a, b) in enumerate(cuts):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.06,afade=t=out:st={d - 0.08:.2f}:d=0.08[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    fc = ("".join(parts) + "".join(labels) + f"concat=n={len(cuts)}:v=1:a=1[cv][ca];"
          f"[cv]crop=1920:960:0:60,split[p][q];"
          f"[p]scale=-2:1920,crop=1080:1920,gblur=sigma=38,eq=brightness=-0.18:saturation=0.7[bg];"
          f"[q]scale={BAND_W}:{BAND_H},crop=1080:{BAND_H}[fg];"
          f"[bg][fg]overlay=0:{BAND_Y},ass='{ass}':fontsdir={os.path.join(HERE, 'fonts')}[v];"
          f"[ca]loudnorm=I=-14:TP=-1.5[a]")
    out = os.path.join(OUT, f"COUNTDOWN_ep{ep:02d}_teaser_ml.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-r", "24",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", out, "-frames:v", "1", "-q:v", "3",
                    os.path.join(OUT, f"COUNTDOWN_ep{ep:02d}_teaser_cover.jpg")], check=True)
    os.remove(ass)
    print(f"wrote teasers/COUNTDOWN_ep{ep:02d}_teaser_ml.mp4  ({total:.1f} s)")


if __name__ == "__main__":
    for ep in ([int(a) for a in sys.argv[1:]] or range(1, 11)):
        build(ep)
