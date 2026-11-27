"""Apply per-character voice treatments to the raw voice lines (Malayalam: voice/, Hindi: voice_hi/).
Usage: python3 process_voices.py [ml|hi]
raw/*.mp3 -> processed/*.wav (48 kHz mono, loudness-normalized)."""
import os, subprocess, glob, sys
LANG = sys.argv[1] if len(sys.argv) > 1 else "ml"          # ml (Malayalam) or hi (Hindi)
ROOT = os.path.join(os.path.dirname(__file__), "..", "voice" if LANG == "ml" else f"voice_{LANG}")
RAW, OUT = os.path.join(ROOT, "raw"), os.path.join(ROOT, "processed")
os.makedirs(OUT, exist_ok=True)

# Lead-in silence trim so lines start on the first syllable.
TRIM = "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02"
NORM = "loudnorm=I=-18:TP=-2:LRA=11"
ROOM = "aecho=0.8:0.5:35|61:0.18|0.10"  # small bedroom-sized room

FX = {
    "meera":      f"{TRIM},highpass=f=90,{ROOM},{NORM}",
    "arjun":      f"{TRIM},highpass=f=80,{ROOM},{NORM}",
    "mom":        f"{TRIM},highpass=f=150,lowpass=f=5000,aecho=0.8:0.6:80|140:0.3|0.2,volume=0.7,{NORM}",
    "teacher":    f"{TRIM},highpass=f=200,lowpass=f=6000,aecho=0.8:0.7:90|170:0.35|0.25,{NORM}",
    "ammachi":    f"{TRIM},rubberband=pitch=0.9:tempo=0.93,highpass=f=80,lowpass=f=7000,{ROOM},{NORM}",
    # Neha: ghost on a dying radio/cassette: band-limited, wobble, crushed, long echo
    "neha":       f"{TRIM},rubberband=pitch=0.97:tempo=0.9,highpass=f=400,lowpass=f=3200,vibrato=f=5.5:d=0.25,"
                  f"acrusher=bits=10:mix=0.4,aecho=0.8:0.7:260|520:0.35|0.2,{NORM}",
    # Ep7: Meera's own voice on the phone, slowed and wrong
    "meeravoice": f"{TRIM},rubberband=pitch=0.75:tempo=0.7,highpass=f=350,lowpass=f=3400,"
                  f"acrusher=bits=8:mix=0.3,aecho=0.8:0.6:400:0.4,{NORM}",
    # Ep7: the reflection whispering, slightly too low, close and dry then a cold tail
    "reflection": f"{TRIM},rubberband=pitch=0.85:tempo=0.85,highpass=f=200,aphaser=type=t:speed=0.3,"
                  f"aecho=0.8:0.8:700:0.35,{NORM}",
    # Ammachi as a fading memory (Ep8)
    "ammachiecho":f"{TRIM},rubberband=pitch=0.9:tempo=0.85,highpass=f=250,lowpass=f=4500,"
                  f"aecho=0.8:0.85:300|600|900:0.45|0.3|0.2,{NORM}",
    "elias":      f"{TRIM},rubberband=pitch=0.82:tempo=0.8,highpass=f=70,lowpass=f=6500,aecho=0.8:0.8:500:0.3,{NORM}",
}
# Arjun lines in Ep5 are heard through his phone camera mic.
PHONE = f"{TRIM},highpass=f=300,lowpass=f=4000,acompressor=threshold=-20dB:ratio=6,{ROOM},{NORM}"

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def keeper(src, dst):
    """Three layered voices pitched down (low, old, child-ish octave above, faint), slowed, in a stone tower."""
    graph = (
        f"[0:a]{TRIM},asplit=3[a][b][c];"
        "[a]rubberband=pitch=0.5:tempo=0.75,volume=1.0[l1];"
        "[b]rubberband=pitch=0.71:tempo=0.75,volume=0.7[l2];"
        "[c]rubberband=pitch=1.26:tempo=0.75,highpass=f=1500,volume=0.18[l3];"
        "[l1][l2][l3]amix=inputs=3:normalize=0,lowpass=f=7000,"
        f"aecho=0.8:0.85:120|260|480:0.4|0.3|0.2,{NORM}"
    )
    run(["ffmpeg", "-y", "-i", src, "-filter_complex", graph, "-ar", "48000", "-ac", "1", dst])

for src in sorted(glob.glob(os.path.join(RAW, "*.mp3"))):
    name = os.path.splitext(os.path.basename(src))[0]
    ep, who = name.split("_")[0], name.split("_")[1]
    dst = os.path.join(OUT, name + ".wav")
    if who == "keeper":
        keeper(src, dst); continue
    if name == "e08_ammachi_03":
        who = "ammachiecho"
    fx = PHONE if (who == "arjun" and ep == "e05") else FX[who]
    run(["ffmpeg", "-y", "-i", src, "-af", fx, "-ar", "48000", "-ac", "1", dst])
    print("done", name)
