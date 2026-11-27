"""Vertical 9:16 versions of the 48 Season 2 posts WITHOUT any text overlay (user preference).
Centre 4:3 of the 16:9 frame shown large, blurred copy behind. Ep1 also gets the 2.5 s cold-open hook (at 72.3 s).
Usage: python3 make_vertical_clean.py [index ...]   (indices into captions.json; default all)"""
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); S2 = os.path.dirname(HERE)
OUT = os.path.join(S2, 'video', 'vertical_clean'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(os.path.dirname(S2), 'social'))
import add_hook


def make(p):
    src = os.path.join(S2, p['file'])
    out = os.path.join(OUT, os.path.basename(src).replace('.mp4', '_9x16.mp4'))
    fc = ('[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.18[bg];'
          '[b]crop=1440:1080:240:0,scale=1080:810[fg];[bg][fg]overlay=0:555,format=yuv420p[v]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[v]', '-map', '0:a', '-threads', '4',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '7000k', '-bufsize', '14000k', '-r', '24',
                    '-c:a', 'copy', '-movflags', '+faststart', out], check=True)
    if p['kind'] == 'episode' and p['ep'] == 1:
        hooked = out.replace('.mp4', '_hook.mp4'); add_hook.make(out, hooked, 72.3); out = hooked
    print(f"{p['_i']}\t{out}\t{os.path.getsize(out)}", flush=True)


if __name__ == '__main__':
    P = json.load(open(os.path.join(HERE, 'captions.json')))
    for i, p in enumerate(P): p['_i'] = i
    idx = [int(a) for a in sys.argv[1:]] or range(len(P))
    for i in idx: make(P[i])
