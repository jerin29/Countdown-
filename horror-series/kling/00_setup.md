# COUNTDOWN — Realistic version with Kling AI: setup

This pack turns the storyboard into a photorealistic film like your reference reel. **118 Kling shots** across 10 episodes; the 21 title cards, end cards and text screens are made by Claude.

## Workflow (per shot)

1. **Make the characters once** (below) and save each as a Kling **Element** (or keep the image to upload as a reference). This keeps faces identical in every shot.
2. **Start frame:** Kling *Image* → paste the shot's **① image prompt**, attach the shot's characters as references, aspect **9:16**. Pick the best of the 4 results.
3. **Video:** Kling *Video → Image to Video* → upload that start frame, paste the **② video prompt**, duration as listed (5 s or 10 s), **Professional mode**, paste the negative prompt below.
4. **Sound off:** download the clip without Kling audio; our Malayalam voices, music and effects are already mixed to time.
5. **Name the file with its Shot ID** (`E01_S04.mp4`) and put all clips in one folder. Send them to me: I cut each to its exact length, add the title cards, text screens, film look and subtitles, and lay it over the soundtrack.

Shots that are 10 s on screen but feel long in one clip: generate 5 s and use Kling **Extend**, or use a 10 s clip.
For 16:9 (YouTube) instead of Reels: change `vertical 9:16 composition` to `widescreen 16:9 composition` in the image prompts and set the aspect ratio to 16:9.

## Negative prompt (use on every shot)

```
cartoon, anime, 3D render, illustration, painting, text, letters, subtitles, watermark, logo, extra fingers, deformed hands, distorted face, face morphing, flicker, blurry, oversaturated, bright cheerful colours, low quality
```

## Character & place references (make these first)

Generate each as a **character sheet**, then crop a clean front portrait and a full-body image to use as references.

### Meera  ·  element tag `MEERA`
```
Character reference sheet of Meera, a 16-year-old Indian Malayali girl, slim, warm brown skin, tired dark eyes with dark circles under them, messy shoulder-length black hair, an oversized maroon hoodie with the sleeves over her hands, dark jeans, a large vintage silver wristwatch loose on her left wrist. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### Arjun  ·  element tag `ARJUN`
```
Character reference sheet of Arjun, a 16-year-old Indian Malayali boy, tall and lanky, warm brown skin, round thin wire-frame glasses, short neat black hair, a mustard-yellow jacket over a grey school sweater vest and white shirt, khaki trousers, a smartphone in his hand. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### Ammachi (Rosa)  ·  element tag `AMMACHI`
```
Character reference sheet of Ammachi (Rosa), a 72-year-old Malayali Christian grandmother, deep wrinkles, kind but haunted eyes, white hair in a small bun, thick round glasses, a plain white Kerala cotton saree, a wooden rosary, an old brass pocket watch hanging on a chain around her neck. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### Neha  ·  element tag `NEHA`
```
Character reference sheet of Neha, the ghost of a 15-year-old Indian schoolgirl from 1986, pale blue pinafore school uniform over a white blouse, two long black braids tied with blue ribbons, pallid grey-blue skin, her eyes hidden in deep shadow, hair and clothes soaking wet and dripping, faint VHS glitch distortion. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### The Keeper  ·  element tag `KEEPER`
```
Character reference sheet of The Keeper, an impossibly tall, very thin figure over 7 feet tall in a long black Victorian tailcoat with brass buttons; instead of a head he has an antique cracked white clock face with no hands, rimmed in tarnished brass; his long fingers are brass skeleton keys; a faint sickly green glow around the clock face. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### Elias Varkey (1946)  ·  element tag `ELIAS`
```
Character reference sheet of Elias Varkey (1946), a gentle 60-year-old Malayali clockmaker in 1946, grey hair and a grey moustache, round spectacles, a white shirt with rolled sleeves and a brown leather apron. Three views side by side: front view, three-quarter view and full-body view, neutral pose, plain grey studio background, soft even light, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture.
```

### the Varkey clock tower  ·  element tag `TOWER`
```
Establishing shot of a tall black stone colonial-era clock tower with a pointed slate roof and a large cracked white clock face with no hands, standing in the old market square of a misty Kerala hill town surrounded by tea estates, at night in thick fog, moonlight, photorealistic cinematic horror film still, shot on ARRI Alexa with an anamorphic lens, shallow depth of field, low-key moody lighting, cold desaturated teal-grey colour grade, volumetric fog, subtle film grain, Kerala India, ultra-detailed, realistic skin texture, vertical 9:16 composition.
```

## Tips for the scary look

- Keep motion **slow**: horror comes from stillness. If a clip moves too much, regenerate with `very slow, almost still` added.
- The Keeper must **never run**. If he walks too fast, add `moves extremely slowly, stiff and unnatural`.
- Neha's glitch is added in editing too, so a clean clip of her is fine.
- If Kling adds random text or letters, regenerate; I'll add all real text (phone screens, name plates) in editing.
- Faces drifting between shots? Re-attach the character Element and lower creativity / raise the reference strength.

## Files

- `ep01.md` … `ep10.md`: every shot with its prompts, in order.
- `shots.csv`: the same in one spreadsheet (ID, timecode, duration, characters, prompts), for tracking what's done.