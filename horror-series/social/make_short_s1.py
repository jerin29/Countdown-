"""~40 s short cuts of Season 1 Ep6-10 (9:16, no text, opening scare kept).

Why: full 90 s reels were watched ~5 s on average (~5%), so Instagram stopped them at ~1K views.
Each short = opening scare + the episode's key scary beat + the cliffhanger and cracking end card.
Segment times are in the *_hook.mp4 timeline (script time + 2.5 s), picked from 2 s thumbnail grids.
Usage: python3 make_short_s1.py [ml|hi|ta] [EP ...]
"""
import os, subprocess, sys

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'video', 'vertical_clean')
SEGS = {
    6: [(0, 2.5), (29.5, 50.5), (70.5, 90.0)],                 # clocks are people -> Sam/Meera/Arjun clocks; run, phone stinger
    7: [(0, 2.5), (30.5, 57.5), (77.5, 90.0)],                 # late reflection, own voice on phone; reflection stinger
    8: [(0, 2.5), (39.5, 54.5), (60.5, 69.5), (79.5, 90.0)],   # "nobody lived here"; watch message; faces in the tower
    9: [(0, 2.5), (34.5, 46.5), (60.0, 90.0)],                 # faces in the gears; Arjun's sacrifice; Keeper points
    10: [(0, 2.5), (20.5, 40.0), (54.0, 62.0), (80.0, 92.5)],  # wind it back; Elias; boy wakes -> "40 / Season 2"
}
F = 0.08  # tiny audio fade at every cut so there are no clicks


def make(lang, ep):
    src = os.path.join(D, f'COUNTDOWN_S1_ep{ep:02d}_{lang}_9x16_hook.mp4')
    out = os.path.join(D, f'COUNTDOWN_S1_ep{ep:02d}_{lang}_9x16_short.mp4')
    segs = SEGS[ep]
    cmd = ['ffmpeg', '-v', 'error', '-y']
    for a, b in segs:
        cmd += ['-ss', str(a), '-t', f'{b - a:.3f}', '-i', src]
    fc, cat = [], ''
    for i, (a, b) in enumerate(segs):
        d = b - a
        fc.append(f'[{i}:v]setpts=PTS-STARTPTS,fps=24,format=yuv420p[v{i}]')
        fc.append(f'[{i}:a]asetpts=PTS-STARTPTS,aresample=48000,'
                  f'afade=t=in:d={F},afade=t=out:st={d - F:.3f}:d={F}[a{i}]')
        cat += f'[v{i}][a{i}]'
    total = sum(b - a for a, b in segs)
    fc.append(f'{cat}concat=n={len(segs)}:v=1:a=1[vc][ac]')
    fc.append(f'[vc]fade=t=out:st={total - 0.4:.3f}:d=0.4,format=yuv420p[v]')
    fc.append(f'[ac]afade=t=out:st={total - 0.4:.3f}:d=0.4[a]')
    cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-profile:v', 'high', '-level', '4.0', '-maxrate', '7000k', '-bufsize', '14000k',
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-threads', '4', out]
    subprocess.run(cmd, check=True)
    print(f'{out}\t{total:.1f}s', flush=True)


if __name__ == '__main__':
    lang = sys.argv[1] if len(sys.argv) > 1 else 'ml'
    eps = [int(e) for e in sys.argv[2:]] or sorted(SEGS)
    for ep in eps:
        make(lang, ep)
