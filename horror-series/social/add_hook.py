"""Prepend a 2.5 s 'cold open' hook (the loudest sudden scare in the episode) to a vertical video.
Usage: python3 add_hook.py IN.mp4 OUT.mp4 [--at SECONDS]   (prints the chosen time)"""
import sys, subprocess, numpy as np, librosa
HOOK = 2.5


def pick(path):
    sr = 22050
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype=np.float32)
    hop = 512; rms = librosa.feature.rms(y=y, hop_length=hop)[0]; t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    db = librosa.amplitude_to_db(rms + 1e-6)
    dur = len(y) / sr; best, bt = -1e9, 10.0
    fps = sr / hop
    for i in range(len(db)):
        s = t[i]
        if s < 8 or s > dur - 12: continue
        pre = db[max(0, i - int(1.5 * fps)):i].mean()
        win = db[i:i + int(1.2 * fps)]
        score = win.max() - pre + 0.15 * win.mean()   # sudden jump in loudness = scare
        if score > best: best, bt = score, s
    return max(0.0, bt - 0.4)   # start just before the hit


def make(src, out, at=None):
    at = pick(src) if at is None else at
    fc = (f"[0:v]setpts=PTS-STARTPTS,fade=t=out:st={HOOK - 0.12}:d=0.12:color=white[hv];"
          f"[0:a]asetpts=PTS-STARTPTS,afade=t=out:st={HOOK - 0.15}:d=0.15[ha];"
          f"[hv][ha][1:v][1:a]concat=n=2:v=1:a=1[vc][a];[vc]format=yuv420p[v]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(at), '-t', str(HOOK), '-i', src, '-i', src,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[a]', '-threads', '4',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '7000k', '-bufsize', '14000k', '-r', '24',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(f'{out}\thook_at={at:.2f}', flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]; at = float(a[a.index('--at') + 1]) if '--at' in a else None
    make(a[0], a[1], at)
