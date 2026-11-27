"""Build the COUNTDOWN Kling prompt pack from shots.py + the panel timecodes.
Writes kling/00_setup.md, kling/epNN.md and kling/shots.csv.  Usage: python3 build_kling.py"""
import csv, json, os
from shots import SHOTS

HERE = os.path.dirname(os.path.abspath(__file__))
KL = os.path.abspath(os.path.join(HERE, ".."))
HS = os.path.abspath(os.path.join(KL, ".."))
idx = json.load(open(os.path.join(HS, "art", "storyboard", "panels", "index.json"), encoding="utf-8"))

STYLE = ("photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, "
         "low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, "
         "ultra-detailed, realistic skin texture")
MOTION_STYLE = "cinematic, realistic, subtle natural motion, consistent face and costume, no morphing, no text"
NEG = ("cartoon, anime, 3D render, illustration, painting, text, letters, subtitles, watermark, logo, extra fingers, deformed hands, "
       "distorted face, face morphing, flicker, blurry, oversaturated, bright cheerful colours, low quality")

CHAR = {
 'MEERA': ("Meera", "a 16-year-old Indian Malayali girl, slim, warm brown skin, tired dark eyes with dark circles under them, messy shoulder-length black hair, "
           "an oversized maroon hoodie with the sleeves over her hands, dark jeans, a large vintage silver wristwatch loose on her left wrist"),
 'ARJUN': ("Arjun", "a 16-year-old Indian Malayali boy, tall and lanky, warm brown skin, round thin wire-frame glasses, short neat black hair, "
           "a mustard-yellow jacket over a grey school sweater vest and white shirt, khaki trousers, a smartphone in his hand"),
 'AMMACHI': ("Ammachi (Rosa)", "a 72-year-old Malayali Christian grandmother, deep wrinkles, kind but haunted eyes, white hair in a small bun, thick round glasses, "
             "a plain white Kerala cotton saree, a wooden rosary, an old brass pocket watch hanging on a chain around her neck"),
 'NEHA': ("Neha", "the ghost of a 15-year-old Indian schoolgirl from 1986, pale blue pinafore school uniform over a white blouse, two long black braids tied with blue ribbons, "
          "pallid grey-blue skin, her eyes hidden in deep shadow, hair and clothes soaking wet and dripping, faint VHS glitch distortion"),
 'KEEPER': ("The Keeper", "an impossibly tall, very thin figure over 7 feet tall in a long black Victorian tailcoat with brass buttons; instead of a head he has an antique cracked "
            "white clock face with no hands, rimmed in tarnished brass; his long fingers are brass skeleton keys; a faint sickly green glow around the clock face"),
 'ELIAS': ("Elias Varkey (1946)", "a gentle 60-year-old Malayali clockmaker in 1946, grey hair and a grey moustache, round spectacles, a white shirt with rolled sleeves and a brown leather apron"),
 'TOWER': ("the Varkey clock tower", "a tall black stone colonial-era clock tower with a pointed slate roof and a large cracked white clock face with no hands, "
           "standing in the old market square of a misty Kerala hill town surrounded by tea estates"),
}

def tsec(tc):
    m, s = tc.split(":"); return int(m) * 60 + int(s)

def sub(text):
    text = text.replace("the [TOWER]", "the Varkey clock tower").replace("[TOWER]", "the Varkey clock tower")
    for k, (name, _) in CHAR.items():
        text = text.replace(f"[{k}]", name)
    return text

rows = []
for ep in range(1, 11):
    pan = [p for p in idx if p["ep"] == ep]
    shots = SHOTS[ep]
    assert len(pan) == len(shots), (ep, len(pan), len(shots))
    starts = [tsec(p["tc"]) for p in pan] + [90]
    for i, (p, s) in enumerate(zip(pan, shots)):
        length = starts[i + 1] - starts[i]
        sid = f"E{ep:02d}_S{i + 1:02d}"
        if s[0] == 'CLAUDE':
            rows.append(dict(id=sid, ep=ep, tc=p["tc"], length=length, kling="", chars="", image="", video="", note="Claude makes this: " + s[1], panel=p["file"]))
            continue
        chars, frame, motion = s
        cdesc = "; ".join(f"{CHAR[c][0][0].upper() + CHAR[c][0][1:]} is {CHAR[c][1]}" for c in chars if c in CHAR)
        image = f"{sub(frame)}. {cdesc + '. ' if cdesc else ''}{STYLE}, vertical 9:16 composition."
        video = f"{sub(motion)}. {MOTION_STYLE}."
        rows.append(dict(id=sid, ep=ep, tc=p["tc"], length=length, kling="5s" if length <= 5.5 else "10s",
                         chars=", ".join(CHAR[c][0] for c in chars), image=image, video=video, note="", panel=p["file"]))

with open(os.path.join(KL, "shots.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

TITLES = {1: "പത്തു മണിയൊച്ച", 2: "ഒഴിഞ്ഞ ബെഞ്ച്", 3: "കണ്ണാടിയിലെ പെൺകുട്ടി", 4: "അമ്മച്ചിയുടെ കഥ", 5: "റെക്കോർഡിംഗ്",
          6: "വർക്കി & സൺസ്", 7: "നഷ്ടപ്പെട്ട സമയം", 8: "ആടുന്ന കസേര", 9: "ഗോപുരത്തിനുള്ളിൽ", 10: "അവസാന മണിയൊച്ച"}
for ep in range(1, 11):
    R = [r for r in rows if r["ep"] == ep]
    k = [r for r in R if r["kling"]]
    out = [f"# COUNTDOWN · Episode {ep}: “{TITLES[ep]}” ({11 - ep}) — Kling prompts\n",
           f"{len(k)} Kling shots · aspect **9:16** · negative prompt for every shot: see `00_setup.md` · save each clip as the **Shot ID** (e.g. `{k[0]['id']}.mp4`).\n",
           f"Storyboard for this episode: `art/storyboard/panels/e{ep:02d}_p*.jpg` (use them as composition guides).\n"]
    for r in R:
        out.append(f"\n---\n\n## {r['id']} · {r['tc']} · {r['length']} s on screen")
        if r["note"]:
            out.append(f"\n> 🎬 {r['note']} — nothing to generate.\n")
            continue
        out.append(f"\n**Kling duration:** {r['kling']} · **Attach elements:** {r['chars'] or '—'} · **Storyboard:** `{r['panel']}`\n")
        out.append(f"\n**① Start frame (image prompt)**\n```\n{r['image']}\n```\n")
        out.append(f"\n**② Video (image-to-video prompt)**\n```\n{r['video']}\n```\n")
    open(os.path.join(KL, f"ep{ep:02d}.md"), "w", encoding="utf-8").write("\n".join(out))

# ---------- setup guide ----------
s = ["# COUNTDOWN — Realistic version with Kling AI: setup\n",
     "This pack turns the storyboard into a photorealistic film like your reference reel. **"
     f"{sum(1 for r in rows if r['kling'])} Kling shots** across 10 episodes; the {sum(1 for r in rows if not r['kling'])} title cards, end cards and text screens are made by Claude.\n",
     "## Workflow (per shot)\n",
     "1. **Make the characters once** (below) and save each as a Kling **Element** (or keep the image to upload as a reference). This keeps faces identical in every shot.",
     "2. **Start frame:** Kling *Image* → paste the shot's **① image prompt**, attach the shot's characters as references, aspect **9:16**. Pick the best of the 4 results.",
     "3. **Video:** Kling *Video → Image to Video* → upload that start frame, paste the **② video prompt**, duration as listed (5 s or 10 s), **Professional mode**, paste the negative prompt below.",
     "4. **Sound off:** download the clip without Kling audio; our Malayalam voices, music and effects are already mixed to time.",
     "5. **Name the file with its Shot ID** (`E01_S04.mp4`) and put all clips in one folder. Send them to me: I cut each to its exact length, add the title cards, text screens, film look and subtitles, and lay it over the soundtrack.",
     "",
     "Shots that are 10 s on screen but feel long in one clip: generate 5 s and use Kling **Extend**, or use a 10 s clip.",
     "For 16:9 (YouTube) instead of Reels: change `vertical 9:16 composition` to `widescreen 16:9 composition` in the image prompts and set the aspect ratio to 16:9.\n",
     "## Negative prompt (use on every shot)\n", f"```\n{NEG}\n```\n",
     "## Character & place references (make these first)\n",
     "Generate each as a **character sheet**, then crop a clean front portrait and a full-body image to use as references.\n"]
for k, (name, desc) in CHAR.items():
    kind = "location" if k == "TOWER" else "character"
    if kind == "character":
        p = (f"Character reference sheet of {name}, {desc}. Three views side by side: front view, three-quarter view and full-body view, neutral pose, "
             f"plain grey studio background, soft even light, {STYLE}.")
    else:
        p = f"Establishing shot of {desc}, at night in thick fog, moonlight, {STYLE}, vertical 9:16 composition."
    s.append(f"### {name}  ·  element tag `{k}`\n```\n{p}\n```\n")
s.append("## Tips for the scary look\n")
s += ["- Keep motion **slow**: horror comes from stillness. If a clip moves too much, regenerate with `very slow, almost still` added.",
      "- The Keeper must **never run**. If he walks too fast, add `moves extremely slowly, stiff and unnatural`.",
      "- Neha's glitch is added in editing too, so a clean clip of her is fine.",
      "- If Kling adds random text or letters, regenerate; I'll add all real text (phone screens, name plates) in editing.",
      "- Faces drifting between shots? Re-attach the character Element and lower creativity / raise the reference strength.\n",
      "## Files\n",
      "- `ep01.md` … `ep10.md`: every shot with its prompts, in order.",
      "- `shots.csv`: the same in one spreadsheet (ID, timecode, duration, characters, prompts), for tracking what's done."]
open(os.path.join(KL, "00_setup.md"), "w", encoding="utf-8").write("\n".join(s))
print(len(rows), "shots;", sum(1 for r in rows if r["kling"]), "for Kling")
