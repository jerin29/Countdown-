"""ElevenLabs helpers for COUNTDOWN Season 2 (the API key is injected by the session proxy).
tts(voice_id, text, out, lang) -> mp3 ; sfx(prompt, out, seconds) -> mp3 ; credits() -> used/limit"""
import json, subprocess, sys
API = "https://api.elevenlabs.io"
def _post(path, body, out):
    r = subprocess.run(["curl", "-sS", "-X", "POST", API + path, "-H", "Content-Type: application/json",
                        "-d", json.dumps(body), "-o", out, "-w", "%{http_code}"], capture_output=True, text=True)
    if r.stdout != "200":
        print("FAILED", path, r.stdout, open(out, errors="ignore").read()[:300], file=sys.stderr); return False
    return True
def tts(voice, text, out, lang="ml", model="eleven_v3", stability=0.4):
    return _post(f"/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                 {"text": text, "model_id": model, "language_code": lang, "voice_settings": {"stability": stability}}, out)
def sfx(prompt, out, seconds=None, influence=0.5):
    body = {"text": prompt, "prompt_influence": influence}
    if seconds: body["duration_seconds"] = seconds
    return _post("/v1/sound-generation?output_format=mp3_44100_128", body, out)
def credits():
    r = subprocess.run(["curl", "-sS", API + "/v1/user/subscription"], capture_output=True, text=True)
    d = json.loads(r.stdout); return d["character_count"], d["character_limit"]
