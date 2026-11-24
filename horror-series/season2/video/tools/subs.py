"""English subtitles for the Hindi and Tamil versions of COUNTDOWN Season 2 (burned in at the bottom)."""
import os, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); S2 = os.path.dirname(os.path.dirname(HERE))
EN = {
 "e01_clara_hook": "Forty.", "e01_clara_warn": "Put your headphones on...", "e01_aadi_wake": "Amma...?",
 "e01_aadi_count1": "One... two... three...", "e01_aadi_count2": "Twelve... twenty... it isn't stopping...", "e01_aadi_count3": "Thirty-nine... forty.",
 "e01_clara_line": "This time it isn't ten, Aadi.",
 "e02_meera_1": "That isn't my heartbeat.", "e02_aadi_vn": "Chechi... the clock in my room struck forty times.", "e02_clara_1": "Tick... tick... Meera.",
 "e03_aadi_1": "Amma...?", "e03_thomas_1": "Thirty-nine.", "e03_mother_1": "Thirty-eight.",
 "e04_arjun_1": "Who... who's there?", "e04_refl_1": "I'm the one who sent you back. Now I have to go back.",
 "e05_ammachi_1": "In 1946, they didn't lock just one person in that tower.", "e05_meera_1": "Then who else, Ammachi?", "e05_ammachi_2": "She is still counting, child.",
 "e06_aadi_1": "Don't blink... don't blink...", "e06_clara_1": "Blink, Aadi.",
 "e07_neha_1": "You didn't defeat him. You were feeding him.", "e07_meera_1": "But I wound the clock back...", "e07_neha_2": "Every turn gave her one more year.",
 "e08_aadi_1": "Chechi... the ticking is here too.", "e08_meera_1": "This is... the second tower.", "e08_aadi_2": "Chechi... those are our names.",
 "e09_meera_1": "Backwards... just one more turn...", "e09_arjun_1": "Stop, Meera! Every turn takes someone!", "e09_clara_1": "Turn it... turn it...",
 "e10_ammachi_1": "In 1986 I hid. This time I'll go, in their place.", "e10_ammachi_2": "Take me.", "e10_meera_1": "Ammachi!",
 "e11_arjun_1": "Meera... my heart is her clock now.", "e11_arjun_2": "Stop me. She hears through me.", "e11_meera_1": "No... I won't let you go.",
 "e12_meera_1": "Sleep, Aadi... sleep...", "e12_clara_1": "This isn't a lullaby... it's a call...", "e12_meera_2": "Every time we sang it... we were calling her.",
 "e13_meera_1": "Everything has stopped... only us.", "e13_aadi_1": "Chechi, the rain is going up!", "e13_clara_1": "Three...",
 "e14_meera_1": "What's your name?", "e14_clara_1": "No one ever asked.", "e14_clara_2": "If no one remembers me... everyone has to stay with me.",
 "e15_clara_1": "Elias's daughter... Clara.", "e15_meera_1": "Clara. Now we will remember.", "e15_clara_2": "Thank you...", "e15_aadi_1": "Chechi, look... it's past three!",
}
EP01 = [(0.9, "e01_clara_hook"), (3.7, "e01_clara_warn"), (19.6, "e01_aadi_wake"), (36.5, "e01_aadi_count1"), (47.4, "e01_aadi_count2"),
        (61.2, "e01_aadi_count3"), (73.4, "e01_clara_line")]


@functools.lru_cache(None)
def dur(lang, key):
    p = os.path.join(S2, "audio", f"voice_{lang}", key + ".mp3")
    try: return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    except Exception: return 2.5


def cues(n, lang):
    if n == 1: items = EP01
    else:
        from eps import EPS
        items = [(v[0], v[1]) for v in EPS[n].get("voice", [])]
    return [(t, t + max(1.6, dur(lang, k)) + .3, EN[k]) for t, k in items if k in EN]


@functools.lru_cache(None)
def _img(text):
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 46)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = d.textbbox((0, 0), text, font=font, stroke_width=4)[2] + 20
    im = Image.new("RGBA", (w, 80), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.text((10, 10), text, font=font, fill=(236, 228, 210, 255), stroke_width=4, stroke_fill=(5, 5, 8, 255))
    a = np.asarray(im).astype(np.float32) / 255
    return a[..., [2, 1, 0]], a[..., 3:4]


def burn(fr, t, cue_list):
    for t0, t1, text in cue_list:
        if t0 <= t < t1:
            rgb, al = _img(text); k = min(1, (t - t0) / .15, (t1 - t) / .15)
            h, w = rgb.shape[:2]; x = (fr.shape[1] - w) // 2; y = fr.shape[0] - 150
            if x < 0: continue
            reg = fr[y:y + h, x:x + w]; fr[y:y + h, x:x + w] = reg * (1 - al * k) + rgb * al * k
    return fr
