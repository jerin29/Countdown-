"""ElevenLabs music for One Reply (key injected by the session proxy). Usage: python3 music.py PLAN.json OUT.mp3"""
import json, subprocess, sys
plan, out = sys.argv[1], sys.argv[2]
body = {"composition_plan": json.load(open(plan)), "model_id": "music_v1"}
r = subprocess.run(["curl", "-sS", "-X", "POST", "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_192",
                    "-H", "Content-Type: application/json", "-d", json.dumps(body), "-o", out, "-w", "%{http_code}"],
                   capture_output=True, text=True)
print(r.stdout, r.stderr[:300])
if r.stdout != "200": print(open(out, errors="ignore").read()[:600])
