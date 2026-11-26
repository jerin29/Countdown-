"""ElevenLabs music from a single prompt. Usage: python3 music_prompt.py "PROMPT" SECONDS OUT.mp3"""
import json, subprocess, sys
prompt, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
body = {"prompt": prompt, "music_length_ms": int(secs * 1000), "model_id": "music_v1", "force_instrumental": True}
r = subprocess.run(["curl", "-sS", "-X", "POST", "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192",
                    "-H", "Content-Type: application/json", "-d", json.dumps(body), "-o", out, "-w", "%{http_code}"], capture_output=True, text=True)
print(r.stdout, r.stderr[:300])
if r.stdout != "200": print(open(out, errors="ignore").read()[:600])
