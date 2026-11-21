"""Cut one sung line of the theme song per episode end card. Edit START (seconds into the song) to re-pick a line.
Keys are the countdown number (10 = Episode 1 ... 1 = Episode 10)."""
import os, subprocess
A = os.path.join(os.path.dirname(__file__), "..")
START = {10: 12.70, 9: 18.05, 8: 24.70, 7: 36.05, 6: 42.05, 5: 48.05, 4: 53.95, 3: 59.90, 2: 81.05, 1: 87.05}
os.makedirs(os.path.join(A, "bgm", "endcards"), exist_ok=True)
for n, s in START.items():
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s - 0.15:.2f}", "-t", "4.8",
                    "-i", os.path.join(A, "songs", "ten-little-chimes-ml.mp3"),
                    "-af", "afade=t=in:d=0.1,afade=t=out:st=3.8:d=1.0", "-ar", "48000", "-ac", "2",
                    os.path.join(A, "bgm", "endcards", f"endcard_hum_{n:02d}.wav")], check=True)
