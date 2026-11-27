"""Season 2 gap teaser (Malayalam, 9:16, no on-screen text) for the 2-8 Dec gap.

Cuts 11 shots from S2 Ep1-8 (no late-season spoilers) and builds a fresh sound bed:
drone + ticking + heartbeat + bell, with the characters' own whispered Malayalam lines.
Usage: python3 make_gap_teaser.py [ml|hi|ta] [OUT]
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = sys.argv[1] if len(sys.argv) > 1 else 'ml'
V = os.path.join(ROOT, 'video', 'vertical_clean', 'COUNTDOWN_S2_ep{:02d}_' + LANG + '_9x16.mp4')
A = os.path.join(ROOT, 'audio')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'video', 'vertical_clean', f'COUNTDOWN_S2_gap_teaser_{LANG}_9x16.mp4')
# per-language start-time overrides where a line runs longer (Hindi first line is 5.7 s)
SHIFT = {'hi': {'e03_thomas_1': 8.1, 'e03_mother_1': 10.6}}

# (episode, start seconds, length) — chosen by eye from 3 s thumbnail grids
SHOTS = [
    (1, 74.0, 2.0),   # girl appears behind Aadi (cold-open scare)
    (1, 33.0, 2.5),   # city at night, every window a clock
    (6, 36.0, 2.5),   # Aadi among clock-faced people
    (3, 33.0, 2.5),   # watchers in the doorways
    (3, 66.0, 2.0),   # mother with blank white eyes
    (5, 36.0, 2.0),   # shadow crowd pointing at the tower
    (7, 45.0, 2.5),   # drowned girl dripping in the bedroom
    (7, 70.0, 2.0),   # hand rising from the bathtub
    (2, 58.0, 2.0),   # phone at 3:00, voice note
    (6, 58.0, 1.5),   # Aadi screaming, tears
    (8, 66.0, 3.0),   # tower clock circled by names
]
TAIL = 3.0  # black ending for the final whisper

# (file, start time in teaser, volume)
CUES = [
    ('sfx_el/impact_hit.mp3', 0.0, 1.0),
    ('voice_LL/e02_aadi_vn.mp3', 2.3, 1.6),     # "Chechi... the clock in my room struck forty."
    ('voice_LL/e03_thomas_1.mp3', 7.3, 1.6),    # "Thirty-nine."
    ('voice_LL/e03_mother_1.mp3', 9.7, 1.6),    # "Thirty-eight."
    ('sfx_el/rev_whisper.mp3', 11.5, 0.6),
    ('voice_LL/e02_clara_1.mp3', 13.8, 1.7),    # "Tick... tick... Meera."
    ('sfx_el/water_drip.mp3', 16.0, 0.7),
    ('sfx_el/static_glitch.mp3', 18.0, 0.7),
    ('sfx_el/scream_far.mp3', 20.0, 0.6),
    ('sfx_el/heartbeat.mp3', 19.5, 0.9),
    ('sfx_el/clock_gears.mp3', 21.5, 0.7),
    ('sfx_el/bell_toll.mp3', 24.5, 1.0),
    ('voice_LL/e06_clara_1.mp3', 25.6, 1.8),    # "Blink, Aadi."
]


def main():
    total = sum(s[2] for s in SHOTS) + TAIL
    cmd = ['ffmpeg', '-v', 'error', '-y']
    for ep, ss, d in SHOTS:
        cmd += ['-ss', str(ss), '-t', str(d), '-i', V.format(ep)]
    n = len(SHOTS)
    cmd += ['-stream_loop', '-1', '-i', os.path.join(A, 'sfx_el/drone_dark.mp3')]
    cmd += ['-stream_loop', '-1', '-i', os.path.join(A, 'sfx_el/tick_loop.mp3')]
    cues = []
    for f, t, vol in CUES:
        f = f.replace('voice_LL', 'voice_' + LANG)
        key = os.path.splitext(os.path.basename(f))[0]
        cues.append((f, SHIFT.get(LANG, {}).get(key, t), vol))
    for f, _, _ in cues:
        cmd += ['-i', os.path.join(A, f)]

    fc = []
    for i in range(n):
        fc.append(f'[{i}:v]setpts=PTS-STARTPTS,fps=24,format=yuv420p[v{i}]')
    fc.append(f'color=black:s=1080x1920:r=24:d={TAIL},format=yuv420p[vt]')
    fc.append(''.join(f'[v{i}]' for i in range(n)) + f'[vt]concat=n={n + 1}:v=1:a=0[vcat]')
    fc.append(f'[vcat]fade=t=in:st=0:d=0.15,format=yuv420p[v]')

    drone, tick = n, n + 1
    fc.append(f'[{drone}:a]atrim=0:{total},asetpts=PTS-STARTPTS,volume=0.55,'
              f'afade=t=in:d=1.5,afade=t=out:st={total - 1.5}:d=1.5[dr]')
    fc.append(f'[{tick}:a]atrim=0:22.5,asetpts=PTS-STARTPTS,volume=0.45,'
              f'afade=t=in:d=1,afade=t=out:st=21.8:d=0.7,adelay=2000|2000[tk]')
    mix = ['[dr]', '[tk]']
    for k, (_, t, vol) in enumerate(cues):
        ms = int(t * 1000)
        fc.append(f'[{n + 2 + k}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[c{k}]')
        mix.append(f'[c{k}]')
    fc.append(''.join(mix) + f'amix=inputs={len(mix)}:normalize=0:duration=longest,'
              f'atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]')

    cmd += ['-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]', '-t', str(total),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-profile:v', 'high', '-level', '4.0', '-maxrate', '7000k', '-bufsize', '14000k',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-threads', '4', OUT]
    subprocess.run(cmd, check=True)
    print(OUT, f'{total:.1f}s')


if __name__ == '__main__':
    main()
