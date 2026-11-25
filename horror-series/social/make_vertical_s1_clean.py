"""Season 1 Ep6-10 vertical 9:16 WITHOUT text overlay, with the 2.5 s cold-open hook.
Usage: python3 make_vertical_s1_clean.py   (prints idx<TAB>path<TAB>size per file)"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); S1 = os.path.dirname(HERE)
OUT = os.path.join(S1, 'video', 'vertical_clean'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE); import add_hook
SRC = {'ml': 'COUNTDOWN_ep{:02d}_cinematic_ml.mp4', 'hi': 'hi/COUNTDOWN_ep{:02d}_cinematic_hi.mp4', 'ta': 'ta/COUNTDOWN_ep{:02d}_cinematic_ta.mp4'}
HOOK = {6: 63.5, 7: 45.0, 8: 18.5, 9: 75.5, 10: 51.0}
FC = ('[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.18[bg];'
      '[b]crop=1440:1080:240:0,scale=1080:810[fg];[bg][fg]overlay=0:555,format=yuv420p[v]')
i = 0
for L in ('ml', 'hi', 'ta'):
    for n in range(6, 11):
        src = os.path.join(S1, 'video', SRC[L].format(n)); base = os.path.join(OUT, f'COUNTDOWN_S1_ep{n:02d}_{L}_9x16.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', FC, '-map', '[v]', '-map', '0:a', '-threads', '4',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '7000k', '-bufsize', '14000k', '-r', '24',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', base], check=True)
        out = base.replace('.mp4', '_hook.mp4'); add_hook.make(base, out, HOOK[n])
        print(f'{i}\t{out}\t{os.path.getsize(out)}', flush=True); i += 1
