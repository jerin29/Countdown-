"""Vertical 9:16 Instagram Reels versions of the COUNTDOWN cinematic episodes.

Layout (1080x1920): the film in a large centre band (the 2:1 picture, letterbox removed, scaled up and trimmed a little at
the sides), a blurred, darkened copy of the same shot filling the screen behind it, the series title + episode name at the
top, and Malayalam subtitles burned in under the picture (Reels can't show a subtitle track). Plus a cover image per episode.

Usage: python3 make_reels.py [episodes...]   (needs the 16:9 videos from make_animatic.py and the .srt files)
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(V, "reels")
TITLES = {1: "പത്തു മണിയൊച്ച", 2: "ഒഴിഞ്ഞ ബെഞ്ച്", 3: "കണ്ണാടിയിലെ പെൺകുട്ടി", 4: "അമ്മച്ചിയുടെ കഥ", 5: "റെക്കോർഡിംഗ്",
          6: "വർക്കി & സൺസ്", 7: "നഷ്ടപ്പെട്ട സമയം", 8: "ആടുന്ന കസേര", 9: "ഗോപുരത്തിനുള്ളിൽ", 10: "അവസാന മണിയൊച്ച"}
STINGER = {1: 77, 2: 76, 3: 79, 4: 79, 5: 76, 6: 77, 7: 79, 8: 80, 9: 78, 10: 55}   # cover frame time (s)
BAND_W, BAND_H = 1440, 720            # film scaled to this, then trimmed to 1080 wide
BAND_Y = 520                          # top of the picture band


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def srt_events(path):
    ev = []
    for block in open(path, encoding="utf-8").read().strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) < 3: continue
        a, b = lines[1].split(" --> ")
        sec = lambda s: (lambda h, m, rest: int(h) * 3600 + int(m) * 60 + float(rest.replace(",", ".")))(*s.split(":"))
        ev.append((sec(a), sec(b), " ".join(lines[2:])))
    return ev


def make_ass(ep, path):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Permanent Marker,104,&H00D0E2E9,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,6,0,1,0,6,8,40,40,170,1
Style: Ep,Noto Sans Malayalam,46,&H00C9C9C9,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,0,3,8,40,40,320,1
Style: Num,Noto Serif,90,&H003A3AB3,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,4,8,40,40,375,1
Style: Sub,Noto Sans Malayalam,50,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,4,2,8,60,60,{BAND_Y + BAND_H + 70},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    end = ass_time(90)
    ev = [f"Dialogue: 0,0:00:00.00,{end},Title,,0,0,0,,COUNTDOWN",
          f"Dialogue: 0,0:00:00.00,{end},Ep,,0,0,0,,എപ്പിസോഡ് {ep} · {TITLES[ep]}"]
    for a, b, t in srt_events(os.path.join(V, "subs", f"COUNTDOWN_ep{ep:02d}_ml.srt")):
        who, _, line = t.partition(": ")
        ev.append(f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Sub,,0,0,0,,{{\\c&H8FB8E8&}}{who}{{\\c&HFFFFFF&}}\\N{line}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def build(ep):
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(V, f"COUNTDOWN_ep{ep:02d}_cinematic_ml.mp4")
    ass = os.path.join(OUT, f"ep{ep:02d}.ass")
    make_ass(ep, ass)
    out = os.path.join(OUT, f"COUNTDOWN_ep{ep:02d}_reel_ml.mp4")
    fc = (f"[0:v]crop=1920:960:0:60,split[a][b];"
          f"[a]scale=-2:1920,crop=1080:1920,gblur=sigma=38,eq=brightness=-0.18:saturation=0.7[bg];"
          f"[b]scale={BAND_W}:{BAND_H},crop=1080:{BAND_H}[fg];"
          f"[bg][fg]overlay=0:{BAND_Y},drawbox=x=0:y={BAND_Y - 2}:w=1080:h=2:color=black@0.8:t=fill,"
          f"drawbox=x=0:y={BAND_Y + BAND_H}:w=1080:h=2:color=black@0.8:t=fill,"
          f"ass='{ass}':fontsdir={os.path.join(HERE, 'fonts')}[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
                    "-r", "24", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    cover = os.path.join(OUT, f"COUNTDOWN_ep{ep:02d}_cover.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(STINGER[ep]), "-i", out, "-frames:v", "1", "-q:v", "3", cover], check=True)
    os.remove(ass)
    print("wrote", os.path.relpath(out, V))


if __name__ == "__main__":
    for ep in ([int(a) for a in sys.argv[1:]] or range(1, 11)):
        build(ep)
